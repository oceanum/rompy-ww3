"""Tests for WW3 point output component and namelists."""

import pytest
from rompy_ww3.components.ounp import Ounp
from rompy_ww3.namelists.point import Point, PointFile
from rompy_ww3.namelists.spectra import Spectra
from rompy_ww3.namelists.param import Param
from rompy_ww3.namelists.source import Source


def test_point_nml():
    """Test POINT_NML namelist creation."""
    point = Point(
        timestart="20100101 000000",
        timestride=3600,
        type=1,
        list="all",
        samefile=True,
        buffer=150,
    )
    content = point.render()
    assert "&POINT_NML" in content
    assert "POINT%TIMESTART = '20100101 000000'" in content
    assert "POINT%TIMESTRIDE = 3600" in content
    assert "POINT%TYPE = 1" in content
    assert "/" in content


def test_point_file_nml():
    """Test FILE_NML namelist for point output."""
    file_nml = PointFile(netcdf=4)
    content = file_nml.render()
    assert "&FILE_NML" in content
    assert "FILE%NETCDF = 4" in content
    assert "/" in content


def test_spectra_nml():
    """Test SPECTRA_NML namelist."""
    spectra = Spectra(output=3, scale_fac=1)
    content = spectra.render()
    assert "&SPECTRA_NML" in content
    assert "SPECTRA%OUTPUT = 3" in content
    assert "SPECTRA%SCALE_FAC = 1" in content
    assert "/" in content


def test_param_nml():
    """Test PARAM_NML namelist."""
    param = Param(output=4)
    content = param.render()
    assert "&PARAM_NML" in content
    assert "PARAM%OUTPUT = 4" in content
    assert "/" in content


def test_source_nml():
    """Test SOURCE_NML namelist."""
    source = Source(output=4, spectrum=True, input=True)
    content = source.render()
    assert "&SOURCE_NML" in content
    assert "SOURCE%OUTPUT = 4" in content
    assert "SOURCE%SPECTRUM = T" in content
    assert "SOURCE%INPUT = T" in content
    assert "/" in content


def test_ounp_component():
    """Test Ounp component with all sub-namelists directly."""
    ounp = Ounp(
        point_nml=Point(timestart="20100101 000000", timestride=3600),
        file_nml=PointFile(netcdf=4),
        spectra_nml=Spectra(output=3),
        param_nml=Param(output=4),
        source_nml=Source(output=4, spectrum=True),
    )

    assert ounp.point_nml is not None
    assert ounp.file_nml is not None
    assert ounp.spectra_nml is not None
    assert ounp.param_nml is not None
    assert ounp.source_nml is not None


def test_ounp_component_render():
    """Test that Ounp component can render all namelist sections."""
    ounp = Ounp(
        point_nml=Point(timestart="20100101 000000", timestride=3600),
        file_nml=PointFile(netcdf=4),
        spectra_nml=Spectra(output=3),
        param_nml=Param(output=4),
        source_nml=Source(output=4),
    )

    # Test that we can render each component
    point_content = ounp.point_nml.render()
    file_content = ounp.file_nml.render()
    spectra_content = ounp.spectra_nml.render()
    param_content = ounp.param_nml.render()
    source_content = ounp.source_nml.render()

    assert "&POINT_NML" in point_content
    assert "&FILE_NML" in file_content
    assert "&SPECTRA_NML" in spectra_content
    assert "&PARAM_NML" in param_content
    assert "&SOURCE_NML" in source_content


if __name__ == "__main__":
    pytest.main([__file__])
