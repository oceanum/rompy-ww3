"""Tests for WW3 output file discovery module."""

from rompy_ww3.namelists.output_type import (
    OutputType,
    OutputTypeCoupling,
    OutputTypeField,
    OutputTypePartition,
    OutputTypePoint,
    OutputTypeRestart,
    OutputTypeTrack,
)
from rompy_ww3.postprocess.discovery import (
    generate_manifest,
    parse_output_type,
)
from rompy.core.responses import ArtifactType
from pathlib import Path


def test_parse_output_type_with_field():
    """Test parsing OutputType with field configuration."""
    output_type = OutputType(field=OutputTypeField(list="HS DIR SPR"))

    result = parse_output_type(output_type)

    assert result["field"] is not None
    assert result["field"]["list"] == "HS DIR SPR"
    assert result["point"] is None
    assert result["track"] is None
    assert result["partition"] is None
    assert result["coupling"] is None
    assert result["restart"] is None


def test_parse_output_type_with_point():
    """Test parsing OutputType with point configuration."""
    output_type = OutputType(point=OutputTypePoint(file="points.txt", name="buoys"))

    result = parse_output_type(output_type)

    assert result["point"] is not None
    assert result["point"]["file"] == "points.txt"
    assert result["point"]["name"] == "buoys"
    assert result["field"] is None


def test_parse_output_type_with_track():
    """Test parsing OutputType with track configuration."""
    output_type = OutputType(track=OutputTypeTrack(format=True))

    result = parse_output_type(output_type)

    assert result["track"] is not None
    assert result["track"]["format"] is True
    assert result["field"] is None


def test_parse_output_type_with_partition():
    """Test parsing OutputType with partition configuration."""
    output_type = OutputType(
        partition=OutputTypePartition(
            x0=10, xn=100, nx=5, y0=20, yn=200, ny=10, format=False
        )
    )

    result = parse_output_type(output_type)

    assert result["partition"] is not None
    assert result["partition"]["x0"] == 10
    assert result["partition"]["xn"] == 100
    assert result["partition"]["nx"] == 5
    assert result["partition"]["y0"] == 20
    assert result["partition"]["yn"] == 200
    assert result["partition"]["ny"] == 10
    assert result["partition"]["format"] is False


def test_parse_output_type_with_coupling():
    """Test parsing OutputType with coupling configuration."""
    output_type = OutputType(
        coupling=OutputTypeCoupling(
            sent="T0M1 OCHA OHS", received="SSH CUR WND", couplet0=True
        )
    )

    result = parse_output_type(output_type)

    assert result["coupling"] is not None
    assert result["coupling"]["sent"] == "T0M1 OCHA OHS"
    assert result["coupling"]["received"] == "SSH CUR WND"
    assert result["coupling"]["couplet0"] is True


def test_parse_output_type_with_restart():
    """Test parsing OutputType with restart configuration."""
    output_type = OutputType(restart=OutputTypeRestart(extra="DW CUR"))

    result = parse_output_type(output_type)

    assert result["restart"] is not None
    assert result["restart"]["extra"] == "DW CUR"


def test_generate_manifest_restart_configured(tmp_path):
    """Test generate_manifest calculates restart files from timing parameters."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    config = {"restart": {"extra": "DW"}}
    start_date = "20230101 000000"
    stop_date = "20230101 120000"
    output_stride = 21600

    result = generate_manifest(
        output_dir,
        config,
        start_date,
        stop_date,
        output_stride,
        include_always_present=False,
    )

    # Now returns List[Artifact], not List[Path]
    assert len(result) == 2
    paths = {a.path for a in result}
    assert "restart001.ww3" in paths
    assert "restart002.ww3" in paths
    assert all(a.artifact_type == ArtifactType.RESTART for a in result)


def test_generate_manifest_no_restart():
    """Test generate_manifest returns empty list when restart is not configured."""
    config = {}
    result = generate_manifest(
        Path("/out"),
        config,
        "20230101 000000",
        "20230102 000000",
        3600,
        include_always_present=False,
    )
    assert len(result) == 0


def test_parse_output_type_with_multiple_types():
    """Test parsing OutputType with multiple output types configured."""
    output_type = OutputType(
        field=OutputTypeField(list="HS DIR"),
        point=OutputTypePoint(file="points.txt"),
        restart=OutputTypeRestart(extra="DW"),
    )

    result = parse_output_type(output_type)

    assert result["field"] is not None
    assert result["field"]["list"] == "HS DIR"
    assert result["point"] is not None
    assert result["point"]["file"] == "points.txt"
    assert result["restart"] is not None
    assert result["restart"]["extra"] == "DW"
    assert result["track"] is None
    assert result["partition"] is None
    assert result["coupling"] is None


def test_parse_output_type_empty():
    """Test parsing empty OutputType with no configured outputs."""
    output_type = OutputType()

    result = parse_output_type(output_type)

    assert result["field"] is None
    assert result["point"] is None
    assert result["track"] is None
    assert result["partition"] is None
    assert result["coupling"] is None
    assert result["restart"] is None


def test_parse_output_type_with_all_types():
    """Test parsing OutputType with all output types configured."""
    output_type = OutputType(
        field=OutputTypeField(list="HS DIR SPR"),
        point=OutputTypePoint(file="points.txt", name="buoys"),
        track=OutputTypeTrack(format=True),
        partition=OutputTypePartition(x0=0, xn=100, nx=10, y0=0, yn=100, ny=10),
        coupling=OutputTypeCoupling(sent="HS", received="WND"),
        restart=OutputTypeRestart(extra="DW CUR"),
    )

    result = parse_output_type(output_type)

    assert result["field"] is not None
    assert result["point"] is not None
    assert result["track"] is not None
    assert result["partition"] is not None
    assert result["coupling"] is not None
    assert result["restart"] is not None


def test_generate_manifest_field_output_samefile(tmp_path):
    """Test generate_manifest predicts single NetCDF when samefile=True."""
    config = {"field": {"list": "HS DIR"}}
    start_date = "20260618 000000"
    stop_date = "20260619 000000"

    result = generate_manifest(
        Path("."),
        config,
        start_date=start_date,
        stop_date=stop_date,
        field_samefile=True,
        field_prefix="ww3.",
        include_always_present=False,
    )

    assert len(result) == 1
    assert result[0].path == "ww3.202606.nc"
    assert result[0].artifact_type == ArtifactType.NETCDF


def test_generate_manifest_always_present():
    """Test generate_manifest includes always-present artifacts."""
    config = {}

    result = generate_manifest(
        Path("."),
        config,
        include_always_present=True,
    )

    paths = {a.path for a in result}
    assert "mod_def.ww3" in paths
    assert "log.ww3" in paths
    assert "ww3_grid.nml" in paths
    assert "full_ww3.sh" in paths
    # Check types
    mod_def = next(a for a in result if a.path == "mod_def.ww3")
    assert mod_def.artifact_type == ArtifactType.OTHER
    log = next(a for a in result if a.path == "log.ww3")
    assert log.artifact_type == ArtifactType.TEXT


def test_generate_manifest_no_field_when_not_configured():
    """Test generate_manifest skips field output when not in config."""
    config = {"restart": {"extra": "DW"}}
    start_date = "20260618 000000"
    stop_date = "20260619 000000"

    result = generate_manifest(
        Path("."),
        config,
        start_date=start_date,
        stop_date=stop_date,
        output_stride=21600,
        include_always_present=False,
    )

    # Only restart files, no field files
    paths = {a.path for a in result}
    assert all(p.startswith("restart") for p in paths)


def test_generate_manifest_field_outputs_empty(tmp_path):
    """Test generate_manifest returns empty for field-only when include_always_present=False."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    config = {"field": {"list": "HS DIR"}}
    start_date = "20230101 000000"
    stop_date = "20230101 120000"

    result = generate_manifest(
        output_dir,
        config,
        start_date,
        stop_date,
        include_always_present=False,
    )

    # Field outputs with samefile=True should produce one file
    assert len(result) == 1
    assert result[0].path == "ww3.202301.nc"
    assert result[0].artifact_type == ArtifactType.NETCDF


def test_generate_manifest_point_outputs_empty(tmp_path):
    """Test generate_manifest skips point output (not implemented for point yet)."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    config = {"point": {"file": "points.txt", "name": "buoys"}}
    start_date = "20230101 000000"
    stop_date = "20230101 120000"

    result = generate_manifest(
        output_dir,
        config,
        start_date,
        stop_date,
        include_always_present=False,
    )

    # Point output prediction not yet implemented — manifest empty
    assert len(result) == 0


def test_generate_manifest_track_outputs_empty(tmp_path):
    """Test generate_manifest skips track output (not implemented for track yet)."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    config = {"track": {"format": True}}
    start_date = "20230101 000000"
    stop_date = "20230101 120000"

    result = generate_manifest(
        output_dir,
        config,
        start_date,
        stop_date,
        include_always_present=False,
    )

    # Track output prediction not yet implemented — manifest empty
    assert len(result) == 0


def test_generate_manifest_always_present_no_duplicates():
    """Test always-present artifacts are not duplicated."""
    config = {"restart": {"extra": "DW"}}
    start_date = "20260618 000000"
    stop_date = "20260619 000000"
    output_stride = 21600

    result = generate_manifest(
        Path("."),
        config,
        start_date=start_date,
        stop_date=stop_date,
        output_stride=output_stride,
        include_always_present=True,
    )

    # Should include 4 restarts + always-present files
    paths = [a.path for a in result]
    # No duplicates
    assert len(paths) == len(set(paths))
    # Restart files present
    assert "restart001.ww3" in paths
    assert "restart004.ww3" in paths
