"""Focused coverage for the WW3/core postprocess integration gate."""

from datetime import datetime, timezone
from pathlib import Path

from rompy.core import result_persistence
from rompy.core.responses import Artifact, ArtifactType, ModelRunSuccess, TimingInfo
from rompy.model import ModelRun
from rompy.postprocess import transfer as core_transfer

from rompy_ww3.postprocess.config import WW3TransferConfig
from rompy_ww3.postprocess.lifecycle import run_transfer_postprocess
from rompy_ww3.postprocess.naming import WW3TargetNaming, target_naming_for_run
from rompy_ww3.postprocess.persistence import build_persisted, write_persisted
from rompy_ww3.postprocess.processor import WW3TransferPostprocessor


def _run(root: Path, artifacts: list[Artifact], metadata=None) -> ModelRunSuccess:
    stamp = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return ModelRunSuccess(
        run_id="core-adapter",
        backend_used="local",
        output_dir=str(root),
        workspace_dir=str(root),
        artifacts=artifacts,
        expected_outputs=[],
        missing_outputs=[],
        timing=TimingInfo(start_time=stamp, end_time=stamp),
        metadata=metadata or {},
    )


def test_ww3_target_strategy_preserves_restart_and_policy_semantics():
    strategy = WW3TargetNaming(
        start_date="20240101 000000", output_stride=3600, naming_policy="restart_only"
    )
    restart = Artifact(path="restart002.ww3", artifact_type=ArtifactType.RESTART)
    field = Artifact(path="ww3.202401.nc", artifact_type=ArtifactType.NETCDF)
    assert strategy(restart) == "20240101_010000_restart.ww3"
    assert strategy(field) == "ww3.202401.nc"
    all_dated = WW3TargetNaming(
        start_date="20240101 000000", output_stride=3600, naming_policy="datestamp_all"
    )
    assert all_dated(field) == "20240101_000000_ww3.202401.nc"


def test_transfer_delegates_to_core_and_keeps_evidence_secret_free(tmp_path):
    source = tmp_path / "one.txt"
    source.write_text("one")
    destination = f"file://{tmp_path / 'destination'}?token=secret-value"
    result = WW3TransferPostprocessor().process(
        _run(tmp_path, [Artifact(path="one.txt", artifact_type=ArtifactType.TEXT)]),
        [destination],
    )
    assert result.success is True
    serialized = result.model_dump_json()
    assert "secret-value" not in serialized
    assert "token=" not in serialized
    assert (tmp_path / "destination" / "one.txt").read_text() == "one"
    assert "transfer" in result.metadata


def test_modelrun_postprocess_uses_the_same_core_adapter(tmp_path):
    (tmp_path / "field.txt").write_text("field")
    run = _run(tmp_path, [Artifact(path="field.txt", artifact_type=ArtifactType.TEXT)])
    result = ModelRun(run_id="core-adapter", output_dir=tmp_path).postprocess(
        WW3TransferConfig(destinations=[f"file://{tmp_path / 'destination'}"]),
        processor_input=run,
    )
    assert result.success is True
    assert (tmp_path / "destination" / "field.txt").read_text() == "field"
    assert (
        result_persistence.load_postprocess_result(
            tmp_path / "core-adapter"
        ).payload.success
        is True
    )


def test_standalone_lifecycle_uses_core_sidecar(tmp_path):
    (tmp_path / "field.txt").write_text("field")
    run = _run(tmp_path, [Artifact(path="field.txt", artifact_type=ArtifactType.TEXT)])
    write_persisted(build_persisted(run), tmp_path)
    result = run_transfer_postprocess(tmp_path, [f"file://{tmp_path / 'destination'}"])
    assert result.success is True
    loaded = result_persistence.load_postprocess_result(tmp_path)
    assert loaded.payload.success is True
    assert result_persistence.load_run_result(tmp_path).payload.run_id == "core-adapter"


def test_core_retry_and_replay_are_used_by_the_adapter(tmp_path, monkeypatch):
    source = tmp_path / "field.txt"
    source.write_text("field")
    calls = []

    class Backend:
        def put(self, source_path, destination):
            calls.append((Path(source_path), destination))
            if len(calls) == 1:
                raise RuntimeError("temporary backend failure")
            target = Path(destination.removeprefix("file://"))
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(Path(source_path).read_bytes())

    monkeypatch.setattr(core_transfer, "get_transfer", lambda _destination: Backend())
    run = _run(tmp_path, [Artifact(path="field.txt", artifact_type=ArtifactType.TEXT)])
    destination = f"file://{tmp_path / 'destination'}"
    first = WW3TransferPostprocessor().process(run, [destination], max_retries=1)
    second = WW3TransferPostprocessor().process(run, [destination], max_retries=1)
    assert first.success is True
    assert second.success is True
    assert len(calls) == 2
    assert second.metadata["transfer"]["replayed_pairs"] == 1


def test_strategy_uses_typed_run_timing_and_ww3_metadata():
    run = _run(
        Path("."),
        [],
        metadata={"ww3": {"restart_stride_seconds": 7200}},
    )
    strategy = target_naming_for_run(run)
    assert strategy(
        Artifact(path="restart003.ww3", artifact_type=ArtifactType.RESTART)
    ) == ("20240101_040000_restart.ww3")
