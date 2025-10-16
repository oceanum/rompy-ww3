"""Tests for the enhanced Ww3Source class."""

import pytest
import tempfile
from pathlib import Path

from rompy_ww3.source import Ww3Source


def test_source_validation():
    """Test source parameter validation."""
    # Test valid source parameters
    source = Ww3Source(
        uri="/path/to/data.nc", data_type="winds", file_format="netcdf", time_step=3600
    )

    # This should not raise an exception
    assert source.data_type == "winds"
    assert source.file_format == "netcdf"
    assert source.time_step == 3600


def test_invalid_data_type():
    """Test validation of invalid data type."""
    with pytest.raises(ValueError):
        Ww3Source(uri="/path/to/data.nc", data_type="INVALID")


def test_invalid_file_format():
    """Test validation of invalid file format."""
    with pytest.raises(ValueError):
        Ww3Source(uri="/path/to/data.nc", file_format="INVALID")


def test_invalid_time_step():
    """Test validation of invalid time step."""
    with pytest.raises(ValueError, match="time_step must be positive"):
        Ww3Source(uri="/path/to/data.nc", time_step=-1)


def test_invalid_value_range():
    """Test validation of invalid value range."""
    with pytest.raises(ValueError, match="min_value must be less than max_value"):
        Ww3Source(uri="/path/to/data.nc", min_value=10.0, max_value=5.0)


def test_get_ww3_variable_name():
    """Test getting WW3 variable names."""
    source = Ww3Source(uri="/path/to/data.nc")

    # Test default mappings
    assert source.get_ww3_variable_name("u_wind") == "u10"
    assert source.get_ww3_variable_name("v_wind") == "v10"
    assert source.get_ww3_variable_name("u_current") == "uocn"
    assert source.get_ww3_variable_name("v_current") == "vocn"
    assert source.get_ww3_variable_name("sea_surface_height") == "ssh"
    assert source.get_ww3_variable_name("ice_concentration") == "aic"

    # Test custom mapping
    source_with_mapping = Ww3Source(
        uri="/path/to/data.nc", variable_mapping={"my_wind_var": "u10"}
    )
    assert source_with_mapping.get_ww3_variable_name("my_wind_var") == "u10"

    # Test unmapped variable
    assert source.get_ww3_variable_name("unknown_var") == "unknown_var"


def test_generate_source_config():
    """Test generating source configuration."""
    source = Ww3Source(
        uri="/path/to/data.nc",
        data_type="winds",
        file_format="netcdf",
        start_time="20230101 000000",
        end_time="20230107 000000",
        time_step=3600,
        variables=["u10", "v10"],
        min_value=0.0,
        max_value=50.0,
    )

    config = source.generate_source_config()

    # Check that all expected keys are present
    expected_keys = {
        "uri",
        "data_type",
        "file_format",
        "start_time",
        "end_time",
        "time_step",
        "variables",
        "min_value",
        "max_value",
    }

    assert set(config.keys()) >= expected_keys
    assert config["uri"] == "/path/to/data.nc"
    assert config["data_type"] == "winds"
    assert config["file_format"] == "netcdf"
    assert config["start_time"] == "20230101 000000"
    assert config["end_time"] == "20230107 000000"
    assert config["time_step"] == 3600
    assert config["variables"] == ["u10", "v10"]
    assert config["min_value"] == 0.0
    assert config["max_value"] == 50.0


def test_write_source_config():
    """Test writing source configuration files."""
    source = Ww3Source(
        uri="/path/to/data.nc",
        data_type="winds",
        file_format="netcdf",
        start_time="20230101 000000",
        end_time="20230107 000000",
        time_step=3600,
        variables=["u10", "v10"],
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        workdir = Path(tmpdir)
        source.write_source_config(workdir)

        # Check that file was created
        config_file = workdir / "source_config.txt"
        assert config_file.exists()

        # Check file contents
        content = config_file.read_text()
        assert "WW3 Source Configuration" in content
        assert "uri: /path/to/data.nc" in content
        assert "data_type: winds" in content
        assert "file_format: netcdf" in content
        assert "start_time: 20230101 000000" in content
        assert "end_time: 20230107 000000" in content
        assert "time_step: 3600" in content
        assert "variables: u10, v10" in content


def test_template_context():
    """Test generation of template context."""
    source = Ww3Source(
        uri="/path/to/data.nc",
        data_type="winds",
        file_format="netcdf",
        start_time="20230101 000000",
        end_time="20230107 000000",
        time_step=3600,
        variables=["u10", "v10"],
        min_value=0.0,
        max_value=50.0,
        variable_mapping={"u_wind": "u10", "v_wind": "v10"},
    )

    context = source.get_template_context()

    # Check that all expected keys are present
    expected_keys = {
        "uri",
        "data_type",
        "file_format",
        "start_time",
        "end_time",
        "time_step",
        "spatial_resolution",
        "variables",
        "min_value",
        "max_value",
        "variable_mapping",
    }

    assert set(context.keys()) >= expected_keys
    assert context["uri"] == "/path/to/data.nc"
    assert context["data_type"] == "winds"
    assert context["file_format"] == "netcdf"
    assert context["variables"] == ["u10", "v10"]
    assert context["variable_mapping"] == {"u_wind": "u10", "v_wind": "v10"}


def test_get_ww3_variable_mapping():
    """Test getting WW3 variable mapping."""
    # Test default mapping
    source = Ww3Source(uri="/path/to/data.nc")
    mapping = source.get_ww3_variable_mapping()

    assert "u_wind" in mapping
    assert mapping["u_wind"] == "u10"
    assert "v_wind" in mapping
    assert mapping["v_wind"] == "v10"

    # Test with custom mapping
    source_with_custom = Ww3Source(
        uri="/path/to/data.nc", variable_mapping={"my_var": "ww3_var"}
    )
    custom_mapping = source_with_custom.get_ww3_variable_mapping()

    assert "u_wind" in custom_mapping
    assert custom_mapping["u_wind"] == "u10"
    assert "my_var" in custom_mapping
    assert custom_mapping["my_var"] == "ww3_var"


def test_time_range_validation():
    """Test time range validation."""
    # Valid time range
    valid_source = Ww3Source(
        uri="/path/to/data.nc", start_time="20230101 000000", end_time="20230107 000000"
    )
    assert valid_source.is_time_range_valid()

    # Invalid time range
    invalid_source = Ww3Source(
        uri="/path/to/data.nc", start_time="20230107 000000", end_time="20230101 000000"
    )
    assert not invalid_source.is_time_range_valid()

    # Missing time range
    incomplete_source = Ww3Source(uri="/path/to/data.nc")
    assert not incomplete_source.is_time_range_valid()

    # Missing start time
    missing_start = Ww3Source(uri="/path/to/data.nc", end_time="20230107 000000")
    assert not missing_start.is_time_range_valid()

    # Missing end time
    missing_end = Ww3Source(uri="/path/to/data.nc", start_time="20230101 000000")
    assert not missing_end.is_time_range_valid()


if __name__ == "__main__":
    test_source_validation()
    test_invalid_data_type()
    test_invalid_file_format()
    test_invalid_time_step()
    test_invalid_value_range()
    test_get_ww3_variable_name()
    test_generate_source_config()
    test_write_source_config()
    test_template_context()
    test_get_ww3_variable_mapping()
    test_time_range_validation()
    print("All source tests passed!")
