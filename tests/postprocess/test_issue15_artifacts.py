"""Issue #15 expected/observed/missing artifact contract coverage."""

from datetime import datetime, timezone
from pathlib import Path

import pytest
from rompy.core.responses import Artifact, ArtifactType

from rompy_ww3.components.multi import Multi
from rompy_ww3.components.ounf import Ounf
from rompy_ww3.components.ounp import Ounp
from rompy_ww3.components.shel import Shel
from rompy_ww3.components.trnc import Trnc
from rompy_ww3.config import MultiConfig, ShelConfig
from rompy_ww3.namelists.domain import Domain
from rompy_ww3.namelists.field import Field
from rompy_ww3.namelists.output_date import OutputDate, OutputDateRestart
from rompy_ww3.namelists.output_file import File
from rompy_ww3.namelists.output_type import (
    AllType,
    OutputType,
    OutputTypeField,
    OutputTypePoint,
    OutputTypeRestart,
    OutputTypeTrack,
)
from rompy_ww3.namelists.point import Point, PointFile
from rompy_ww3.namelists.track import Track, TrackFile


@pytest.mark.parametrize(
    ("samefile", "timesplit", "expected"),
    [
        (True, None, "nested/ww3.202301.nc"),
        (False, 8, "nested/ww3.20230101.nc"),
    ],
)
def test_shel_expected_observed_missing_matrix(tmp_path, samefile, timesplit, expected):
    """Expected paths are deterministic; validation reports truthful observations."""
    config = ShelConfig(
        ww3_shel=Shel(
            domain=Domain(
                start=datetime(2023, 1, 1, tzinfo=timezone.utc).replace(tzinfo=None),
                stop=datetime(2023, 1, 2, tzinfo=timezone.utc).replace(tzinfo=None),
            ),
            output_type=OutputType(
                field=OutputTypeField(list="HS"),
                point=OutputTypePoint(file="points.inp"),
                track=OutputTypeTrack(format=True),
                restart=OutputTypeRestart(extra="HS"),
            ),
            output_date=OutputDate(
                restart=OutputDateRestart(stride=43200),
            ),
        ),
        ww3_ounp=Ounp(
            point_nml=Point(
                timestart=datetime(2023, 1, 1, tzinfo=timezone.utc).replace(tzinfo=None),
                timestride=86400,
                timecount=2,
                timesplit=8,
                samefile=False,
            ),
            file_nml=PointFile(prefix="custom-points."),
        ),
        ww3_track=Trnc(
            track=Track(
                timestart=datetime(2023, 1, 1, tzinfo=timezone.utc).replace(tzinfo=None),
                timestride=86400,
                timecount=2,
                timesplit=8,
            ),
            file_nml=TrackFile(prefix="custom-track."),
        ),
    )
    # The configured field prefix is nested and remains staging-relative.
    config.ww3_ounf = Ounf(
        field=Field(samefile=samefile, timesplit=timesplit),
        file=File(prefix="nested/ww3."),
    )
    expected_artifacts = config.expected_artifacts()
    assert expected in {artifact.path for artifact in expected_artifacts}
    assert "custom-points.20230101.nc" in {a.path for a in expected_artifacts}
    assert "custom-track.20230101.nc" in {a.path for a in expected_artifacts}
    assert any(a.artifact_type is ArtifactType.NETCDF for a in expected_artifacts)
    assert any(a.artifact_type is ArtifactType.RESTART for a in expected_artifacts)
    assert any(a.artifact_type is ArtifactType.TEXT for a in expected_artifacts)

    # Populate one expected output and one always-present text artifact only.
    observed_path = tmp_path / expected
    observed_path.parent.mkdir(parents=True)
    observed_path.write_bytes(b"field")
    (tmp_path / "log.ww3").write_text("log")
    with pytest.warns(UserWarning):
        observed = config.validate_outputs(tmp_path)
    observed_by_path = {artifact.path: artifact for artifact in observed}
    assert observed_by_path[expected].size_bytes == 5
    assert "log.ww3" not in observed_by_path
    assert "mod_def.ww3" not in observed_by_path
    assert all(not Path(artifact.path).is_absolute() for artifact in observed)


def test_shel_expected_point_track_and_restart_types():
    config = ShelConfig(
        ww3_shel=Shel(
            domain=Domain(
                start=datetime(2023, 1, 1, tzinfo=timezone.utc).replace(tzinfo=None),
                stop=datetime(2023, 1, 2, tzinfo=timezone.utc).replace(tzinfo=None),
            ),
            output_type=OutputType(
                point=OutputTypePoint(file="points.inp"),
                track=OutputTypeTrack(format=True),
                restart=OutputTypeRestart(extra="HS"),
            ),
            output_date=OutputDate(restart=OutputDateRestart(stride=43200)),
        ),
        ww3_ounp=Ounp(
            point_nml=Point(
                timestart=datetime(2023, 1, 1, tzinfo=timezone.utc).replace(tzinfo=None),
                timestride=86400,
                timecount=2,
                samefile=True,
            )
        ),
        ww3_track=Trnc(
            track=Track(
                timestart=datetime(2023, 1, 1, tzinfo=timezone.utc).replace(tzinfo=None),
                timestride=86400,
                timecount=2,
                timesplit=6,
            )
        ),
    )
    artifacts = config.expected_artifacts()
    paths = {artifact.path: artifact.artifact_type for artifact in artifacts}
    assert paths["points.202301.nc"] is ArtifactType.NETCDF
    assert paths["track.202301.nc"] is ArtifactType.NETCDF
    assert paths["restart001.ww3"] is ArtifactType.RESTART


def test_shel_strict_track_window_does_not_use_domain_stop():
    """A split track without component count does not fabricate later periods."""
    config = ShelConfig(
        ww3_shel=Shel(
            domain=Domain(
                start=datetime(2023, 1, 1, tzinfo=timezone.utc).replace(tzinfo=None),
                stop=datetime(2023, 1, 5, tzinfo=timezone.utc).replace(tzinfo=None),
            ),
            output_type=OutputType(track=OutputTypeTrack(format=True)),
        ),
        ww3_track=Trnc(
            track=Track(
                timestart=datetime(2023, 1, 1, tzinfo=timezone.utc).replace(tzinfo=None),
                timesplit=8,
            )
        ),
    )
    paths = {artifact.path for artifact in config.expected_artifacts()}
    assert not any(path.startswith("track.") for path in paths)


def test_shel_expected_controls_match_actual_generation(tmp_path):
    from types import SimpleNamespace

    config = ShelConfig(ww3_shel=Shel())
    runtime = SimpleNamespace(staging_dir=tmp_path, period=None)
    config(runtime)
    expected_paths = {artifact.path for artifact in config.expected_artifacts()}
    generated_paths = {path.name for path in tmp_path.iterdir() if path.is_file()}
    assert expected_paths <= generated_paths
    assert "ww3_shel.nml" in expected_paths
    assert "ww3_grid.nml" not in expected_paths
    assert "ww3_ounp.nml" not in expected_paths


def test_validate_outputs_preserves_yaml_text_and_missing_evidence(tmp_path, monkeypatch):
    config = ShelConfig()
    expected = [
        Artifact(path="nested/config.yaml", artifact_type=ArtifactType.YAML),
        Artifact(path="nested/notes.txt", artifact_type=ArtifactType.TEXT),
    ]
    monkeypatch.setattr(ShelConfig, "expected_artifacts", lambda self: expected)
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested/config.yaml").write_text("yaml")
    with pytest.warns(UserWarning):
        observed = config.validate_outputs(tmp_path)
    by_path = {artifact.path: artifact for artifact in observed}
    assert by_path["nested/config.yaml"].artifact_type is ArtifactType.YAML
    assert by_path["nested/config.yaml"].size_bytes == 4
    assert by_path["nested/notes.txt"].artifact_type is ArtifactType.TEXT
    assert by_path["nested/notes.txt"].size_bytes is None


@pytest.mark.parametrize(
    "artifact_type",
    [
        ArtifactType.RESTART,
        ArtifactType.NETCDF,
        ArtifactType.YAML,
        ArtifactType.TEXT,
        ArtifactType.OTHER,
        ArtifactType.PLOT,
    ],
)
def test_expected_validate_preserves_declared_artifact_type(tmp_path, monkeypatch, artifact_type):
    config = ShelConfig()
    expected = [Artifact(path="nested/artifact", artifact_type=artifact_type)]
    monkeypatch.setattr(ShelConfig, "expected_artifacts", lambda self: expected)
    target = tmp_path / "nested/artifact"
    target.parent.mkdir()
    target.write_bytes(b"evidence")
    observed = config.validate_outputs(tmp_path)
    assert observed[0].path == "nested/artifact"
    assert observed[0].artifact_type is artifact_type
    assert observed[0].size_bytes == len(b"evidence")


def test_multiconfig_does_not_expect_unsupported_track_converter():
    """Multi has no ww3_trnc execution path, so track is not an artifact."""
    config = MultiConfig(
        multi=Multi(
            domain=Domain(
                start=datetime(2023, 1, 1, tzinfo=timezone.utc).replace(tzinfo=None),
                stop=datetime(2023, 1, 2, tzinfo=timezone.utc).replace(tzinfo=None),
            ),
            output_type=AllType(
                field=OutputTypeField(list="HS"),
                point=OutputTypePoint(file="points.inp"),
                track=OutputTypeTrack(format=True),
            ),
        ),
        grids=[],
        ounp=Ounp(
            point_nml=Point(
                timestart=datetime(2023, 1, 1, tzinfo=timezone.utc).replace(tzinfo=None),
                timestride=86400,
                timecount=2,
                samefile=True,
            ),
            file_nml=PointFile(prefix="multi-points."),
        ),
    )
    paths = {artifact.path for artifact in config.expected_artifacts()}
    assert "multi-points.202301.nc" in paths
    assert not any(path.startswith("track.") for path in paths)
    assert not any(path.startswith("multi-track.") for path in paths)


def test_multiconfig_expected_and_observed_use_same_contract(tmp_path):
    """MultiConfig does not discover files after the run and preserves missing evidence."""
    from types import SimpleNamespace

    output_type = OutputType(field=OutputTypeField(list="HS"))
    config = MultiConfig.model_construct(
        multi=SimpleNamespace(
            output_type=output_type,
            domain=Domain(
                start=datetime(2023, 1, 1, tzinfo=timezone.utc).replace(tzinfo=None),
                stop=datetime(2023, 1, 2, tzinfo=timezone.utc).replace(tzinfo=None),
            ),
            output_date=None,
        ),
        ounf=None,
        grids=[],
    )
    expected = config.expected_artifacts()
    assert "ww3.202301.nc" in {artifact.path for artifact in expected}
    (tmp_path / "ww3.202301.nc").write_text("nc")
    with pytest.warns(UserWarning):
        observed = config.validate_outputs(tmp_path)
    by_path = {artifact.path: artifact for artifact in observed}
    assert by_path["ww3.202301.nc"].size_bytes == 2
    assert "mod_def.ww3" not in by_path


def test_legacy_inference_surface_and_callers_are_absent():
    import rompy_ww3.config as config_module
    import rompy_ww3.postprocess.discovery as discovery_module

    assert not hasattr(config_module.ShelConfig, "infer_artifacts")
    assert not hasattr(config_module.MultiConfig, "infer_artifacts")
    assert not hasattr(discovery_module, "infer_artifacts_from_files")
    assert not list(Path("tests").rglob("test_artifact_inference.py"))
