"""Tests for WW3TransferPostprocessor."""

import pytest
from types import SimpleNamespace

from rompy_ww3.postprocess.processor import WW3TransferPostprocessor


def test_processor_initialization():
    """Test processor initializes without parameters (new framework pattern)."""
    processor = WW3TransferPostprocessor()
    assert processor is not None


def test_processor_invalid_policy():
    """Test processor raises on invalid failure policy during process()."""
    processor = WW3TransferPostprocessor()
    model_run = SimpleNamespace(output_dir="/tmp/fake")

    with pytest.raises(ValueError, match="Invalid failure_policy"):
        processor.process(
            model_run,
            destinations=["file:///tmp/dest"],
            output_types={},
            failure_policy="INVALID",
        )


def test_processor_empty_destinations():
    """Test processor raises on empty destinations list during process()."""
    processor = WW3TransferPostprocessor()
    model_run = SimpleNamespace(output_dir="/tmp/fake")

    with pytest.raises(ValueError, match="destinations must be a non-empty list"):
        processor.process(
            model_run,
            destinations=[],
            output_types={},
        )


def test_single_destination_transfer(tmp_path):
    """Test successful transfer to single destination."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    restart_file = output_dir / "restart.ww3"
    restart_file.write_text("test restart data")

    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    model_run = SimpleNamespace(output_dir=str(output_dir))

    processor = WW3TransferPostprocessor()

    result = processor.process(
        model_run,
        destinations=[f"file://{dest_dir}"],
        output_types={"restart": {"extra": "DW"}},
        failure_policy="CONTINUE",
        start_date="20230101 000000",
    )

    assert result["success"] is True
    assert result["transferred_count"] >= 0
    assert result["failed_count"] == 0
    assert isinstance(result["results"], list)


def test_multi_destination_transfer(tmp_path):
    """Test successful transfer to multiple destinations."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    restart_file = output_dir / "restart.ww3"
    restart_file.write_text("test restart data")

    dest1 = tmp_path / "dest1"
    dest1.mkdir()
    dest2 = tmp_path / "dest2"
    dest2.mkdir()

    model_run = SimpleNamespace(output_dir=str(output_dir))

    processor = WW3TransferPostprocessor()

    result = processor.process(
        model_run,
        destinations=[f"file://{dest1}", f"file://{dest2}"],
        output_types={"restart": {"extra": "DW"}},
        failure_policy="CONTINUE",
        start_date="20230101 000000",
    )

    assert result["success"] is True
    assert isinstance(result["results"], list)


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
    """Test graceful handling when no files match manifest."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    model_run = SimpleNamespace(output_dir=str(output_dir))

    processor = WW3TransferPostprocessor()

    result = processor.process(
        model_run,
        destinations=[f"file://{tmp_path}/dest"],
        output_types={"restart": {"extra": "DW"}},
        failure_policy="CONTINUE",
    )

    assert result["transferred_count"] == 0
    assert isinstance(result["results"], list)
