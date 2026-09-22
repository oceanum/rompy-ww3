"""Tests for WW3TransferPostprocessor."""

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from rompy.core.responses import (
    Artifact,
    ArtifactType,
    ModelRunSuccess,
    PostprocessSuccess,
    TimingInfo,
)

from rompy_ww3.postprocess.processor import WW3TransferPostprocessor


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


def test_output_dir_resolution_rejects_private_config(tmp_path):
    """Config-only v1 objects are not an accepted sidecar contract."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    model_run = SimpleNamespace(config=SimpleNamespace(output_dir=str(output_dir)))
    processor = WW3TransferPostprocessor()
    with pytest.raises(AttributeError, match="Cannot determine output directory"):
        processor._get_output_dir(model_run)


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


def test_processor_uses_typed_timing_and_metadata(tmp_path):
    """Canonical ModelRunResult supplies timing and WW3 metadata."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    restart_file = output_dir / "restart001.ww3"
    restart_file.write_text("test restart data")
    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()
    start = datetime(2024, 1, 15, tzinfo=timezone.utc)
    model_run_result = ModelRunSuccess(
        success=True,
        run_id="test-run-ctx",
        backend_used="local",
        output_dir=str(output_dir),
        workspace_dir=str(output_dir),
        artifacts=[Artifact(path="restart001.ww3", artifact_type=ArtifactType.RESTART)],
        expected_outputs=[],
        missing_outputs=[],
        timing=TimingInfo(start_time=start, end_time=start),
        metadata={"ww3": {"restart_stride_seconds": 3600}},
    )
    processor = WW3TransferPostprocessor()
    assert processor._extract_start_date(model_run_result) == "20240115 000000"
    assert processor._extract_output_stride(model_run_result) == 3600
    result = processor.process(
        model_run_result,
        destinations=[f"file://{dest_dir}"],
        failure_policy="CONTINUE",
    )
    assert isinstance(result, PostprocessSuccess)
    assert result.success is True
    assert result.metadata["name_map"][str(output_dir / "restart001.ww3")] == "20240115_000000_restart.ww3"


def test_processor_ignores_private_config_fallback(tmp_path):
    """Private v1 config data is not consulted for transfer naming."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    start = datetime(2024, 1, 10, tzinfo=timezone.utc)
    processor = WW3TransferPostprocessor()
    typed = ModelRunSuccess(
        success=True,
        run_id="test-run-v1",
        backend_used="local",
        output_dir=str(output_dir),
        artifacts=[],
        expected_outputs=[],
        missing_outputs=[],
        timing=TimingInfo(start_time=start, end_time=start),
        metadata={},
    )
    assert processor._extract_output_stride(typed) is None


def test_processor_restart_only_default_keeps_non_restart_name(tmp_path):
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    field_file = output_dir / "ww3.202001.nc"
    field_file.write_text("field data")

    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    ctx = SimpleNamespace(
        period_start=datetime(2024, 1, 15, 0, 0, 0, tzinfo=timezone.utc),
        period_end=datetime(2024, 1, 20, 0, 0, 0, tzinfo=timezone.utc),
        output_dir=str(tmp_path),
        staging_dir=str(output_dir),
        extensions={"ww3": {"restart_stride_seconds": 3600}},
    )
    model_run_result = SimpleNamespace(
        output_dir=str(output_dir),
        artifacts=[Artifact(path="ww3.202001.nc", artifact_type=ArtifactType.NETCDF)],
        timing=SimpleNamespace(start_time=datetime(2026, 3, 19, tzinfo=timezone.utc)),
        run_id="test-run-fields",
        normalized_context=ctx,
    )

    processor = WW3TransferPostprocessor()
    result = processor.process(
        model_run_result,
        destinations=[f"file://{dest_dir}"],
        failure_policy="CONTINUE",
    )

    assert isinstance(result, PostprocessSuccess)
    assert (
        result.metadata["name_map"][str(output_dir / "ww3.202001.nc")]
        == "ww3.202001.nc"
    )


def test_processor_exposes_transfer_log_entries(tmp_path):
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    restart_file = output_dir / "restart001.ww3"
    restart_file.write_text("restart")

    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    ctx = SimpleNamespace(
        period_start=datetime(2024, 1, 15, 0, 0, 0, tzinfo=timezone.utc),
        period_end=datetime(2024, 1, 20, 0, 0, 0, tzinfo=timezone.utc),
        output_dir=str(tmp_path),
        staging_dir=str(output_dir),
        extensions={"ww3": {"restart_stride_seconds": 3600}},
    )
    model_run_result = SimpleNamespace(
        output_dir=str(output_dir),
        artifacts=[Artifact(path="restart001.ww3", artifact_type=ArtifactType.RESTART)],
        timing=SimpleNamespace(start_time=datetime(2026, 3, 19, tzinfo=timezone.utc)),
        run_id="test-run-logging",
        normalized_context=ctx,
    )

    processor = WW3TransferPostprocessor()
    result = processor.process(
        model_run_result,
        destinations=[f"file://{dest_dir}"],
        failure_policy="CONTINUE",
    )

    assert isinstance(result, PostprocessSuccess)
    assert result.metadata["transferred_count"] == 1
    assert result.metadata["failed_count"] == 0


def test_processor_v1_sidecar_is_not_an_accepted_result_contract():
    """A flat/partial v1 object is rejected instead of heuristically migrated."""
    model_run_result = SimpleNamespace(
        artifacts=[],
        timing=SimpleNamespace(start_time=datetime(2024, 1, 1, tzinfo=timezone.utc)),
        run_id="test-run-v1-sidecar",
    )
    processor = WW3TransferPostprocessor()
    with pytest.raises(TypeError, match="core-compatible ModelRunResult"):
        processor.process(
            model_run_result,
            destinations=["file:///tmp/dest"],
            failure_policy="CONTINUE",
        )
    with pytest.raises(AttributeError, match="Cannot determine output directory"):
        processor._get_output_dir(model_run_result)


def test_shel_config_populates_extensions():
    """Test ShelConfig populates WW3 extensions correctly."""
    from rompy_ww3.components import Shel
    from rompy_ww3.config import ShelConfig
    from rompy_ww3.namelists import OutputDate
    from rompy_ww3.namelists.output_date import OutputDateRestart

    config = ShelConfig(
        ww3_shel=Shel(
            output_date=OutputDate(restart=OutputDateRestart(stride=3600)),
        )
    )

    extensions = config.get_normalized_extensions()

    assert "ww3" in extensions
    assert extensions["ww3"]["config_variant"] == "ww3shel"
    assert extensions["ww3"]["restart_stride_seconds"] == 3600


def test_shel_config_extensions_no_restart():
    """Test ShelConfig extensions when restart stride is not configured."""
    from rompy_ww3.components import Shel
    from rompy_ww3.config import ShelConfig

    config = ShelConfig(ww3_shel=Shel())

    extensions = config.get_normalized_extensions()

    assert "ww3" in extensions
    assert extensions["ww3"]["config_variant"] == "ww3shel"
    assert extensions["ww3"]["restart_stride_seconds"] is None


def test_multi_config_populates_extensions():
    """Test MultiConfig populates WW3 extensions correctly."""
    from rompy_ww3.components import Grid, Multi
    from rompy_ww3.config import GridSpec, MultiConfig
    from rompy_ww3.namelists import InputGrid, OutputDate
    from rompy_ww3.namelists.output_date import OutputDateRestart

    config = MultiConfig(
        multi=Multi(
            input_grid=InputGrid(name="grid1"),
            output_date=OutputDate(restart=OutputDateRestart(stride=7200)),
        ),
        grids=[
            GridSpec(name="grid1", grid=Grid()),
        ],
    )

    extensions = config.get_normalized_extensions()

    assert "ww3" in extensions
    assert extensions["ww3"]["config_variant"] == "ww3multi"
    assert extensions["ww3"]["restart_stride_seconds"] == 7200
