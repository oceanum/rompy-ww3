"""Tests for artifact inference in ShelConfig."""

from rompy_ww3.config import ShelConfig
from rompy.core.responses import ArtifactType


class TestInferArtifacts:
    def test_restart_file_inference(self, tmp_path):
        restart_file = tmp_path / "restart001.ww3"
        restart_file.write_text("restart data")

        config = ShelConfig()

        result = config.infer_artifacts(
            files=[restart_file], output_types={"restart": {"extra": "DW"}}
        )

        assert len(result) == 1
        assert result[0].artifact_type == ArtifactType.OTHER
        assert "restart" in result[0].path

    def test_restart_file_variants(self, tmp_path):
        files = [
            tmp_path / "restart.ww3",
            tmp_path / "restart001.ww3",
            tmp_path / "restart999.ww3",
        ]
        for f in files:
            f.write_text("test")

        config = ShelConfig()

        result = config.infer_artifacts(files=files, output_types={})

        assert len(result) == 3
        for artifact in result:
            assert artifact.artifact_type == ArtifactType.OTHER

    def test_field_output_enabled(self, tmp_path):
        field_file = tmp_path / "ww3.20230101_000000.nc"
        field_file.write_text("field data")

        config = ShelConfig()

        result = config.infer_artifacts(
            files=[field_file], output_types={"field": {"list": [1, 2, 3]}}
        )

        assert len(result) == 1
        assert result[0].artifact_type == ArtifactType.NETCDF

    def test_field_output_disabled(self, tmp_path):
        field_file = tmp_path / "ww3.20230101_000000.nc"
        field_file.write_text("field data")

        config = ShelConfig()

        result = config.infer_artifacts(files=[field_file], output_types={})

        assert len(result) == 1
        assert result[0].artifact_type == ArtifactType.OTHER

    def test_point_output_enabled(self, tmp_path):
        point_file = tmp_path / "points.20230101_000000.nc"
        point_file.write_text("point data")

        config = ShelConfig()

        result = config.infer_artifacts(
            files=[point_file], output_types={"point": True}
        )

        assert len(result) == 1
        assert result[0].artifact_type == ArtifactType.NETCDF

    def test_point_output_disabled(self, tmp_path):
        point_file = tmp_path / "points.20230101_000000.nc"
        point_file.write_text("point data")

        config = ShelConfig()

        result = config.infer_artifacts(files=[point_file], output_types={})

        assert len(result) == 1
        assert result[0].artifact_type == ArtifactType.OTHER

    def test_track_output_enabled(self, tmp_path):
        track_file = tmp_path / "track.20230101_000000.nc"
        track_file.write_text("track data")

        config = ShelConfig()

        result = config.infer_artifacts(
            files=[track_file], output_types={"track": True}
        )

        assert len(result) == 1
        assert result[0].artifact_type == ArtifactType.NETCDF

    def test_track_output_disabled(self, tmp_path):
        track_file = tmp_path / "track.20230101_000000.nc"
        track_file.write_text("track data")

        config = ShelConfig()

        result = config.infer_artifacts(files=[track_file], output_types={})

        assert len(result) == 1
        assert result[0].artifact_type == ArtifactType.OTHER

    def test_multiple_file_types(self, tmp_path):
        files = [
            tmp_path / "restart001.ww3",
            tmp_path / "ww3.20230101_000000.nc",
            tmp_path / "points.20230101_000000.nc",
            tmp_path / "track.20230101_000000.nc",
        ]
        for f in files:
            f.write_text("test data")

        config = ShelConfig()

        result = config.infer_artifacts(
            files=files,
            output_types={
                "field": True,
                "point": True,
                "track": True,
            },
        )

        assert len(result) == 4
        assert any(
            a.artifact_type == ArtifactType.OTHER and "restart" in a.path
            for a in result
        )
        assert any(
            a.artifact_type == ArtifactType.NETCDF and "ww3." in a.path for a in result
        )
        assert any(
            a.artifact_type == ArtifactType.NETCDF and "points." in a.path
            for a in result
        )
        assert any(
            a.artifact_type == ArtifactType.NETCDF and "track." in a.path
            for a in result
        )

    def test_empty_files_list(self):
        config = ShelConfig()

        result = config.infer_artifacts(files=[], output_types={"field": True})

        assert len(result) == 0

    def test_empty_output_types(self, tmp_path):
        files = [
            tmp_path / "restart001.ww3",
            tmp_path / "ww3.20230101_000000.nc",
            tmp_path / "points.20230101_000000.nc",
            tmp_path / "track.20230101_000000.nc",
        ]
        for f in files:
            f.write_text("test")

        config = ShelConfig()

        result = config.infer_artifacts(files=files, output_types={})

        assert len(result) == 4
        for artifact in result:
            assert artifact.artifact_type == ArtifactType.OTHER

    def test_unknown_file_type(self, tmp_path):
        files = [
            tmp_path / "spec.nc",
            tmp_path / "unknown.txt",
            tmp_path / "data.20230101.nc",
        ]
        for f in files:
            f.write_text("test")

        config = ShelConfig()

        result = config.infer_artifacts(
            files=files, output_types={"field": True, "point": True, "track": True}
        )

        assert len(result) == 3
        for artifact in result:
            assert artifact.artifact_type == ArtifactType.OTHER

    def test_nonexistent_file_size(self, tmp_path):
        nonexistent = tmp_path / "nonexistent.ww3"

        config = ShelConfig()

        result = config.infer_artifacts(files=[nonexistent], output_types={})

        assert len(result) == 1
        assert result[0].size_bytes is None

    def test_existing_file_size(self, tmp_path):
        test_file = tmp_path / "restart001.ww3"
        content = "test content"
        test_file.write_text(content)

        config = ShelConfig()

        result = config.infer_artifacts(files=[test_file], output_types={})

        assert len(result) == 1
        assert result[0].size_bytes == len(content.encode())

    def test_partial_output_types_enabled(self, tmp_path):
        files = [
            tmp_path / "ww3.20230101_000000.nc",
            tmp_path / "points.20230101_000000.nc",
            tmp_path / "track.20230101_000000.nc",
        ]
        for f in files:
            f.write_text("test")

        config = ShelConfig()

        result = config.infer_artifacts(files=files, output_types={"field": True})

        assert len(result) == 3
        assert any(
            a.artifact_type == ArtifactType.NETCDF and "ww3." in a.path for a in result
        )
        assert any(
            a.artifact_type == ArtifactType.OTHER and "points." in a.path
            for a in result
        )
        assert any(
            a.artifact_type == ArtifactType.OTHER and "track." in a.path for a in result
        )


class TestExpectedArtifacts:
    def test_expected_artifacts_returns_empty_list(self):
        config = ShelConfig()

        result = config.expected_artifacts()

        assert isinstance(result, list)
        assert len(result) == 0
