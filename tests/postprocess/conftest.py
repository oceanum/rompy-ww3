"""Pytest fixtures for postprocess tests."""

from pathlib import Path
import pytest

from rompy_ww3.postprocess.config import (
    UploadConfig,
    FilesystemDestination,
    CloudDestination,
    HTTPDestination,
    FileSelection,
    RetryConfig,
)
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

    # Create sample field output files
    (output_dir / "ww3.20240115.nc").write_text("mock field output")
    (output_dir / "ww3.20240116.nc").write_text("mock field output")

    # Create sample point output files
    (output_dir / "points.20240115.nc").write_text("mock point output")
    (output_dir / "points.20240116.nc").write_text("mock point output")

    # Create sample restart files
    (output_dir / "restart1.ww3").write_text("mock restart 1")
    (output_dir / "restart2.ww3").write_text("mock restart 2")

    # Create sample track file
    (output_dir / "track.20240115.nc").write_text("mock track output")

    return output_dir


@pytest.fixture
def sample_upload_config():
    """Create a valid UploadConfig instance for testing."""
    return UploadConfig(
        destinations=[FilesystemDestination(path=Path("/tmp/test_dest"))],
        file_selection=FileSelection(output_types=["field", "point", "restart"]),
        retry=RetryConfig(max_retries=3, backoff_factor=2.0),
        failure_mode="strict",
    )


@pytest.fixture
def sample_cloud_config():
    """Create UploadConfig with cloud destination."""
    return UploadConfig(
        destinations=[CloudDestination(uri="s3://test-bucket/prefix/")],
        file_selection=FileSelection(output_types=["field", "restart"]),
        retry=RetryConfig(max_retries=2),
        failure_mode="lenient",
    )


@pytest.fixture
def sample_multi_dest_config():
    """Create UploadConfig with multiple destinations."""
    return UploadConfig(
        destinations=[
            FilesystemDestination(path=Path("/tmp/dest1")),
            CloudDestination(uri="s3://bucket/prefix/"),
            HTTPDestination(
                url="https://example.com/upload",
                headers={"Authorization": "Bearer token"},
            ),
        ],
        file_selection=FileSelection(output_types=["field", "point", "restart"]),
        retry=RetryConfig(),
        failure_mode="strict",
    )


@pytest.fixture
def mock_namelist_config():
    """Create mock WW3 namelist configuration for testing.

    Provides sample OutputDate configuration with restart settings
    for testing restart file renaming.
    """
    return OutputDate(
        restart=OutputDateRestart(
            start="20240101 000000",
            stride="86400",  # 1 day in seconds
            stop="20240107 000000",
        )
    )


@pytest.fixture
def mock_http_server():
    """Mock HTTP server for testing HTTP uploads.

    Note: This is a placeholder. Actual implementation would use
    pytest-httpserver or similar for HTTP testing.
    """
    # Placeholder for HTTP server mock
    # In real implementation, use pytest-httpserver fixture
    return {"url": "http://localhost:8888/upload", "status": 200}


@pytest.fixture
def temp_upload_dest(tmp_path):
    """Create temporary upload destination directory."""
    dest_dir = tmp_path / "upload_dest"
    dest_dir.mkdir()
    return dest_dir
