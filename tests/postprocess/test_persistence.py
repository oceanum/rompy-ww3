import json
from types import SimpleNamespace
from datetime import datetime, timezone
from pathlib import Path

from rompy.core.responses import Artifact, ArtifactType, TimingInfo

from rompy_ww3.postprocess.persistence import (
    build_persisted,
    write_persisted,
    load_persisted,
    compute_artifact_checksums,
    mark_step_completed,
    is_step_completed,
    RUN_JSON,
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

    # Some ModelRunResult implementations are pydantic; use SimpleNamespace to
    # emulate duck-typed object as used by WW3TransferPostprocessor.
    mr = SimpleNamespace(
        success=True,
        run_id="run-1",
        backend_used="local",
        output_dir=str(output_dir),
        workspace_dir=str(tmp_path),
        timing=timing,
        artifacts=artifacts,
        error=None,
        message=None,
        metadata={},
    )
    return mr


def test_write_and_load_roundtrip(tmp_path):
    mr = _make_model_run(tmp_path)

    # Simulate model_dump output that includes duration_seconds (trap)
    class Dumper:
        def __init__(self, ns):
            self._ns = ns

        def model_dump(self):
            d = dict(vars(self._ns))
            # timing as dict with extra duration_seconds
            t = d.get("timing")
            if t is not None and hasattr(t, "model_dump"):
                tdict = t.model_dump()
            elif isinstance(t, dict):
                tdict = dict(t)
            else:
                tdict = dict(vars(t)) if t is not None else {}
            tdict["duration_seconds"] = 12.34
            d["timing"] = tdict
            return d

    dumped = Dumper(mr)

    persisted = build_persisted(dumped, config={"example": True})
    out = Path(mr.output_dir)
    p = write_persisted(persisted, out)
    assert p.exists()

    loaded = load_persisted(out)
    # Loaded should have basic fields
    assert loaded.run_id == "run-1"
    assert getattr(loaded, "output_dir") == str(out)

    # persisted JSON should not contain duration_seconds (it must be stripped)
    raw_text = (out / RUN_JSON).read_text()
    assert "duration_seconds" not in raw_text


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
    # Inspect run_result.json for state
    raw = json.loads((out / RUN_JSON).read_text())
    assert raw["postprocess"]["transfer"]["completed"] is True
    assert raw["postprocess"]["transfer"]["state"]["count"] == 2


def test_load_from_output_dir_default(tmp_path):
    mr = _make_model_run(tmp_path)
    persisted = build_persisted(mr)
    out = Path(mr.output_dir)
    write_persisted(persisted, out)

    loaded = load_persisted(out)
    assert loaded.run_id == "run-1"
