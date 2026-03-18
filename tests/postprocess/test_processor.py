"""Tests for WW3TransferPostprocessor."""

import pytest
from types import SimpleNamespace
from datetime import datetime, timezone

from rompy_ww3.postprocess.processor import WW3TransferPostprocessor
from rompy.core.responses import (
    PostprocessSuccess,
    Artifact,
    ArtifactType,
)


def test_processor_initialization():
    """Test processor initializes without parameters (new framework pattern)."""
    processor = WW3TransferPostprocessor()
    assert processor is not None


def test_processor_invalid_policy():
    """Test processor raises on invalid failure policy during process()."""
    processor = WW3TransferPostprocessor()
    model_run = SimpleNamespace(output_dir="/tmp/fake", artifacts=[])

    with pytest.raises(ValueError, match="Invalid failure_policy"):
        processor.process(
            model_run,
            destinations=["file:///tmp/dest"],
            failure_policy="INVALID",
        )


def test_processor_empty_destinations():
    """Test processor raises on empty destinations list during process()."""
    processor = WW3TransferPostprocessor()
    model_run = SimpleNamespace(output_dir="/tmp/fake", artifacts=[])

    with pytest.raises(ValueError, match="destinations must be a non-empty list"):
        processor.process(
            model_run,
            destinations=[],
        )


def test_single_destination_transfer(tmp_path):
    """Test successful transfer to single destination."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Create restart files
    restart_file1 = output_dir / "restart001.ww3"
    restart_file1.write_text("test restart data 1")
    restart_file2 = output_dir / "restart002.ww3"
    restart_file2.write_text("test restart data 2")

    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    # Build model_run_result with artifacts
    artifacts = [
        Artifact(path="restart001.ww3", artifact_type=ArtifactType.RESTART),
        Artifact(path="restart002.ww3", artifact_type=ArtifactType.RESTART),
    ]
    model_run_result = SimpleNamespace(
        output_dir=str(output_dir),
        artifacts=artifacts,
        timing=SimpleNamespace(start_time=datetime(2023, 1, 1, tzinfo=timezone.utc)),
        run_id="test-run-001",
    )

    processor = WW3TransferPostprocessor()

    result = processor.process(
        model_run_result,
        destinations=[f"file://{dest_dir}"],
        failure_policy="CONTINUE",
    )

    # Validate response type and success
    assert isinstance(result, PostprocessSuccess)
    assert result.success is True

    # Check metadata
    assert result.metadata["transferred_count"] >= 1
    assert result.metadata["failed_count"] == 0

    # Validate artifacts list
    assert isinstance(result.artifacts, list)


def test_multi_destination_transfer(tmp_path):
    """Test successful transfer to multiple destinations."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    restart_file1 = output_dir / "restart001.ww3"
    restart_file1.write_text("test restart data 1")
    restart_file2 = output_dir / "restart002.ww3"
    restart_file2.write_text("test restart data 2")

    dest1 = tmp_path / "dest1"
    dest1.mkdir()
    dest2 = tmp_path / "dest2"
    dest2.mkdir()

    artifacts = [
        Artifact(path="restart001.ww3", artifact_type=ArtifactType.RESTART),
        Artifact(path="restart002.ww3", artifact_type=ArtifactType.RESTART),
    ]
    model_run_result = SimpleNamespace(
        output_dir=str(output_dir),
        artifacts=artifacts,
        timing=SimpleNamespace(start_time=datetime(2023, 1, 1, tzinfo=timezone.utc)),
        run_id="test-run-001",
    )

    processor = WW3TransferPostprocessor()

    result = processor.process(
        model_run_result,
        destinations=[f"file://{dest1}", f"file://{dest2}"],
        failure_policy="CONTINUE",
    )

    # Validate response type and success
    assert isinstance(result, PostprocessSuccess)
    assert result.success is True

    # Validate artifacts list
    assert isinstance(result.artifacts, list)


def test_output_dir_resolution_direct(tmp_path):
    """Test output_dir resolved from model_run.output_dir."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    model_run = SimpleNamespace(output_dir=str(output_dir))

    processor = WW3TransferPostprocessor()

    resolved = processor._get_output_dir(model_run)
    assert resolved == output_dir


def test_output_dir_resolution_run_dir(tmp_path):
    """Test output_dir resolved from model_run.run_dir."""
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    model_run = SimpleNamespace(run_dir=str(run_dir))

    processor = WW3TransferPostprocessor()

    resolved = processor._get_output_dir(model_run)
    assert resolved == run_dir


def test_output_dir_resolution_config(tmp_path):
    """Test output_dir resolved from model_run.config.output_dir."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    config = SimpleNamespace(output_dir=str(output_dir))
    model_run = SimpleNamespace(config=config)

    processor = WW3TransferPostprocessor()

    resolved = processor._get_output_dir(model_run)
    assert resolved == output_dir


def test_output_dir_resolution_missing():
    """Test output_dir resolution raises when not found."""
    model_run = SimpleNamespace()

    processor = WW3TransferPostprocessor()

    with pytest.raises(AttributeError, match="Cannot determine output directory"):
        processor._get_output_dir(model_run)


def test_no_files_to_transfer(tmp_path):
    """Test graceful handling when no artifacts to transfer."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    model_run_result = SimpleNamespace(
        output_dir=str(output_dir),
        artifacts=[],
        timing=SimpleNamespace(start_time=datetime(2023, 1, 1, tzinfo=timezone.utc)),
        run_id="test-run-001",
    )

    processor = WW3TransferPostprocessor()

    result = processor.process(
        model_run_result,
        destinations=[f"file://{tmp_path}/dest"],
        failure_policy="CONTINUE",
    )

    # Empty artifacts now returns success with zero transfers
    assert isinstance(result, PostprocessSuccess)
    assert result.metadata["transferred_count"] == 0
    assert result.metadata["failed_count"] == 0

    # Artifacts list is empty
    assert isinstance(result.artifacts, list)
    assert len(result.artifacts) == 0
