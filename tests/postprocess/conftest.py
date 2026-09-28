"""Pytest fixtures for postprocess tests."""

import pytest
from types import SimpleNamespace
from datetime import datetime, timezone
from typing import List

from rompy_ww3.namelists.output_date import OutputDate, OutputDateRestart


@pytest.fixture
def mock_output_dir(tmp_path):
    """Create temporary directory with sample WW3 output files.

    Creates a mock WW3 output directory structure with:
    - Field output files (ww3.YYYYMMDD.nc)
    - Point output files (points.YYYYMMDD.nc)
    - Restart files (restart1.ww3, restart2.ww3)
    """
    output_dir = tmp_path / "ww3_output"
    output_dir.mkdir()

    (output_dir / "ww3.20240115.nc").write_text("mock field output")
    (output_dir / "ww3.20240116.nc").write_text("mock field output")

    (output_dir / "points.20240115.nc").write_text("mock point output")
    (output_dir / "points.20240116.nc").write_text("mock point output")

    (output_dir / "restart1.ww3").write_text("mock restart 1")
    (output_dir / "restart2.ww3").write_text("mock restart 2")

    (output_dir / "track.20240115.nc").write_text("mock track output")

    return output_dir


@pytest.fixture
def mock_namelist_config():
    """Create mock WW3 namelist configuration for testing.

    Provides sample OutputDate configuration with restart settings
    for testing restart file renaming.
    """
    return OutputDate(
        restart=OutputDateRestart(
            start="20240101 000000",
            stride="86400",
            stop="20240107 000000",
        )
    )


@pytest.fixture
def temp_upload_dest(tmp_path):
    """Create temporary upload destination directory."""
    dest_dir = tmp_path / "upload_dest"
    dest_dir.mkdir()
    return dest_dir


@pytest.fixture
def make_model_run_result():
    """Factory fixture to create ModelRunResult-shaped objects.

    Returns a factory function that creates SimpleNamespace objects
    mimicking ModelRunResult with artifacts, output_dir, timing, and run_id.

    Usage:
        model_run_result = make_model_run_result(
            output_dir=str(tmp_path),
            artifacts=[Artifact(path="restart001.ww3", artifact_type=ArtifactType.RESTART)]
        )
    """

    def _make_model_run_result(
        output_dir: str,
        artifacts: List = None,
        run_id: str = "test-run-001",
        start_time: datetime = None,
    ):
        if artifacts is None:
            artifacts = []
        if start_time is None:
            start_time = datetime(2024, 1, 15, tzinfo=timezone.utc)

        timing = SimpleNamespace(start_time=start_time)
        return SimpleNamespace(
            output_dir=output_dir,
            artifacts=artifacts,
            timing=timing,
            run_id=run_id,
        )

    return _make_model_run_result
