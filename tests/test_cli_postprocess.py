import json
from types import SimpleNamespace
from datetime import datetime, timezone

from typer.testing import CliRunner

from rompy_ww3.postprocess.persistence import build_persisted, write_persisted
from rompy_ww3.postprocess.lifecycle import TRANSFER_STEP
from rompy.core.responses import Artifact, ArtifactType, TimingInfo

from rompy_ww3.cli import app


runner = CliRunner()


def make_persisted_dir(
    tmp_path, name="out", artifact_name="a.txt", art_type=ArtifactType.TEXT
):
    out = tmp_path / name
    out.mkdir()
    (out / artifact_name).write_text("x")

    artifacts = [
        Artifact(
            path=artifact_name,
            artifact_type=art_type,
            size_bytes=None,
            description="",
            date=None,
        )
    ]
    mr = SimpleNamespace(
        success=True,
        run_id="rtest",
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
    return out


def test_postprocess_success(tmp_path):
    out = make_persisted_dir(tmp_path)
    dest = f"file://{tmp_path / 'dest'}"
    result = runner.invoke(app, ["postprocess", str(out), "-d", dest])
    assert result.exit_code == 0
    data = json.loads((out / "run_result.json").read_text())
    assert data.get("postprocess", {}).get(TRANSFER_STEP, {}).get("completed") is True


def test_postprocess_skips_if_already_completed(tmp_path):
    out = make_persisted_dir(tmp_path, name="out2", artifact_name="b.txt")
    dest = f"file://{tmp_path / 'dest2'}"
    r1 = runner.invoke(app, ["postprocess", str(out), "-d", dest])
    assert r1.exit_code == 0
    r2 = runner.invoke(app, ["postprocess", str(out), "-d", dest])
    assert r2.exit_code == 0
    assert "Skipped" in r2.stdout or "skipped" in r2.stdout


def test_postprocess_missing_path_exits_nonzero(tmp_path):
    missing = tmp_path / "nope"
    dest = f"file://{tmp_path / 'dest3'}"
    r = runner.invoke(app, ["postprocess", str(missing), "-d", dest])
    assert r.exit_code != 0
