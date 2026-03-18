"""Tests for complete artifact handling integration in WW3TransferPostprocessor."""

from types import SimpleNamespace
from datetime import datetime, timezone

from rompy_ww3.postprocess.processor import WW3TransferPostprocessor
from rompy.core.responses import ArtifactType, Artifact, PostprocessSuccess


class TestCompleteArtifactHandling:
    """Test complete artifact handling for all WW3 output types."""

    def test_restart_file_handling(self, tmp_path):
        """Test restart file handling with artifacts."""
        output_dir = tmp_path / "ww3_output"
        output_dir.mkdir()

        restart_file1 = output_dir / "restart001.ww3"
        restart_file1.write_text("test restart data 1")
        restart_file2 = output_dir / "restart002.ww3"
        restart_file2.write_text("test restart data 2")

        artifacts = [
            Artifact(
                path="restart001.ww3",
                artifact_type=ArtifactType.RESTART,
                size_bytes=None,
                description=None,
                date=None,
            ),
            Artifact(
                path="restart002.ww3",
                artifact_type=ArtifactType.RESTART,
                size_bytes=None,
                description=None,
                date=None,
            ),
        ]

        model_run_result = SimpleNamespace(
            output_dir=str(output_dir),
            artifacts=artifacts,
            timing=SimpleNamespace(
                start_time=datetime(2023, 1, 1, tzinfo=timezone.utc)
            ),
            run_id="test-run-001",
        )

        processor = WW3TransferPostprocessor()
        result = processor.process(
            model_run_result,
            destinations=[f"file://{tmp_path}/dest"],
            failure_policy="CONTINUE",
        )

        assert isinstance(result, PostprocessSuccess)
        assert result.metadata["transferred_count"] >= 1
        assert isinstance(result.artifacts, list)

        paths = [a.path for a in result.artifacts]
        assert any("restart" in p for p in paths)

    def test_field_output_handling(self, tmp_path):
        """Test field output handling with artifacts."""
        output_dir = tmp_path / "ww3_output"
        output_dir.mkdir()

        field_file1 = output_dir / "ww3.20230101_000000.nc"
        field_file1.write_text("test field data 1")
        field_file2 = output_dir / "ww3.20230101_060000.nc"
        field_file2.write_text("test field data 2")

        artifacts = [
            Artifact(
                path="ww3.20230101_000000.nc",
                artifact_type=ArtifactType.NETCDF,
                size_bytes=None,
                description=None,
                date=None,
            ),
            Artifact(
                path="ww3.20230101_060000.nc",
                artifact_type=ArtifactType.NETCDF,
                size_bytes=None,
                description=None,
                date=None,
            ),
        ]

        model_run_result = SimpleNamespace(
            output_dir=str(output_dir),
            artifacts=artifacts,
            timing=SimpleNamespace(
                start_time=datetime(2023, 1, 1, tzinfo=timezone.utc)
            ),
            run_id="test-run-001",
        )

        processor = WW3TransferPostprocessor()
        result = processor.process(
            model_run_result,
            destinations=[f"file://{tmp_path}/dest"],
            failure_policy="CONTINUE",
        )

        assert isinstance(result, PostprocessSuccess)
        assert result.metadata["transferred_count"] >= 1
        assert isinstance(result.artifacts, list)

    def test_point_output_handling(self, tmp_path):
        """Test point output handling with artifacts."""
        output_dir = tmp_path / "ww3_output"
        output_dir.mkdir()

        point_file1 = output_dir / "points.20230101_000000.nc"
        point_file1.write_text("test point data 1")
        point_file2 = output_dir / "points.20230101_060000.nc"
        point_file2.write_text("test point data 2")

        artifacts = [
            Artifact(
                path="points.20230101_000000.nc",
                artifact_type=ArtifactType.NETCDF,
                size_bytes=None,
                description=None,
                date=None,
            ),
            Artifact(
                path="points.20230101_060000.nc",
                artifact_type=ArtifactType.NETCDF,
                size_bytes=None,
                description=None,
                date=None,
            ),
        ]

        model_run_result = SimpleNamespace(
            output_dir=str(output_dir),
            artifacts=artifacts,
            timing=SimpleNamespace(
                start_time=datetime(2023, 1, 1, tzinfo=timezone.utc)
            ),
            run_id="test-run-001",
        )

        processor = WW3TransferPostprocessor()
        result = processor.process(
            model_run_result,
            destinations=[f"file://{tmp_path}/dest"],
            failure_policy="CONTINUE",
        )

        assert isinstance(result, PostprocessSuccess)
        assert all(
            artifact.artifact_type == ArtifactType.NETCDF
            for artifact in result.artifacts
        )
        assert all("points." in artifact.path for artifact in result.artifacts)

    def test_track_output_handling(self, tmp_path):
        """Test track output handling with artifacts."""
        output_dir = tmp_path / "ww3_output"
        output_dir.mkdir()

        track_file1 = output_dir / "track.20230101_000000.nc"
        track_file1.write_text("test track data 1")
        track_file2 = output_dir / "track.20230101_060000.nc"
        track_file2.write_text("test track data 2")

        artifacts = [
            Artifact(
                path="track.20230101_000000.nc",
                artifact_type=ArtifactType.NETCDF,
                size_bytes=None,
                description=None,
                date=None,
            ),
            Artifact(
                path="track.20230101_060000.nc",
                artifact_type=ArtifactType.NETCDF,
                size_bytes=None,
                description=None,
                date=None,
            ),
        ]

        model_run_result = SimpleNamespace(
            output_dir=str(output_dir),
            artifacts=artifacts,
            timing=SimpleNamespace(
                start_time=datetime(2023, 1, 1, tzinfo=timezone.utc)
            ),
            run_id="test-run-001",
        )

        processor = WW3TransferPostprocessor()
        result = processor.process(
            model_run_result,
            destinations=[f"file://{tmp_path}/dest"],
            failure_policy="CONTINUE",
        )

        assert isinstance(result, PostprocessSuccess)
        assert all(
            artifact.artifact_type == ArtifactType.NETCDF
            for artifact in result.artifacts
        )
        assert all("track." in artifact.path for artifact in result.artifacts)

    def test_artifact_type_filtering(self, tmp_path):
        """Test artifact_types filter includes only matching artifacts."""
        output_dir = tmp_path / "ww3_output"
        output_dir.mkdir()

        restart_file = output_dir / "restart001.ww3"
        restart_file.write_text("test restart data")

        field_file = output_dir / "ww3.20230101_000000.nc"
        field_file.write_text("test field data")

        artifacts = [
            Artifact(
                path="restart001.ww3",
                artifact_type=ArtifactType.RESTART,
                size_bytes=None,
                description=None,
                date=None,
            ),
            Artifact(
                path="ww3.20230101_000000.nc",
                artifact_type=ArtifactType.NETCDF,
                size_bytes=None,
                description=None,
                date=None,
            ),
        ]

        model_run_result = SimpleNamespace(
            output_dir=str(output_dir),
            artifacts=artifacts,
            timing=SimpleNamespace(
                start_time=datetime(2023, 1, 1, tzinfo=timezone.utc)
            ),
            run_id="test-run-001",
        )

        processor = WW3TransferPostprocessor()

        result = processor.process(
            model_run_result,
            destinations=[f"file://{tmp_path}/dest"],
            artifact_types=[ArtifactType.NETCDF],
            failure_policy="CONTINUE",
        )

        assert isinstance(result, PostprocessSuccess)
        assert result.metadata["transferred_count"] == 1
        assert len(result.artifacts) == 1
        assert result.artifacts[0].artifact_type == ArtifactType.NETCDF

    def test_all_output_types_combined(self, tmp_path):
        """Test all WW3 output types combined in a single run."""
        output_dir = tmp_path / "ww3_output"
        output_dir.mkdir()

        files_to_create = [
            ("restart001.ww3", "restart data", ArtifactType.RESTART),
            ("restart002.ww3", "restart data", ArtifactType.RESTART),
            ("ww3.20230101_000000.nc", "field data", ArtifactType.NETCDF),
            ("ww3.20230101_060000.nc", "field data", ArtifactType.NETCDF),
            ("points.20230101_000000.nc", "point data", ArtifactType.NETCDF),
            ("points.20230101_060000.nc", "point data", ArtifactType.NETCDF),
            ("track.20230101_000000.nc", "track data", ArtifactType.NETCDF),
            ("track.20230101_060000.nc", "track data", ArtifactType.NETCDF),
        ]

        artifacts = []
        for filename, content, artifact_type in files_to_create:
            file_path = output_dir / filename
            file_path.write_text(content)
            artifacts.append(
                Artifact(
                    path=filename,
                    artifact_type=artifact_type,
                    size_bytes=None,
                    description=None,
                    date=None,
                )
            )

        model_run_result = SimpleNamespace(
            output_dir=str(output_dir),
            artifacts=artifacts,
            timing=SimpleNamespace(
                start_time=datetime(2023, 1, 1, tzinfo=timezone.utc)
            ),
            run_id="test-run-001",
        )

        processor = WW3TransferPostprocessor()
        result = processor.process(
            model_run_result,
            destinations=[f"file://{tmp_path}/dest"],
            failure_policy="CONTINUE",
        )

        assert isinstance(result, PostprocessSuccess)
        assert result.metadata["transferred_count"] >= 1
        assert isinstance(result.artifacts, list)

        paths = [a.path for a in result.artifacts]
        assert any("restart" in p for p in paths)


class TestArtifactDateNormalization:
    def _process_with_artifact_date(self, tmp_path, artifact_date):
        output_dir = tmp_path / "ww3_output"
        output_dir.mkdir()

        artifact_file = output_dir / "ww3.20230101_000000.nc"
        artifact_file.write_text("test field data")

        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        artifacts = [
            Artifact(
                path="ww3.20230101_000000.nc",
                artifact_type=ArtifactType.NETCDF,
                size_bytes=None,
                description=None,
                date=artifact_date,
            )
        ]

        model_run_result = SimpleNamespace(
            output_dir=str(output_dir),
            artifacts=artifacts,
            timing=SimpleNamespace(
                start_time=datetime(2023, 1, 1, tzinfo=timezone.utc)
            ),
            run_id="test-run-001",
        )

        processor = WW3TransferPostprocessor()
        return processor.process(
            model_run_result,
            destinations=[f"file://{dest_dir}"],
            failure_policy="CONTINUE",
        )

    def test_basic_iso_artifact_date_succeeds(self, tmp_path):
        result = self._process_with_artifact_date(tmp_path, "2024-01-15T00:00:00")

        assert isinstance(result, PostprocessSuccess)
        assert result.metadata["transferred_count"] == 1
        assert (
            result.metadata["name_map"][
                str(tmp_path / "ww3_output" / "ww3.20230101_000000.nc")
            ]
            == "20240115_000000_ww3.20230101_000000.nc"
        )

    def test_timezone_iso_artifact_date_succeeds(self, tmp_path):
        result = self._process_with_artifact_date(tmp_path, "2024-01-15T00:00:00+00:00")

        assert isinstance(result, PostprocessSuccess)
        assert result.metadata["transferred_count"] == 1
        assert (
            result.metadata["name_map"][
                str(tmp_path / "ww3_output" / "ww3.20230101_000000.nc")
            ]
            == "20240115_000000_ww3.20230101_000000.nc"
        )

    def test_fractional_seconds_artifact_date_succeeds(self, tmp_path):
        result = self._process_with_artifact_date(
            tmp_path, "2024-01-15T00:00:00.123456"
        )

        assert isinstance(result, PostprocessSuccess)
        assert result.metadata["transferred_count"] == 1
        assert (
            result.metadata["name_map"][
                str(tmp_path / "ww3_output" / "ww3.20230101_000000.nc")
            ]
            == "20240115_000000_ww3.20230101_000000.nc"
        )

    def test_none_artifact_date_falls_back_to_timing_start_time(self, tmp_path):
        result = self._process_with_artifact_date(tmp_path, None)

        assert isinstance(result, PostprocessSuccess)
        assert result.metadata["transferred_count"] == 1
        assert (
            result.metadata["name_map"][
                str(tmp_path / "ww3_output" / "ww3.20230101_000000.nc")
            ]
            == "20230101_000000_ww3.20230101_000000.nc"
        )

    def test_restart_artifact_date_with_timezone_succeeds(self, tmp_path):
        output_dir = tmp_path / "ww3_output"
        output_dir.mkdir()

        restart_file = output_dir / "restart002.ww3"
        restart_file.write_text("test restart data")

        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        artifacts = [
            Artifact(
                path="restart002.ww3",
                artifact_type=ArtifactType.RESTART,
                size_bytes=None,
                description=None,
                date="2024-01-15T00:00:00+00:00",
            )
        ]

        restart = SimpleNamespace(stride="3600")
        output_date = SimpleNamespace(restart=restart)
        ww3_shel = SimpleNamespace(output_date=output_date)
        config = SimpleNamespace(ww3_shel=ww3_shel)

        model_run_result = SimpleNamespace(
            output_dir=str(output_dir),
            artifacts=artifacts,
            config=config,
            timing=SimpleNamespace(
                start_time=datetime(2023, 1, 1, tzinfo=timezone.utc)
            ),
            run_id="test-run-001",
        )

        processor = WW3TransferPostprocessor()
        result = processor.process(
            model_run_result,
            destinations=[f"file://{dest_dir}"],
            failure_policy="CONTINUE",
        )

        assert isinstance(result, PostprocessSuccess)
        assert result.metadata["transferred_count"] == 1
        assert (
            result.metadata["name_map"][str(tmp_path / "ww3_output" / "restart002.ww3")]
            == "20240115_010000_restart.ww3"
        )
