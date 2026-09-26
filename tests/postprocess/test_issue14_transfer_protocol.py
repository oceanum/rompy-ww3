"""Public WW3/core transfer protocol coverage migrated from the v1 lifecycle API.

The WW3 adapter owns target naming.  Core owns transfer reconciliation, replay,
redaction, retries, and persistence.  These tests deliberately exercise the
public ModelRun, lifecycle, and CLI seams instead of removed WW3 internals.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

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
from rompy.model import ModelRun
from rompy.postprocess import transfer as core_transfer
from typer.testing import CliRunner

from rompy_ww3.cli import app
from rompy_ww3.postprocess.config import WW3TransferConfig
from rompy_ww3.postprocess.lifecycle import run_transfer_postprocess
from rompy_ww3.postprocess.persistence import (
    build_persisted,
    load_postprocess,
    write_persisted,
)

runner = CliRunner()


def _run(
    root: Path,
    artifacts: list[Artifact | RemoteArtifact],
    *,
    success: bool = True,
    run_id: str = "issue14",
    expected_outputs: list[Artifact] | None = None,
    metadata: dict | None = None,
):
    stamp = datetime(2024, 1, 1, tzinfo=timezone.utc)
    common = {
        "run_id": run_id,
        "backend_used": "local",
        "output_dir": str(root),
        "workspace_dir": str(root),
        "artifacts": artifacts,
        "expected_outputs": expected_outputs or [],
        "missing_outputs": [],
        "timing": TimingInfo(start_time=stamp, end_time=stamp),
        "metadata": metadata or {},
    }
    return (
        ModelRunSuccess(**common)
        if success
        else ModelRunFailure(error="model failed", **common)
    )


def _public_postprocess(
    root: Path,
    model_result,
    destinations: list[str],
    *,
    artifact_types: list[ArtifactType] | None = None,
    failure_policy: str = "CONTINUE",
    required_policy: str = "expected_outputs_required",
    naming_policy: str = "restart_only",
    max_retries: int = 0,
):
    """Use the public ModelRun adapter, retaining the canonical run result."""
    config = WW3TransferConfig(
        destinations=destinations,
        artifact_types=artifact_types,
        failure_policy=failure_policy,
        required_policy=required_policy,
        naming_policy=naming_policy,
        max_retries=max_retries,
    )
    model = ModelRun(run_id=model_result.run_id, output_dir=root, run_id_subdir=False)
    return model.postprocess(config, processor_input=model_result)


def _mock_backend(monkeypatch, action):
    """Patch the core registry seam with a deterministic test-only backend."""

    class Backend:
        def put(self, source_path, destination):
            return action(Path(source_path), destination)

    monkeypatch.setattr(core_transfer, "get_transfer", lambda _destination: Backend())


def _write_run(root: Path, result) -> None:
    root.mkdir(parents=True, exist_ok=True)
    write_persisted(build_persisted(result), root)


def _pairs(result):
    return result.metadata.get("transfer", {}).get("pairs", [])


def test_public_modelrun_path_delegates_ww3_naming_and_core_pairs(tmp_path):
    root = tmp_path / "outputs"
    root.mkdir()
    (root / "restart001.ww3").write_text("restart")
    (root / "field.nc").write_text("field")
    result = _public_postprocess(
        root,
        _run(
            root,
            [
                Artifact(path="restart001.ww3", artifact_type=ArtifactType.RESTART),
                Artifact(path="field.nc", artifact_type=ArtifactType.NETCDF),
            ],
            metadata={"ww3": {"restart_stride_seconds": 3600}},
        ),
        [f"file://{tmp_path / 'destination'}"],
    )

    assert isinstance(result, PostprocessSuccess)
    assert (tmp_path / "destination" / "20240101_000000_restart.ww3").read_text() == "restart"
    assert (tmp_path / "destination" / "field.nc").read_text() == "field"
    pairs = _pairs(result)
    assert {pair["status"] for pair in pairs} == {"succeeded"}
    assert {pair["destination"].rsplit("/", 1)[-1] for pair in pairs} == {
        "20240101_000000_restart.ww3",
        "field.nc",
    }
    persisted = result_persistence.load_postprocess_result(root).payload
    assert isinstance(persisted, PostprocessSuccess)
    assert persisted.metadata["transfer"]["pairs"] == pairs


def test_public_modelrun_filter_preserves_observed_evidence(tmp_path):
    root = tmp_path / "outputs"
    root.mkdir()
    (root / "restart.ww3").write_text("restart")
    (root / "field.nc").write_text("field")
    result = _public_postprocess(
        root,
        _run(
            root,
            [
                Artifact(path="restart.ww3", artifact_type=ArtifactType.RESTART),
                Artifact(path="field.nc", artifact_type=ArtifactType.NETCDF),
            ],
        ),
        [f"file://{tmp_path / 'destination'}"],
        artifact_types=[ArtifactType.NETCDF],
    )

    assert isinstance(result, PostprocessSuccess)
    assert (tmp_path / "destination" / "field.nc").is_file()
    assert not (tmp_path / "destination" / "restart.ww3").exists()
    assert {artifact.path for artifact in result.artifacts} == {"restart.ww3", "field.nc"}
    assert len(_pairs(result)) == 1


def test_public_lifecycle_reports_required_missing_and_persists_core_sidecar(tmp_path):
    root = tmp_path / "outputs"
    root.mkdir()
    observed = Artifact(path="observed.txt", artifact_type=ArtifactType.TEXT)
    missing = Artifact(path="required.txt", artifact_type=ArtifactType.TEXT)
    (root / observed.path).write_text("observed")
    run = _run(
        root,
        [observed],
        expected_outputs=[observed, missing],
    ).model_copy(update={"missing_outputs": [missing]})
    _write_run(root, run)

    result = run_transfer_postprocess(root, [f"file://{tmp_path / 'destination'}"])

    assert isinstance(result, PostprocessFailure)
    assert "required" in result.error
    assert result_persistence.load_postprocess_result(root).payload.error == result.error
    assert not (tmp_path / "destination" / observed.path).exists()


def test_public_modelrun_continue_accounts_for_failed_core_pairs(tmp_path, monkeypatch):
    root = tmp_path / "outputs"
    root.mkdir()
    for name in ("ok.txt", "bad.txt"):
        (root / name).write_text(name)

    def transfer(_source, destination):
        if destination.endswith("bad.txt"):
            raise RuntimeError("denied")

    _mock_backend(monkeypatch, transfer)
    result = _public_postprocess(
        root,
        _run(root, [Artifact(path="ok.txt"), Artifact(path="bad.txt")]),
        ["mock://destination"],
    )

    assert isinstance(result, PostprocessFailure)
    pairs = _pairs(result)
    statuses = {pair["source"]: pair["status"] for pair in pairs}
    assert statuses == {"local:ok.txt": "succeeded", "local:bad.txt": "failed"}
    assert next(pair for pair in pairs if pair["source"] == "local:bad.txt")["error"] == "denied"
    assert result.metadata["failed_count"] == 1
    assert result.metadata["transferred_count"] == 1


@pytest.mark.parametrize("failed_name", ["one.txt", "two.txt"])
def test_public_modelrun_fail_fast_marks_remaining_pairs_unattempted(
    tmp_path, monkeypatch, failed_name
):
    root = tmp_path / "outputs"
    root.mkdir()
    names = ["one.txt", "two.txt", "three.txt"]
    for name in names:
        (root / name).write_text(name)

    def transfer(_source, destination):
        if destination.endswith(failed_name):
            raise RuntimeError("denied")

    _mock_backend(monkeypatch, transfer)
    result = _public_postprocess(
        root,
        _run(root, [Artifact(path=name) for name in names]),
        ["mock://destination"],
        failure_policy="FAIL_FAST",
    )

    assert isinstance(result, PostprocessFailure)
    pairs = _pairs(result)
    assert sum(pair["status"] == "failed" for pair in pairs) == 1
    ordered_names = sorted(names)
    expected_unattempted = len(names) - ordered_names.index(failed_name) - 1
    assert sum(pair["status"] == "unattempted" for pair in pairs) == expected_unattempted
    assert all("error" not in pair for pair in pairs if pair["status"] == "unattempted")


def test_public_modelrun_retry_and_replay_use_core_state(tmp_path, monkeypatch):
    root = tmp_path / "outputs"
    root.mkdir()
    (root / "field.txt").write_text("field")
    calls = []

    def transfer(source, destination):
        calls.append((source, destination))
        if len(calls) == 1:
            raise RuntimeError("temporary")

    _mock_backend(monkeypatch, transfer)
    run = _run(root, [Artifact(path="field.txt")])
    first = _public_postprocess(root, run, ["mock://destination"], max_retries=1)
    second = _public_postprocess(root, run, ["mock://destination"], max_retries=1)

    assert isinstance(first, PostprocessSuccess)
    assert isinstance(second, PostprocessSuccess)
    assert len(calls) == 2
    assert _pairs(first)[0]["attempts"] == 2
    assert _pairs(second)[0]["status"] == "skipped"
    assert second.metadata["transfer"]["replayed_pairs"] == 1


def test_public_modelrun_replay_identity_changes_when_source_changes(tmp_path):
    root = tmp_path / "outputs"
    root.mkdir()
    (root / "field.txt").write_text("before")
    run = _run(root, [Artifact(path="field.txt")])
    first = _public_postprocess(root, run, [f"file://{tmp_path / 'destination'}"])
    (root / "field.txt").write_text("after")
    second = _public_postprocess(root, run, [f"file://{tmp_path / 'destination'}"])

    assert isinstance(first, PostprocessSuccess)
    assert isinstance(second, PostprocessSuccess)
    assert _pairs(first)[0]["replay_identity"] != _pairs(second)[0]["replay_identity"]
    assert (tmp_path / "destination" / "field.txt").read_text() == "after"


def test_public_pipeline_accepts_typed_model_failure_without_private_fallback(tmp_path):
    root = tmp_path / "outputs"
    root.mkdir()
    failed = _run(root, [], success=False, run_id="failed-run")
    _write_run(root, failed)

    result = run_transfer_postprocess(root, [f"file://{tmp_path / 'destination'}"])

    assert isinstance(result, PostprocessSuccess)
    assert result.success is True
    assert isinstance(load_postprocess(root), PostprocessSuccess)


def test_public_core_redacts_destination_and_backend_secrets(tmp_path, monkeypatch):
    root = tmp_path / "outputs"
    root.mkdir()
    (root / "field.txt").write_text("field")
    secret_destination = "mock://bucket/path?token=TOPSECRET"

    def transfer(_source, destination):
        raise RuntimeError(f"denied {destination} TOPSECRET")

    _mock_backend(monkeypatch, transfer)
    result = _public_postprocess(
        root, _run(root, [Artifact(path="field.txt")]), [secret_destination]
    )
    serialized = result.model_dump_json()
    sidecar = (root / "postprocess_result.json").read_text()

    assert isinstance(result, PostprocessFailure)
    assert "TOPSECRET" not in serialized + sidecar
    assert "token=" not in serialized + sidecar
    assert "mock://bucket/path/field.txt" in serialized


def test_public_core_preserves_remote_and_local_observed_evidence(tmp_path):
    root = tmp_path / "outputs"
    root.mkdir()
    (root / "local.txt").write_text("local")
    remote = RemoteArtifact(uri="s3://bucket/run/remote.txt", artifact_type=ArtifactType.TEXT)
    result = _public_postprocess(
        root,
        _run(root, [Artifact(path="local.txt"), remote]),
        [f"file://{tmp_path / 'destination'}"],
    )

    assert isinstance(result, PostprocessSuccess)
    assert result.metadata["transferred_count"] == 1
    assert any(artifact.kind == "remote" for artifact in result.artifacts)
    remote_only = _public_postprocess(
        root, _run(root, [remote]), [f"file://{tmp_path / 'destination2'}"]
    )
    assert isinstance(remote_only, PostprocessSuccess)
    assert remote_only.metadata["transferred_count"] == 0
    assert _pairs(remote_only) == []


def test_public_core_rejects_malformed_replay_state_without_reusing_success(
    tmp_path, monkeypatch
):
    root = tmp_path / "outputs"
    root.mkdir()
    (root / "field.txt").write_text("field")
    calls = []

    def transfer(source, destination):
        calls.append((source, destination))

    _mock_backend(monkeypatch, transfer)
    run = _run(root, [Artifact(path="field.txt")])
    first = _public_postprocess(root, run, ["mock://destination"])
    assert isinstance(first, PostprocessSuccess)
    state = root / ".rompy-postprocess" / "ww3-transfer" / "transfer-state.json"
    state.write_text("not json")
    retried = _public_postprocess(root, run, ["mock://destination"])

    assert isinstance(retried, PostprocessFailure)
    assert "invalid transfer replay state" in retried.error
    assert len(calls) == 1


def test_public_lifecycle_and_cli_use_canonical_postprocess_sidecar(tmp_path):
    root = tmp_path / "outputs"
    root.mkdir()
    (root / "field.txt").write_text("field")
    run = _run(root, [Artifact(path="field.txt")])
    _write_run(root, run)
    destination = f"file://{tmp_path / 'destination'}"

    direct = run_transfer_postprocess(root, [destination])
    direct_raw = json.loads((root / "postprocess_result.json").read_text())
    cli = runner.invoke(app, ["postprocess", str(root), "-d", destination])

    assert isinstance(direct, PostprocessSuccess)
    assert cli.exit_code == 0, cli.stdout
    assert json.loads((root / "postprocess_result.json").read_text())["kind"] == "postprocess_result"
    assert load_postprocess(root).metadata["transferred_count"] == direct.metadata["transferred_count"]
    replayed = load_postprocess(root).metadata["transfer"]
    assert replayed["replayed_pairs"] == 1
    assert replayed["pairs"][0]["request_id"] == direct_raw["payload"]["metadata"]["transfer"]["pairs"][0]["request_id"]


def test_public_cli_failure_reports_canonical_error_and_nonzero_exit(tmp_path):
    root = tmp_path / "outputs"
    root.mkdir()
    missing = _run(root, [Artifact(path="missing.txt")])
    _write_run(root, missing)

    result = runner.invoke(app, ["postprocess", str(root), "-d", f"file://{tmp_path / 'destination'}"])

    assert result.exit_code == 1
    assert "transfer" in result.stdout.lower() or "failed" in result.stdout.lower()
    assert isinstance(load_postprocess(root), PostprocessFailure)


def test_public_destination_identity_is_secret_free_and_stable(tmp_path, monkeypatch):
    root = tmp_path / "outputs"
    root.mkdir()
    (root / "field.txt").write_text("field")
    calls = []

    def transfer(source, destination):
        calls.append(destination)

    _mock_backend(monkeypatch, transfer)
    run = _run(root, [Artifact(path="field.txt")])
    first = _public_postprocess(root, run, ["mock://bucket/path?b=2&token=one"])
    second = _public_postprocess(root, run, ["mock://bucket/path?token=two&b=2"])

    assert isinstance(first, PostprocessSuccess)
    assert isinstance(second, PostprocessSuccess)
    assert _pairs(first)[0]["destination"] == _pairs(second)[0]["destination"]
    assert "token" not in _pairs(first)[0]["destination"]
    assert len(calls) == 1


def test_public_core_rejects_arbitrary_processor_input(tmp_path):
    root = tmp_path / "outputs"
    root.mkdir()
    config = WW3TransferConfig(destinations=[f"file://{tmp_path / 'destination'}"])
    result = ModelRun(run_id="invalid", output_dir=root, run_id_subdir=False).postprocess(
        config, processor_input={"artifacts": []}
    )

    assert isinstance(result, PostprocessFailure)
    assert "concrete ModelRun" in result.error


def test_public_core_requires_non_empty_destinations():
    with pytest.raises(ValueError, match="at least 1 item"):
        WW3TransferConfig(destinations=[])


# Keep a small explicit assertion that the public transfer destination is a URI
# path rather than a filesystem implementation detail.  This replaces the old
# private ``_destination_identity`` unit tests.
def test_public_destination_evidence_uses_redacted_uri_path(tmp_path):
    root = tmp_path / "outputs"
    root.mkdir()
    (root / "field.txt").write_text("field")
    result = _public_postprocess(
        root,
        _run(root, [Artifact(path="field.txt")]),
        ["file://" + str(tmp_path / "destination") + "?token=secret"],
    )
    assert isinstance(result, PostprocessSuccess)
    destination = _pairs(result)[0]["destination"]
    assert urlsplit(destination).query == ""
    assert "secret" not in destination
