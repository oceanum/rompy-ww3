"""Tests for complete artifact handling integration in WW3TransferPostprocessor."""

from types import SimpleNamespace
from unittest.mock import patch

from rompy_ww3.config import ShelConfig
from rompy_ww3.postprocess.processor import WW3TransferPostprocessor
from rompy.core.responses import (
    ArtifactType,
    Artifact,
)


def run_with_mocks(processor, model_run, **process_kwargs):
    """Helper to run processor with mocked timing extraction methods."""
    with patch.object(
        WW3TransferPostprocessor,
        "_extract_start_date",
        return_value="20230101 000000",
    ):
        with patch.object(
            WW3TransferPostprocessor,
            "_extract_stop_date",
            return_value="20230101 060000",
        ):
            with patch.object(
                WW3TransferPostprocessor,
                "_extract_output_stride",
                return_value=3600,
            ):
                return processor.process(model_run, **process_kwargs)


class TestCompleteArtifactHandling:
    """Test complete artifact handling for all WW3 output types."""

    def test_restart_file_handling_with_config_methods(self, tmp_path):
        """Test restart file handling when config methods are available."""
        output_dir = tmp_path / "output" / "test_run"
        output_dir.mkdir(parents=True)

        restart_file1 = output_dir / "restart001.ww3"
        restart_file1.write_text("test restart data 1")
        restart_file2 = output_dir / "restart002.ww3"
        restart_file2.write_text("test restart data 2")

        def mock_expected_artifacts():
            return [
                Artifact(
                    path="restart001.ww3",
                    artifact_type=ArtifactType.OTHER,
                    size_bytes=19,
                    description="WW3 binary restart file: restart001.ww3",
                ),
                Artifact(
                    path="restart002.ww3",
                    artifact_type=ArtifactType.OTHER,
                    size_bytes=19,
                    description="WW3 binary restart file: restart002.ww3",
                ),
            ]

        def mock_infer_artifacts(files, output_types):
            return mock_expected_artifacts()

        config = ShelConfig()
        model_run = SimpleNamespace(
            output_dir=str(tmp_path / "output"), config=config, run_id="test_run"
        )
        processor = WW3TransferPostprocessor()

        with patch.object(ShelConfig, "expected_artifacts", mock_expected_artifacts):
            with patch.object(ShelConfig, "infer_artifacts", mock_infer_artifacts):
                result = run_with_mocks(
                    processor,
                    model_run,
                    destinations=[f"file://{tmp_path}/dest"],
                    output_types={"restart": {"extra": "DW"}},
                    failure_policy="CONTINUE",
                )

        assert "artifacts_planned" in result.metadata
        planned_artifacts = result.metadata["artifacts_planned"]
        assert len(planned_artifacts) >= 1
        assert "restart" in planned_artifacts[0].path

    def test_field_output_handling_with_config_methods(self, tmp_path):
        """Test field output handling when config methods are available."""
        output_dir = tmp_path / "output" / "test_run"
        output_dir.mkdir(parents=True)

        field_file1 = output_dir / "ww3.20230101_000000.nc"
        field_file1.write_text("test field data 1")
        field_file2 = output_dir / "ww3.20230101_060000.nc"
        field_file2.write_text("test field data 2")

        def mock_expected_artifacts():
            return [
                Artifact(
                    path="ww3.20230101_000000.nc",
                    artifact_type=ArtifactType.NETCDF,
                    size_bytes=18,
                    description="WW3 NetCDF output: ww3.20230101_000000.nc",
                ),
                Artifact(
                    path="ww3.20230101_060000.nc",
                    artifact_type=ArtifactType.NETCDF,
                    size_bytes=18,
                    description="WW3 NetCDF output: ww3.20230101_060000.nc",
                ),
            ]

        def mock_infer_artifacts(files, output_types):
            return mock_expected_artifacts()

        config = ShelConfig()
        model_run = SimpleNamespace(
            output_dir=str(tmp_path / "output"), config=config, run_id="test_run"
        )
        processor = WW3TransferPostprocessor()

        with patch.object(ShelConfig, "expected_artifacts", mock_expected_artifacts):
            with patch.object(ShelConfig, "infer_artifacts", mock_infer_artifacts):
                result = run_with_mocks(
                    processor,
                    model_run,
                    destinations=[f"file://{tmp_path}/dest"],
                    output_types={"field": {"list": [1, 2, 3]}},
                    failure_policy="CONTINUE",
                )

        assert "artifacts_planned" in result.metadata

    def test_point_output_handling_with_config_methods(self, tmp_path):
        """Test point output handling when config methods are available."""
        output_dir = tmp_path / "output" / "test_run"
        output_dir.mkdir(parents=True)

        point_file1 = output_dir / "points.20230101_000000.nc"
        point_file1.write_text("test point data 1")
        point_file2 = output_dir / "points.20230101_060000.nc"
        point_file2.write_text("test point data 2")

        def mock_expected_artifacts():
            return [
                Artifact(
                    path="points.20230101_000000.nc",
                    artifact_type=ArtifactType.NETCDF,
                    size_bytes=18,
                    description="WW3 NetCDF output: points.20230101_000000.nc",
                ),
                Artifact(
                    path="points.20230101_060000.nc",
                    artifact_type=ArtifactType.NETCDF,
                    size_bytes=18,
                    description="WW3 NetCDF output: points.20230101_060000.nc",
                ),
            ]

        def mock_infer_artifacts(files, output_types):
            return mock_expected_artifacts()

        config = ShelConfig()
        model_run = SimpleNamespace(
            output_dir=str(tmp_path / "output"), config=config, run_id="test_run"
        )
        processor = WW3TransferPostprocessor()

        with patch.object(ShelConfig, "expected_artifacts", mock_expected_artifacts):
            with patch.object(ShelConfig, "infer_artifacts", mock_infer_artifacts):
                result = run_with_mocks(
                    processor,
                    model_run,
                    destinations=[f"file://{tmp_path}/dest"],
                    output_types={"point": {"stations": [1, 2, 3]}},
                    failure_policy="CONTINUE",
                )

        assert "artifacts_planned" in result.metadata
        planned_artifacts = result.metadata.get("artifacts_planned", [])
        assert all(
            artifact.artifact_type == ArtifactType.NETCDF
            for artifact in planned_artifacts
        )
        assert all("points." in artifact.path for artifact in planned_artifacts)

    def test_track_output_handling_with_config_methods(self, tmp_path):
        """Test track output handling when config methods are available."""
        output_dir = tmp_path / "output" / "test_run"
        output_dir.mkdir(parents=True)

        track_file1 = output_dir / "track.20230101_000000.nc"
        track_file1.write_text("test track data 1")
        track_file2 = output_dir / "track.20230101_060000.nc"
        track_file2.write_text("test track data 2")

        def mock_expected_artifacts():
            return [
                Artifact(
                    path="track.20230101_000000.nc",
                    artifact_type=ArtifactType.NETCDF,
                    size_bytes=18,
                    description="WW3 NetCDF output: track.20230101_000000.nc",
                ),
                Artifact(
                    path="track.20230101_060000.nc",
                    artifact_type=ArtifactType.NETCDF,
                    size_bytes=18,
                    description="WW3 NetCDF output: track.20230101_060000.nc",
                ),
            ]

        def mock_infer_artifacts(files, output_types):
            return mock_expected_artifacts()

        config = ShelConfig()
        model_run = SimpleNamespace(
            output_dir=str(tmp_path / "output"), config=config, run_id="test_run"
        )
        processor = WW3TransferPostprocessor()

        with patch.object(ShelConfig, "expected_artifacts", mock_expected_artifacts):
            with patch.object(ShelConfig, "infer_artifacts", mock_infer_artifacts):
                result = run_with_mocks(
                    processor,
                    model_run,
                    destinations=[f"file://{tmp_path}/dest"],
                    output_types={"track": {"output": [1, 2, 3]}},
                    failure_policy="CONTINUE",
                )

        assert "artifacts_planned" in result.metadata
        planned_artifacts = result.metadata.get("artifacts_planned", [])
        assert all(
            artifact.artifact_type == ArtifactType.NETCDF
            for artifact in planned_artifacts
        )
        assert all("track." in artifact.path for artifact in planned_artifacts)

    def test_fallback_logic_when_config_methods_not_available(self, tmp_path):
        """Test fallback logic when config methods return empty results."""
        output_dir = tmp_path / "output" / "test_run"
        output_dir.mkdir(parents=True)

        restart_file = output_dir / "restart001.ww3"
        restart_file.write_text("test restart data")

        field_file = output_dir / "ww3.20230101_000000.nc"
        field_file.write_text("test field data")

        def mock_expected_artifacts():
            return [
                Artifact(
                    path="restart001.ww3",
                    artifact_type=ArtifactType.OTHER,
                    size_bytes=17,
                    description="WW3 binary restart file",
                ),
                Artifact(
                    path="ww3.20230101_000000.nc",
                    artifact_type=ArtifactType.NETCDF,
                    size_bytes=15,
                    description="WW3 NetCDF output",
                ),
            ]

        config = ShelConfig()
        model_run = SimpleNamespace(
            output_dir=str(tmp_path / "output"), config=config, run_id="test_run"
        )
        processor = WW3TransferPostprocessor()

        with patch.object(ShelConfig, "expected_artifacts", mock_expected_artifacts):
            result = run_with_mocks(
                processor,
                model_run,
                destinations=[f"file://{tmp_path}/dest"],
                output_types={
                    "restart": {"extra": "DW"},
                    "field": {"list": [1, 2, 3]},
                },
                failure_policy="CONTINUE",
            )

        assert "artifacts_planned" in result.metadata
        planned_artifacts = result.metadata.get("artifacts_planned", [])
        assert len(planned_artifacts) >= 1

        paths = [a.path for a in planned_artifacts]
        assert any("restart" in p for p in paths)

    def test_all_output_types_combined(self, tmp_path):
        """Test all WW3 output types combined in a single run."""
        output_dir = tmp_path / "output" / "test_run"
        output_dir.mkdir(parents=True)

        files_to_create = [
            ("restart001.ww3", "restart data"),
            ("restart002.ww3", "restart data"),
            ("ww3.20230101_000000.nc", "field data"),
            ("ww3.20230101_060000.nc", "field data"),
            ("points.20230101_000000.nc", "point data"),
            ("points.20230101_060000.nc", "point data"),
            ("track.20230101_000000.nc", "track data"),
            ("track.20230101_060000.nc", "track data"),
        ]

        for filename, content in files_to_create:
            file_path = output_dir / filename
            file_path.write_text(content)

        def mock_expected_artifacts():
            artifacts = []
            for filename, content in files_to_create:
                if filename.startswith("restart"):
                    artifact_type = ArtifactType.OTHER
                else:
                    artifact_type = ArtifactType.NETCDF

                artifacts.append(
                    Artifact(
                        path=filename,
                        artifact_type=artifact_type,
                        size_bytes=len(content.encode()),
                        description=f"WW3 output file: {filename}",
                    )
                )
            return artifacts

        config = ShelConfig()
        model_run = SimpleNamespace(
            output_dir=str(tmp_path / "output"), config=config, run_id="test_run"
        )
        processor = WW3TransferPostprocessor()

        with patch.object(ShelConfig, "expected_artifacts", mock_expected_artifacts):
            result = run_with_mocks(
                processor,
                model_run,
                destinations=[f"file://{tmp_path}/dest"],
                output_types={
                    "restart": {"extra": "DW"},
                    "field": {"list": [1, 2, 3]},
                    "point": {"stations": [1, 2, 3]},
                    "track": {"output": [1, 2, 3]},
                },
                failure_policy="CONTINUE",
            )

        assert "artifacts_planned" in result.metadata
        planned_artifacts = result.metadata["artifacts_planned"]
        assert len(planned_artifacts) >= 1

        paths = [a.path for a in planned_artifacts]
        assert any("restart" in p for p in paths)
