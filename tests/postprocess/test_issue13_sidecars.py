"""Issue #13 canonical run-result sidecar contract tests."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from importlib.metadata import metadata
from pathlib import Path
from types import SimpleNamespace

import pytest

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 compatibility
    import tomli as tomllib

from rompy.core import result_persistence
from rompy.core.responses import (
    Artifact,
    ArtifactType,
    ModelRunFailure,
    ModelRunSuccess,
    PostprocessSuccess,
    RemoteArtifact,
    TimingInfo,
)

from rompy_ww3.postprocess.persistence import (
    RUN_JSON,
    build_persisted,
    compute_artifact_checksums,
    load_persisted,
    write_persisted,
)
from rompy_ww3.postprocess.processor import WW3TransferPostprocessor

FIXTURES = Path(__file__).parents[1] / "fixtures" / "core_return_schema_v2"
CORE_SHA = "b43c11ae0fe0f24e25786117d30128812a188760"


def _declared_core_dependency(source_root: Path | None = None) -> str:
    """Read the exact project pin when source metadata is available."""
    source_root = source_root or Path(__file__).resolve().parents[2]
    pyproject = source_root / "pyproject.toml"
    source_package = source_root / "src" / "rompy_ww3"
    if pyproject.is_file() and source_package.is_dir():
        project = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        assert project.get("project", {}).get("name") == "rompy_ww3"
        dependencies = project["project"]["dependencies"]
    else:
        dependencies = metadata("rompy_ww3").get_all("Requires-Dist") or []
    return next(
        dependency for dependency in dependencies if dependency.startswith("rompy @ ")
    )


def test_core_dependency_fallback_reads_installed_metadata(tmp_path: Path) -> None:
    """Use installed metadata when no matching source tree is present."""
    assert _declared_core_dependency(tmp_path).endswith(f"@{CORE_SHA}")


def test_core_fixture_hashes_and_provenance_are_frozen() -> None:
    fixture_readme = (FIXTURES / "README.md").read_text()
    assert CORE_SHA in fixture_readme
    rompy_dependency = _declared_core_dependency()
    assert rompy_dependency.rsplit("@", 1)[1].split(" ", 1)[0] == CORE_SHA
    assert f"merge\n`{CORE_SHA}`" in fixture_readme
    expected = {
        "run_success.json": "9e64d49a896a9fa521daa2cb5d0067517b3b65da5eb380d04c5d72e584d1ce9f",
        "run_failure.json": "d1da8ea12df2c3a40ae00c2f41fc1f345a0d4b2292f12dbeb75c2652eb267643",
        "adversarial/legacy_v1.json": "3c43fa6af22b2244292f3366a2c31fc4b2997e049bd98493b215187f1500abd6",
        "adversarial/malformed.json": "6f5e7359678e8924994c6dbfb317d70fb6443042df93c6d531bef3aa73974ba9",
        "adversarial/unsupported_v99.json": "b3975b59c2922984132d9a7e8febb142abb6ef7b36640e1c8db382cbd18d8265",
        "adversarial/wrong_kind.json": "d13d994a831fe9c7b156a08bfa30c4e1bbd8db28aa7628490fc33396db830875",
    }
    for name, digest in expected.items():
        assert hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest() == digest


@pytest.mark.parametrize(
    ("name", "result_type"),
    [("run_success.json", ModelRunSuccess), ("run_failure.json", ModelRunFailure)],
)
def test_canonical_run_fixture_preserves_typed_payload(
    name: str, result_type: type
) -> None:
    sidecar = result_persistence.load_run_result(FIXTURES / name)
    loaded = load_persisted(FIXTURES / name)
    assert isinstance(sidecar.payload, result_type)
    assert isinstance(loaded, result_type)
    assert loaded.model_dump(mode="json") == sidecar.payload.model_dump(mode="json")
    assert loaded.artifacts
    assert loaded.expected_outputs
    assert loaded.missing_outputs
    assert (
        loaded.metadata["normalized_context"]["config_hash"] == "sha256:fixture-config"
    )


@pytest.mark.parametrize(
    "name",
    [
        "adversarial/malformed.json",
        "adversarial/legacy_v1.json",
        "adversarial/unsupported_v99.json",
        "adversarial/wrong_kind.json",
    ],
)
def test_invalid_and_legacy_documents_are_rejected_with_regeneration_guidance(
    name: str,
) -> None:
    with pytest.raises(
        (ValueError, json.JSONDecodeError),
        match="(?i)(invalid|unsupported|expected|regenerate|canonical)",
    ):
        load_persisted(FIXTURES / name)


@pytest.mark.parametrize("value", [{"success": True}, SimpleNamespace(success=True)])
def test_private_adapters_reject_arbitrary_result_values(value) -> None:
    with pytest.raises(TypeError, match="ModelRunSuccess or ModelRunFailure"):
        build_persisted(value)


def test_missing_and_envelope_mismatch_are_rejected_by_public_loader(
    tmp_path: Path,
) -> None:
    with pytest.raises(FileNotFoundError, match="run_result sidecar not found"):
        load_persisted(tmp_path)
    raw = json.loads((FIXTURES / "run_success.json").read_text())
    raw["run_id"] = "different-run"
    mismatch = tmp_path / RUN_JSON
    mismatch.write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="run_id mismatch"):
        load_persisted(mismatch)


def test_ww3_writes_only_core_envelope_and_never_former_flat_shape(
    tmp_path: Path,
) -> None:
    result = load_persisted(FIXTURES / "run_success.json")
    destination = write_persisted(build_persisted(result), tmp_path)
    assert destination == tmp_path / RUN_JSON
    raw = json.loads(destination.read_text())
    assert raw["kind"] == "run_result"
    assert raw["schema_version"] == 2
    assert raw["payload"] == result.model_dump(mode="json")
    assert "postprocess" not in raw
    assert "artifact_checksums" not in raw
    assert "config" not in raw


def _run_result(
    workspace: Path, artifacts: list, metadata: dict | None = None
) -> ModelRunSuccess:
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return ModelRunSuccess(
        success=True,
        run_id="nested-run",
        backend_used="local",
        output_dir=str(workspace / "output"),
        workspace_dir=str(workspace),
        artifacts=artifacts,
        expected_outputs=[],
        missing_outputs=[],
        timing=TimingInfo(start_time=start, end_time=start),
        metadata=metadata or {},
    )


def test_checksums_and_transfer_resolve_paths_from_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    (workspace / "one").mkdir(parents=True)
    (workspace / "two").mkdir()
    (workspace / "one" / "same.txt").write_text("one")
    (workspace / "two" / "same.txt").write_text("two")
    artifacts = [
        Artifact(path="one/same.txt", artifact_type=ArtifactType.TEXT),
        Artifact(path="two/same.txt", artifact_type=ArtifactType.TEXT),
    ]
    result = _run_result(workspace, artifacts)
    write_persisted(build_persisted(result), workspace)
    loaded = load_persisted(workspace)
    assert [artifact.path for artifact in loaded.artifacts] == [
        "one/same.txt",
        "two/same.txt",
    ]
    checksums = compute_artifact_checksums(loaded)
    assert checksums["one/same.txt"] != checksums["two/same.txt"]
    destination = tmp_path / "destination"
    transferred = WW3TransferPostprocessor().process(
        result, destinations=[f"file://{destination}"]
    )
    assert isinstance(transferred, PostprocessSuccess)
    assert transferred.metadata["transferred_count"] == 2
    assert set(transferred.metadata["name_map"]) == {
        str(workspace / "one" / "same.txt"),
        str(workspace / "two" / "same.txt"),
    }


def test_remote_and_mixed_observed_evidence_survives_transfer_result(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "local.txt").write_text("local")
    remote = RemoteArtifact(
        uri="s3://bucket/run/remote.txt", artifact_type=ArtifactType.TEXT
    )
    local = Artifact(path="local.txt", artifact_type=ArtifactType.TEXT)
    result = _run_result(workspace, [local, remote])
    mixed = WW3TransferPostprocessor().process(
        result, destinations=[f"file://{tmp_path / 'destination'}"]
    )
    assert mixed.metadata["transferred_count"] == 1
    remote_evidence = [artifact for artifact in mixed.artifacts if artifact.kind == "remote"]
    assert remote_evidence[0].uri == "s3://bucket/run/remote.txt"
    remote_only = _run_result(workspace, [remote])
    empty = WW3TransferPostprocessor().process(
        remote_only, destinations=[f"file://{tmp_path / 'destination2'}"]
    )
    assert empty.metadata["transferred_count"] == 0
    assert any(artifact.kind == "remote" for artifact in empty.artifacts)


def test_fresh_process_loads_same_typed_model_run_result(tmp_path: Path) -> None:
    script = """
from pathlib import Path
from rompy_ww3.postprocess.persistence import load_persisted
from rompy.core.responses import ModelRunFailure, ModelRunSuccess
result = load_persisted(Path(__import__('sys').argv[1]))
assert isinstance(result, (ModelRunSuccess, ModelRunFailure))
print(result.__class__.__name__)
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(Path(__file__).parents[2] / "src"), *sys.path]
    )
    completed = subprocess.run(
        [sys.executable, "-c", script, str(FIXTURES / "run_success.json")],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    assert completed.stdout.strip() == "ModelRunSuccess"
