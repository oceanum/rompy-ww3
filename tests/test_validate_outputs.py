"""Tests for ShelConfig and MultiConfig validate_outputs / expected_artifacts."""

import pytest
from pathlib import Path
from datetime import datetime

from rompy.core.responses import ArtifactType
from rompy_ww3.config import ShelConfig
from rompy_ww3.namelists.output_type import (
    OutputType,
    OutputTypeField,
    OutputTypeRestart,
)
from rompy_ww3.namelists.output_date import (
    OutputDate,
    OutputDateRestart,
)
from rompy_ww3.namelists.domain import Domain
from rompy_ww3.namelists.field import Field
from rompy_ww3.namelists.output_file import File
from rompy_ww3.components.shel import Shel
from rompy_ww3.components.ounf import Ounf


class TestShelConfigExpectedArtifacts:
    """Tests for ShelConfig.expected_artifacts()."""

    def test_returns_config_driven_manifest(self):
        """expected_artifacts() returns artifacts from config, not empty list."""
        config = ShelConfig(
            ww3_shel=Shel(
                domain=Domain(
                    start=datetime(2026, 6, 18, 0, 0),
                    stop=datetime(2026, 6, 19, 0, 0),
                ),
                output_type=OutputType(
                    field=OutputTypeField(list="DPT HS FP DIR SPR WND"),
                    restart=OutputTypeRestart(extra="HS"),
                ),
                output_date=OutputDate(
                    restart=OutputDateRestart(stride=21600),
                ),
            ),
            ww3_ounf=Ounf(
                field=Field(samefile=True),
                file=File(prefix="ww3."),
            ),
        )

        artifacts = config.expected_artifacts()

        # Should NOT be empty — should be config-driven
        assert len(artifacts) > 0

        # Check restart artifacts
        restart_artifacts = [
            a for a in artifacts if a.artifact_type == ArtifactType.RESTART
        ]
        assert len(restart_artifacts) == 4
        restart_paths = {a.path for a in restart_artifacts}
        assert "restart001.ww3" in restart_paths
        assert "restart004.ww3" in restart_paths

        # Check field output
        field_artifacts = [
            a for a in artifacts if a.artifact_type == ArtifactType.NETCDF
        ]
        assert len(field_artifacts) == 1
        assert field_artifacts[0].path == "ww3.202606.nc"

        # Check always-present
        paths = {a.path for a in artifacts}
        assert "mod_def.ww3" in paths
        assert "log.ww3" in paths

    def test_no_restart_when_not_configured(self):
        """No restart artifacts when output_type.restart is None."""
        config = ShelConfig(
            ww3_shel=Shel(
                domain=Domain(
                    start=datetime(2026, 6, 18),
                    stop=datetime(2026, 6, 19),
                ),
                output_type=OutputType(
                    field=OutputTypeField(list="HS"),
                ),
            ),
        )

        artifacts = config.expected_artifacts()

        restart_artifacts = [
            a for a in artifacts if a.artifact_type == ArtifactType.RESTART
        ]
        assert len(restart_artifacts) == 0

    def test_no_field_when_not_configured(self):
        """No field artifacts when output_type.field is None."""
        config = ShelConfig(
            ww3_shel=Shel(
                domain=Domain(
                    start=datetime(2026, 6, 18),
                    stop=datetime(2026, 6, 19),
                ),
                output_type=OutputType(
                    restart=OutputTypeRestart(extra="HS"),
                ),
                output_date=OutputDate(
                    restart=OutputDateRestart(stride=21600),
                ),
            ),
        )

        artifacts = config.expected_artifacts()

        field_artifacts = [
            a for a in artifacts if a.artifact_type == ArtifactType.NETCDF
        ]
        assert len(field_artifacts) == 0

    def test_empty_config_returns_always_present_only(self):
        """Config with no output types returns only always-present artifacts."""
        config = ShelConfig()

        artifacts = config.expected_artifacts()

        # Should have always-present files but no restart/field
        paths = {a.path for a in artifacts}
        assert "mod_def.ww3" in paths
        assert all(a.artifact_type != ArtifactType.RESTART for a in artifacts)
        assert all(a.artifact_type != ArtifactType.NETCDF for a in artifacts)


class TestShelConfigValidateOutputs:
    """Tests for ShelConfig.validate_outputs()."""

    def test_existing_files_have_size_bytes(self, tmp_path):
        """Files that exist get size_bytes filled in."""
        # Create expected files on disk
        (tmp_path / "restart001.ww3").write_text("restart data")
        (tmp_path / "restart002.ww3").write_text("restart data" * 10)
        (tmp_path / "mod_def.ww3").write_text("mod def")
        (tmp_path / "log.ww3").write_text("log content here")

        config = ShelConfig(
            ww3_shel=Shel(
                domain=Domain(
                    start=datetime(2026, 6, 18),
                    stop=datetime(2026, 6, 19),
                ),
                output_type=OutputType(
                    restart=OutputTypeRestart(extra="HS"),
                ),
                output_date=OutputDate(
                    restart=OutputDateRestart(
                        stride=43200
                    ),  # 12h stride = 2 restart files
                ),
            ),
        )

        artifacts = config.validate_outputs(tmp_path)

        for a in artifacts:
            if Path(tmp_path / a.path).exists():
                assert a.size_bytes is not None, f"{a.path} should have size_bytes"
                assert a.size_bytes > 0

    def test_missing_file_emits_warning(self, tmp_path):
        """Missing expected files emit UserWarning."""
        # Create only some files
        (tmp_path / "restart001.ww3").write_text("data")
        # restart002.ww3 deliberately missing

        config = ShelConfig(
            ww3_shel=Shel(
                domain=Domain(
                    start=datetime(2026, 6, 18),
                    stop=datetime(2026, 6, 19),
                ),
                output_type=OutputType(
                    restart=OutputTypeRestart(extra="HS"),
                    field=OutputTypeField(list="HS"),
                ),
                output_date=OutputDate(
                    restart=OutputDateRestart(stride=43200),
                ),
            ),
        )

        with pytest.warns(UserWarning, match="Expected artifact not found"):
            artifacts = config.validate_outputs(tmp_path)

        # Should still return all expected artifacts (including missing ones)
        paths = {a.path for a in artifacts}
        assert "restart001.ww3" in paths
        assert "restart002.ww3" in paths  # included even though missing

    def test_no_base_class_warning(self, tmp_path):
        """validate_outputs should NOT emit the base-class fallback warning."""
        (tmp_path / "mod_def.ww3").write_text("dummy")

        config = ShelConfig()

        with pytest.warns(UserWarning) as record:
            config.validate_outputs(tmp_path)

        # No warning about "validate_outputs() is not implemented"
        fallback_warnings = [
            w
            for w in record
            if "validate_outputs() is not implemented" in str(w.message)
        ]
        assert len(fallback_warnings) == 0

    def test_all_present_no_warnings(self, tmp_path):
        """When all expected files exist, no warnings are emitted."""
        # Create all always-present files matching the manifest
        always_present = [
            "mod_def.ww3",
            "log.ww3",
            "ww3_grid.nml",
            "ww3_shel.nml",
            "ww3_ounf.nml",
            "namelists.nml",
            "full_ww3.sh",
            "preprocess_ww3.sh",
            "postprocess_ww3.sh",
            "run_ww3.sh",
            "ST4TABUHF2.bin",
            "mapsta.ww3",
            "mask.ww3",
            "out_grd.ww3",
        ]
        for f in always_present:
            (tmp_path / f).write_text("dummy")

        config = ShelConfig()

        import warnings

        with warnings.catch_warnings(record=True) as record:
            warnings.simplefilter("always")
            config.validate_outputs(tmp_path)

        # No "Expected artifact not found" warnings since all files exist
        missing_warnings = [
            w for w in record if "Expected artifact not found" in str(w.message)
        ]
        assert len(missing_warnings) == 0
