import json
from datetime import datetime, timezone

from rompy.core import result_persistence
from rompy.core.responses import (
    Artifact,
    ArtifactType,
    ModelRunSuccess,
    RunResultSidecar,
    TimingInfo,
)

from rompy_ww3.postprocess.lifecycle import run_transfer_postprocess


def _persisted_run(out, artifact_name, artifact_type):
    result = ModelRunSuccess(
        success=True,
        run_id=out.name,
        backend_used="local",
        output_dir=str(out),
        workspace_dir=str(out),
        artifacts=[
            Artifact(
                path=artifact_name,
                artifact_type=artifact_type,
                size_bytes=None,
                description="",
                date=None,
            )
        ],
        expected_outputs=[],
        missing_outputs=[],
        timing=TimingInfo(
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc),
        ),
        message=None,
        metadata={},
    )
    result_persistence.write_run_result(
        out,
        RunResultSidecar(
            run_id=result.run_id,
            status="success",
            success=True,
            staging_dir=str(out),
            payload=result,
        ),
    )


def test_run_transfer_postprocess_persists_core_result_only(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    (out / "restart001.ww3").write_text("data")
    _persisted_run(out, "restart001.ww3", ArtifactType.RESTART)

    run_transfer_postprocess(out, destinations=[f"file://{tmp_path / 'dest'}"])

    loaded = result_persistence.load_run_result(out).payload
    assert isinstance(loaded, ModelRunSuccess)
    run_raw = json.loads((out / "run_result.json").read_text())
    assert "postprocess" not in run_raw
    assert (out / "postprocess_result.json").exists()
    assert not (out / "postprocess_state.json").exists()


def test_run_transfer_postprocess_reexecutes_existing_marker_for_new_request(tmp_path):
    out = tmp_path / "out2"
    out.mkdir()
    (out / "a.txt").write_text("x")
    _persisted_run(out, "a.txt", ArtifactType.TEXT)

    first_destination = f"file://{tmp_path / 'dest-first'}"
    run_transfer_postprocess(out, destinations=[first_destination])
    assert (out / "postprocess_result.json").exists()

    before = json.loads((out / "run_result.json").read_text())
    second_destination = f"file://{tmp_path / 'dest-second'}"
    result = run_transfer_postprocess(out, destinations=[second_destination])
    after = json.loads((out / "run_result.json").read_text())
    assert before == after
    assert result.success is True
    assert result.metadata.get("skipped") is None
    assert (tmp_path / "dest-second" / "a.txt").exists()
