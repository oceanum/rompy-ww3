import json
from types import SimpleNamespace
from datetime import datetime, timezone


from rompy_ww3.postprocess.persistence import (
    build_persisted,
    write_persisted,
    load_persisted,
    is_step_completed,
)
from rompy_ww3.postprocess.lifecycle import run_transfer_postprocess
from rompy.core.responses import Artifact, ArtifactType
from rompy.core.responses import TimingInfo


def test_run_transfer_postprocess_creates_marker(tmp_path):
    # Prepare persisted run_result.json in output dir with one artifact file
    out = tmp_path / "out"
    out.mkdir()
    (out / "restart001.ww3").write_text("data")

    artifacts = [
        Artifact(
            path="restart001.ww3",
            artifact_type=ArtifactType.RESTART,
            size_bytes=None,
            description="",
            date=None,
        )
    ]
    mr = SimpleNamespace(
        success=True,
        run_id="r1",
        backend_used="local",
        output_dir=str(out),
        workspace_dir=str(out),
        artifacts=artifacts,
        timing=TimingInfo(
            start_time=datetime.now(timezone.utc), end_time=datetime.now(timezone.utc)
        ),
        error=None,
        message=None,
        metadata={},
    )

    persisted = build_persisted(mr)
    write_persisted(persisted, out)

    # Run lifecycle
    run_transfer_postprocess(out, destinations=[f"file://{tmp_path / 'dest'}"])

    # Should mark step completed in run_result.json
    assert is_step_completed(out, "transfer")
    loaded = load_persisted(out)
    post = getattr(loaded, "postprocess", {})
    assert "transfer" in post


def test_run_transfer_postprocess_skips_if_completed(tmp_path):
    out = tmp_path / "out2"
    out.mkdir()
    (out / "a.txt").write_text("x")

    artifacts = [
        Artifact(
            path="a.txt",
            artifact_type=ArtifactType.TEXT,
            size_bytes=None,
            description="",
            date=None,
        )
    ]
    mr = SimpleNamespace(
        success=True,
        run_id="r2",
        backend_used="local",
        output_dir=str(out),
        workspace_dir=str(out),
        artifacts=artifacts,
        timing=TimingInfo(
            start_time=datetime.now(timezone.utc), end_time=datetime.now(timezone.utc)
        ),
        error=None,
        message=None,
        metadata={},
    )

    persisted = build_persisted(mr)
    write_persisted(persisted, out)

    # First run to set marker
    run_transfer_postprocess(out, destinations=[f"file://{tmp_path / 'dest'}"])
    assert is_step_completed(out, "transfer")

    # Capture run_result.json content and run again - should be skipped and not duplicate
    before = json.loads((out / "run_result.json").read_text())
    result2 = run_transfer_postprocess(
        out, destinations=[f"file://{tmp_path / 'dest'}"]
    )
    after = json.loads((out / "run_result.json").read_text())
    assert before == after
    # And result should indicate skip via metadata if possible
    assert getattr(result2, "metadata", {}).get("skipped") is True
