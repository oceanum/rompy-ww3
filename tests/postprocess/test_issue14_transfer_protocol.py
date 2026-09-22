"""Issue #14 canonical WW3 transfer protocol tests."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
from rompy.core import result_persistence
from rompy.core.responses import (
    Artifact,
    ArtifactType,
    ModelRunFailure,
    ModelRunSuccess,
    PostprocessFailure,
    PostprocessSuccess,
    RemoteArtifact,
    TimingInfo,
)
from rompy.transfer.manager import TransferBatchResult, TransferItemResult
from typer.testing import CliRunner

from rompy_ww3.cli import app
from rompy_ww3.postprocess.lifecycle import run_transfer_postprocess
from rompy_ww3.postprocess.persistence import (
    build_persisted,
    load_postprocess,
    write_persisted,
)
from rompy_ww3.postprocess.processor import WW3TransferPostprocessor


def _run(root: Path, artifacts, *, success: bool = True):
    timing = TimingInfo(
        start_time=datetime(2024, 1, 1, tzinfo=timezone.utc),
        end_time=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    common = {
        "run_id": "issue14",
        "backend_used": "local",
        "output_dir": str(root),
        "workspace_dir": str(root),
        "artifacts": artifacts,
        "expected_outputs": [],
        "missing_outputs": [],
        "timing": timing,
    }
    if success:
        return ModelRunSuccess(**common)
    return ModelRunFailure(error="model failed", **common)


def test_empty_and_mixed_evidence_are_canonical_and_persisted(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    remote = RemoteArtifact(uri="s3://bucket/remote.nc", artifact_type=ArtifactType.NETCDF)
    result = WW3TransferPostprocessor().process(
        _run(root, [remote]), [f"file://{tmp_path / 'destination'}"]
    )
    assert isinstance(result, PostprocessSuccess)
    assert result.metadata["requested_count"] == 0
    assert result.metadata["remote_count"] == 1
    assert result.metadata["skipped_count"] == 1
    assert load_postprocess(root).model_dump(mode="json") == result.model_dump(mode="json")


def test_all_local_success_preserves_names_checksums_and_counts(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    (root / "one.txt").write_text("one")
    (root / "two.txt").write_text("two")
    result = WW3TransferPostprocessor().process(
        _run(
            root,
            [
                Artifact(path="one.txt", artifact_type=ArtifactType.TEXT),
                Artifact(path="two.txt", artifact_type=ArtifactType.TEXT),
            ],
        ),
        [f"file://{tmp_path / 'destination'}"],
    )
    assert isinstance(result, PostprocessSuccess)
    assert result.metadata["requested_count"] == 2
    assert result.metadata["local_count"] == 2
    assert result.metadata["transferred_count"] == 2
    assert result.metadata["failed_count"] == 0
    assert result.metadata["source_checksums"]["one.txt"].startswith("sha256:")
    assert set(result.metadata["name_map"].values()) == {"one.txt", "two.txt"}


def test_missing_required_source_is_failure(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    required = Artifact(path="required.txt", artifact_type=ArtifactType.TEXT)
    result = WW3TransferPostprocessor().process(
        _run(root, [], success=True).model_copy(update={"expected_outputs": [required]}),
        [f"file://{tmp_path / 'destination'}"],
    )
    assert isinstance(result, PostprocessFailure)
    assert result.metadata["required_missing_count"] == 1
    assert result.metadata["transfer_failures"][0]["reason"] == "missing_required_source"


def _fake_batch(monkeypatch, batch):
    class FakeManager:
        def transfer_files(self, **kwargs):
            return batch

    monkeypatch.setattr("rompy_ww3.postprocess.processor.TransferManager", FakeManager)


def test_partial_transfer_returns_successful_artifacts_and_failures(tmp_path, monkeypatch):
    root = tmp_path / "run"
    root.mkdir()
    (root / "ok.txt").write_text("ok")
    (root / "bad.txt").write_text("bad")
    destination = "mock://destination"
    batch = TransferBatchResult(
        total=2,
        succeeded=1,
        failed=1,
        items=[
            TransferItemResult(root / "ok.txt", destination, "ok.txt", destination + "/ok.txt", True),
            TransferItemResult(root / "bad.txt", destination, "bad.txt", destination + "/bad.txt", False, "denied"),
        ],
    )
    _fake_batch(monkeypatch, batch)
    result = WW3TransferPostprocessor().process(
        _run(root, [Artifact(path="ok.txt"), Artifact(path="bad.txt")]), [destination]
    )
    assert isinstance(result, PostprocessFailure)
    assert [artifact.path for artifact in result.artifacts] == ["ok.txt"]
    assert result.metadata["failed_count"] == 1
    assert result.metadata["transfer_failures"][0]["error"] == "denied"


def test_wholly_failed_transfer_is_failure(tmp_path, monkeypatch):
    root = tmp_path / "run"
    root.mkdir()
    (root / "bad.txt").write_text("bad")
    destination = "mock://destination"
    _fake_batch(
        monkeypatch,
        TransferBatchResult(
            total=1,
            succeeded=0,
            failed=1,
            items=[
                TransferItemResult(root / "bad.txt", destination, "bad.txt", destination + "/bad.txt", False, "denied")
            ],
        ),
    )
    result = WW3TransferPostprocessor().process(
        _run(root, [Artifact(path="bad.txt")]), [destination]
    )
    assert isinstance(result, PostprocessFailure)
    assert result.success is False
    assert result.metadata["transferred_count"] == 0
    assert result.metadata["failed_count"] == 1


def test_missing_source_is_failure_with_structured_evidence(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    result = WW3TransferPostprocessor().process(
        _run(root, [Artifact(path="missing.txt", artifact_type=ArtifactType.TEXT)]),
        [f"file://{tmp_path / 'destination'}"],
    )
    assert isinstance(result, PostprocessFailure)
    assert result.metadata["failed_count"] == 1
    assert result.metadata["transfer_failures"][0]["reason"] == "missing_source"


def test_model_failure_never_becomes_transfer_success(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    result = WW3TransferPostprocessor().process(
        _run(root, [], success=False), [f"file://{tmp_path / 'destination'}"]
    )
    assert isinstance(result, PostprocessFailure)
    assert "model failed" in result.error


def test_arbitrary_inputs_and_outputs_are_rejected(tmp_path):
    processor = WW3TransferPostprocessor()
    with pytest.raises(TypeError, match="ModelRunSuccess or ModelRunFailure"):
        processor.process({"artifacts": []}, [f"file://{tmp_path / 'destination'}"])
    with pytest.raises(TypeError, match="PostprocessSuccess or PostprocessFailure"):
        from rompy_ww3.postprocess.persistence import require_postprocess

        require_postprocess({"success": True})


def test_persistence_failure_keeps_transfer_error(tmp_path, monkeypatch):
    root = tmp_path / "run"
    root.mkdir()
    (root / "missing.txt").unlink(missing_ok=True)
    monkeypatch.setattr(
        result_persistence,
        "write_postprocess_result",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("read-only")),
    )
    result = WW3TransferPostprocessor().process(
        _run(root, [Artifact(path="missing.txt", artifact_type=ArtifactType.TEXT)]),
        [f"file://{tmp_path / 'destination'}"],
    )
    assert isinstance(result, PostprocessFailure)
    assert "Transfer failed" in result.error
    assert result.persistence_diagnostic is not None
    assert result.persistence_diagnostic.primary_error == result.error


def test_fresh_subprocess_loads_and_executes_typed_transfer(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    (root / "field.txt").write_text("field")
    write_persisted(
        build_persisted(_run(root, [Artifact(path="field.txt")])), root
    )
    destination = tmp_path / "destination"
    script = """
from pathlib import Path
import sys
from rompy.core.responses import PostprocessSuccess
from rompy_ww3.postprocess.lifecycle import run_transfer_postprocess
result = run_transfer_postprocess(Path(sys.argv[1]), [sys.argv[2]])
assert isinstance(result, PostprocessSuccess)
print(result.__class__.__name__)
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(Path(__file__).parents[2] / "src"), *sys.path]
    )
    completed = subprocess.run(
        [sys.executable, "-c", script, str(root), f"file://{destination}"],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    assert completed.stdout.strip() == "PostprocessSuccess"
    assert isinstance(load_postprocess(root), PostprocessSuccess)


def test_cli_and_lifecycle_use_same_canonical_sidecar(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    (root / "field.txt").write_text("field")
    model_run = _run(root, [Artifact(path="field.txt", artifact_type=ArtifactType.TEXT)])
    write_persisted(build_persisted(model_run), root)
    destination = f"file://{tmp_path / 'destination'}"
    direct = run_transfer_postprocess(root, [destination])
    repeated = run_transfer_postprocess(root, [destination])
    assert repeated.metadata["skipped"] is True
    cli = CliRunner().invoke(app, ["postprocess", str(root), "-d", destination])
    assert cli.exit_code == 0
    assert isinstance(direct, PostprocessSuccess)
    persisted = load_postprocess(root)
    assert persisted.metadata["transferred_count"] == direct.metadata["transferred_count"]
    assert json.loads((root / "postprocess_result.json").read_text())["kind"] == "postprocess_result"
