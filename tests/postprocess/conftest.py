"""Pytest fixtures for postprocess tests."""

import pytest

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
