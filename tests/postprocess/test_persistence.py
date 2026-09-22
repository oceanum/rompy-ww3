import json
from datetime import datetime, timezone
from pathlib import Path

from rompy.core.responses import Artifact, ArtifactType, ModelRunSuccess, TimingInfo

from rompy_ww3.postprocess.persistence import (
    RUN_JSON,
    build_persisted,
    compute_artifact_checksums,
    is_step_completed,
    load_persisted,
    mark_step_completed,
    write_persisted,
)


def _make_model_run(tmp_path):
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    # create artifact files
    f1 = output_dir / "a.txt"
    f1.write_text("hello")

    artifacts = [
        Artifact(
            path="a.txt",
            artifact_type=ArtifactType.TEXT,
            size_bytes=5,
            description="f1",
            date=None,
        )
    ]
    start = datetime(2023, 1, 1, tzinfo=timezone.utc)
    timing = TimingInfo(start_time=start, end_time=start)

    mr = ModelRunSuccess(
        success=True,
        run_id="run-1",
        backend_used="local",
        output_dir=str(output_dir),
        workspace_dir=str(tmp_path),
        timing=timing,
        artifacts=artifacts,
        expected_outputs=[],
        missing_outputs=[],
        message=None,
        metadata={},
    )
    return mr


def test_write_and_load_roundtrip(tmp_path):
    mr = _make_model_run(tmp_path)

    persisted = build_persisted(mr)
    out = Path(mr.output_dir)
    p = write_persisted(persisted, out)
    assert p.exists()

    loaded = load_persisted(out)
    # Loaded should have basic fields
    assert loaded.run_id == "run-1"
    assert loaded.output_dir == str(out)

    raw = json.loads((out / RUN_JSON).read_text())
    assert raw["kind"] == "run_result"
    assert raw["schema_version"] == 2
    assert raw["payload"]["timing"]["duration_seconds"] == 0.0


def test_checksum_capture_and_relative_paths(tmp_path):
    mr = _make_model_run(tmp_path)
    persisted = build_persisted(mr)
    out = Path(mr.output_dir)
    write_persisted(persisted, out)

    loaded = load_persisted(out)
    checks = compute_artifact_checksums(loaded)
    assert "a.txt" in checks
    assert checks["a.txt"] != ""  # checksum exists


def test_postprocess_markers_idempotent(tmp_path):
    mr = _make_model_run(tmp_path)
    persisted = build_persisted(mr)
    out = Path(mr.output_dir)
    write_persisted(persisted, out)

    assert not is_step_completed(out, "transfer")
    mark_step_completed(out, "transfer", state={"count": 1})
    assert is_step_completed(out, "transfer")
    # Call again with updated state - should remain completed and update state
    mark_step_completed(out, "transfer", state={"count": 2})
    # Lifecycle state is separate and the canonical run envelope is untouched.
    raw = json.loads((out / "postprocess_state.json").read_text())
    assert raw["steps"]["transfer"]["completed"] is True
    assert raw["steps"]["transfer"]["state"]["count"] == 2
    run_raw = json.loads((out / RUN_JSON).read_text())
    assert "postprocess" not in run_raw
    assert run_raw["schema_version"] == 2


def test_load_from_output_dir_default(tmp_path):
    mr = _make_model_run(tmp_path)
    persisted = build_persisted(mr)
    out = Path(mr.output_dir)
    write_persisted(persisted, out)

    loaded = load_persisted(out)
    assert loaded.run_id == "run-1"
