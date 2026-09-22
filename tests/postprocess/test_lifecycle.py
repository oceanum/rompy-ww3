import json
from datetime import datetime, timezone

from rompy.core.responses import Artifact, ArtifactType, ModelRunSuccess, TimingInfo

from rompy_ww3.postprocess.lifecycle import run_transfer_postprocess
from rompy_ww3.postprocess.persistence import (
    build_persisted,
    is_step_completed,
    load_persisted,
    write_persisted,
)


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
    write_persisted(build_persisted(result), out)


def test_run_transfer_postprocess_creates_marker(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    (out / "restart001.ww3").write_text("data")
    _persisted_run(out, "restart001.ww3", ArtifactType.RESTART)

    run_transfer_postprocess(out, destinations=[f"file://{tmp_path / 'dest'}"])

    assert is_step_completed(out, "transfer")
    loaded = load_persisted(out)
    assert isinstance(loaded, ModelRunSuccess)
    run_raw = json.loads((out / "run_result.json").read_text())
    assert "postprocess" not in run_raw
    state = json.loads((out / "postprocess_state.json").read_text())
    assert state["steps"]["transfer"]["completed"] is True


def test_run_transfer_postprocess_skips_if_completed(tmp_path):
    out = tmp_path / "out2"
    out.mkdir()
    (out / "a.txt").write_text("x")
    _persisted_run(out, "a.txt", ArtifactType.TEXT)

    destination = f"file://{tmp_path / 'dest'}"
    run_transfer_postprocess(out, destinations=[destination])
    assert is_step_completed(out, "transfer")

    before = json.loads((out / "run_result.json").read_text())
    state_before = json.loads((out / "postprocess_state.json").read_text())
    result = run_transfer_postprocess(out, destinations=[destination])
    after = json.loads((out / "run_result.json").read_text())
    state_after = json.loads((out / "postprocess_state.json").read_text())
    assert before == after
    assert state_before["steps"]["transfer"]["state"] == state_after["steps"]["transfer"]["state"]
    assert result.metadata["skipped"] is True
