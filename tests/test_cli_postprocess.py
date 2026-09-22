import json
from datetime import datetime, timezone

from rompy.core.responses import Artifact, ArtifactType, ModelRunSuccess, TimingInfo
from typer.testing import CliRunner

from rompy_ww3.cli import app
from rompy_ww3.postprocess.persistence import build_persisted, write_persisted

runner = CliRunner()


def make_persisted_dir(
    tmp_path, name="out", artifact_name="a.txt", art_type=ArtifactType.TEXT
):
    out = tmp_path / name
    out.mkdir()
    (out / artifact_name).write_text("x")
    result = ModelRunSuccess(
        success=True,
        run_id=name,
        backend_used="local",
        output_dir=str(out),
        workspace_dir=str(out),
        artifacts=[
            Artifact(
                path=artifact_name,
                artifact_type=art_type,
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
    return out


def test_postprocess_success(tmp_path):
    out = make_persisted_dir(tmp_path)
    dest = f"file://{tmp_path / 'dest'}"
    result = runner.invoke(app, ["postprocess", str(out), "-d", dest])
    assert result.exit_code == 0
    data = json.loads((out / "postprocess_state.json").read_text())
    assert data["steps"]["transfer"]["completed"] is True
    run_data = json.loads((out / "run_result.json").read_text())
    assert run_data["schema_version"] == 2
    assert "postprocess" not in run_data


def test_postprocess_reexecutes_existing_marker_for_new_destination(tmp_path):
    out = make_persisted_dir(tmp_path, name="out2", artifact_name="b.txt")
    first = f"file://{tmp_path / 'dest2-first'}"
    r1 = runner.invoke(app, ["postprocess", str(out), "-d", first])
    assert r1.exit_code == 0
    second = f"file://{tmp_path / 'dest2-second'}"
    r2 = runner.invoke(app, ["postprocess", str(out), "-d", second])
    assert r2.exit_code == 0
    assert "Skipped" not in r2.stdout
    assert (tmp_path / "dest2-second" / "b.txt").exists()


def test_postprocess_missing_path_exits_nonzero(tmp_path):
    missing = tmp_path / "nope"
    dest = f"file://{tmp_path / 'dest3'}"
    r = runner.invoke(app, ["postprocess", str(missing), "-d", dest])
    assert r.exit_code != 0
