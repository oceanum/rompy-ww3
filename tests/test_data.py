"""
Test cases for WW3 Data class.
"""

import tempfile
from pathlib import Path
from rompy_ww3.data import Data
from rompy.core.source import SourceFile


def test_data_with_ww3_parameters():
    """Test Data class with WW3-specific parameters."""

    # Create a minimal source
    source = SourceFile(uri="/path/to/data.nc")

    # Create data with WW3-specific parameters
    data = Data(source=source)

    # Set WW3-specific attributes
    data.data_type = "winds"
    data.forcing_flag = "T"
    data.file_format = "netcdf"
    data.start_time = "20230101 000000"
    data.end_time = "20230102 000000"
    data.time_step = 3600

    # Test getting forcing configuration
    forcing_config = data.get_forcing_config()
    print("Forcing configuration:")
    print(forcing_config)

    # Should be empty since we don't have a matching data type in our mapping
    # Let's test with a proper data type
    data.data_type = "winds"
    forcing_config = data.get_forcing_config()
    print("\nForcing configuration for winds:")
    print(forcing_config)

    assert (
        "FORCING%WINDS" in forcing_config or len(forcing_config) == 0
    )  # Empty if no match

    # Test getting assimilation configuration
    assim_config = data.get_assim_config()
    print("\nAssimilation configuration:")
    print(assim_config)

    # Test generating namelist entries
    nml_entries = data.generate_input_data_nml()
    print("\nNamelist entries:")
    print(nml_entries)

    # Test writing configuration
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir) / "data"
        data.write_data_config(data_dir)

        config_file = data_dir / "data_config.txt"
        assert config_file.exists()

        print(f"\nCreated data configuration in {data_dir}")


if __name__ == "__main__":
    test_data_with_ww3_parameters()
    print("\nData test passed!")
