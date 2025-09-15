"""
Test cases for WW3 Ww3Source class.
"""

import tempfile
from pathlib import Path
from rompy_ww3.source import Ww3Source


def test_ww3_source_with_parameters():
    """Test Ww3Source class with WW3-specific parameters."""
    
    # Create a source with WW3-specific parameters
    source = Ww3Source(
        uri="/path/to/wind_data.nc",
        data_type="winds",
        file_format="netcdf",
        start_time="20230101 000000",
        end_time="20230102 000000",
        time_step=3600,
        spatial_resolution="0.1 degrees",
        variable_mapping={
            "wind_u": "u10",
            "wind_v": "v10"
        }
    )
    
    # Test string representation
    source_str = str(source)
    print("Source string representation:")
    print(source_str)
    
    assert "Ww3Source" in source_str
    assert "wind_data.nc" in source_str
    
    # Test variable mapping
    u_var = source.get_ww3_variable_name("wind_u")
    v_var = source.get_ww3_variable_name("wind_v")
    unknown_var = source.get_ww3_variable_name("unknown_var")
    
    print(f"\nVariable mapping:")
    print(f"wind_u -> {u_var}")
    print(f"wind_v -> {v_var}")
    print(f"unknown_var -> {unknown_var}")
    
    assert u_var == "u10"
    assert v_var == "v10"
    assert unknown_var == "unknown_var"
    
    # Test configuration generation
    config = source.generate_source_config()
    print(f"\nSource configuration:")
    print(config)
    
    assert config["uri"] == "/path/to/wind_data.nc"
    assert config["data_type"] == "winds"
    assert config["file_format"] == "netcdf"
    
    # Test writing configuration
    with tempfile.TemporaryDirectory() as tmpdir:
        source_dir = Path(tmpdir) / "source"
        source.write_source_config(source_dir)
        
        config_file = source_dir / "source_config.txt"
        assert config_file.exists()
        
        print(f"\nCreated source configuration in {source_dir}")


if __name__ == "__main__":
    test_ww3_source_with_parameters()
    print("\nWw3Source test passed!")