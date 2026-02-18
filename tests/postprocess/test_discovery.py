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


def test_generate_manifest_restart_configured():
    """Test generate_manifest returns restart file when restart is configured."""
    config = {"restart": {"extra": "DW"}}
    result = generate_manifest(Path("/out"), config)
    assert Path("/out/restart.ww3") in result


def test_generate_manifest_no_restart():
    """Test generate_manifest returns empty list when restart is not configured."""
    config = {}
    result = generate_manifest(Path("/out"), config)
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
