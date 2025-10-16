"""Tests for the enhanced Data class."""

import pytest
import tempfile
from pathlib import Path

from rompy_ww3.data import Data
from rompy.core.source import SourceFile


def test_data_validation():
    """Test data parameter validation."""
    # Test valid data parameters
    source = SourceFile(uri="/path/to/data.nc")
    data = Data(
        source=source,
        data_type="winds",
        forcing_flag="T",
        assim_flag="F",
        file_format="netcdf",
    )

    # This should not raise an exception
    assert data.data_type == "winds"
    assert data.forcing_flag == "T"
    assert data.assim_flag == "F"
    assert data.file_format == "netcdf"


def test_invalid_forcing_flag():
    """Test validation of invalid forcing flag."""
    source = SourceFile(uri="/path/to/data.nc")
    with pytest.raises(ValueError, match="forcing_flag must be one of"):
        Data(source=source, forcing_flag="INVALID")


def test_invalid_assim_flag():
    """Test validation of invalid assimilation flag."""
    source = SourceFile(uri="/path/to/data.nc")
    with pytest.raises(ValueError, match="assim_flag must be one of"):
        Data(source=source, assim_flag="INVALID")


def test_invalid_data_type():
    """Test validation of invalid data type."""
    source = SourceFile(uri="/path/to/data.nc")
    with pytest.raises(ValueError):
        Data(source=source, data_type="INVALID")


def test_invalid_file_format():
    """Test validation of invalid file format."""
    source = SourceFile(uri="/path/to/data.nc")
    with pytest.raises(ValueError):
        Data(source=source, file_format="INVALID")


def test_invalid_time_step():
    """Test validation of invalid time step."""
    source = SourceFile(uri="/path/to/data.nc")
    with pytest.raises(ValueError, match="time_step must be positive"):
        Data(source=source, time_step=-1)


def test_get_forcing_config():
    """Test getting forcing configuration."""
    source = SourceFile(uri="/path/to/data.nc")
    data = Data(source=source, data_type="winds", forcing_flag="T")

    config = data.get_forcing_config()
    assert "FORCING%WINDS" in config
    assert config["FORCING%WINDS"] == "T"


def test_get_assim_config():
    """Test getting assimilation configuration."""
    source = SourceFile(uri="/path/to/data.nc")
    data = Data(source=source, data_type="spectra", assim_flag="T")

    config = data.get_assim_config()
    assert "ASSIM%SPEC2D" in config
    assert config["ASSIM%SPEC2D"] == "T"


def test_generate_input_data_nml():
    """Test generating input data namelist."""
    source = SourceFile(uri="/path/to/data.nc")
    data = Data(source=source, data_type="winds", forcing_flag="T", assim_flag="F")

    nml_content = data.generate_input_data_nml()
    assert "INPUT%FORCING%WINDS" in nml_content
    assert "INPUT%ASSIM%" not in nml_content  # No assim config for winds


def test_write_data_config():
    """Test writing data configuration files."""
    source = SourceFile(uri="/path/to/data.nc")
    data = Data(
        source=source,
        data_type="winds",
        forcing_flag="T",
        file_format="netcdf",
        start_time="20230101 000000",
        end_time="20230107 000000",
        time_step=3600,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        workdir = Path(tmpdir)
        data.write_data_config(workdir)

        # Check that file was created
        config_file = workdir / "data_config.txt"
        assert config_file.exists()

        # Check file contents
        content = config_file.read_text()
        assert "WW3 Data Configuration" in content
        assert "Data Type: winds" in content
        assert "Forcing Flag: T" in content
        assert "File Format: netcdf" in content
        assert "Start Time: 20230101 000000" in content
        assert "End Time: 20230107 000000" in content
        assert "Time Step: 3600" in content


def test_template_context():
    """Test generation of template context."""
    source = SourceFile(uri="/path/to/data.nc")
    data = Data(
        source=source,
        data_type="winds",
        forcing_flag="T",
        file_format="netcdf",
        start_time="20230101 000000",
        end_time="20230107 000000",
        time_step=3600,
        homogeneous_values=[10.0, 90.0],
        variable_mapping={"u_wind": "u10", "v_wind": "v10"},
    )

    context = data.get_template_context()

    # Check that all expected keys are present
    expected_keys = {
        "data_type",
        "forcing_flag",
        "assim_flag",
        "file_format",
        "start_time",
        "end_time",
        "time_step",
        "homogeneous_values",
        "variable_mapping",
        "forcing_config",
        "assim_config",
    }

    assert set(context.keys()) >= expected_keys
    assert context["data_type"] == "winds"
    assert context["forcing_flag"] == "T"
    assert context["homogeneous_values"] == [10.0, 90.0]
    assert context["variable_mapping"] == {"u_wind": "u10", "v_wind": "v10"}


def test_data_type_checks():
    """Test data type checking methods."""
    source = SourceFile(uri="/path/to/data.nc")

    # Test homogeneous data
    homogeneous_data = Data(source=source, forcing_flag="H")
    assert homogeneous_data.is_homogeneous()
    assert not homogeneous_data.is_from_file()
    assert not homogeneous_data.is_coupled()
    assert not homogeneous_data.is_disabled()

    # Test file data
    file_data = Data(source=source, forcing_flag="T")
    assert not file_data.is_homogeneous()
    assert file_data.is_from_file()
    assert not file_data.is_coupled()
    assert not file_data.is_disabled()

    # Test coupled data
    coupled_data = Data(source=source, forcing_flag="C")
    assert not coupled_data.is_homogeneous()
    assert not coupled_data.is_from_file()
    assert coupled_data.is_coupled()
    assert not coupled_data.is_disabled()

    # Test disabled data
    disabled_data = Data(source=source, forcing_flag="F")
    assert not disabled_data.is_homogeneous()
    assert not disabled_data.is_from_file()
    assert not disabled_data.is_coupled()
    assert disabled_data.is_disabled()


if __name__ == "__main__":
    test_data_validation()
    test_invalid_forcing_flag()
    test_invalid_assim_flag()
    test_invalid_data_type()
    test_invalid_file_format()
    test_invalid_time_step()
    test_get_forcing_config()
    test_get_assim_config()
    test_generate_input_data_nml()
    test_write_data_config()
    test_template_context()
    test_data_type_checks()
    print("All data tests passed!")
