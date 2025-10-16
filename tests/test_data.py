"""Tests for WW3 Data object."""

import pytest
from pathlib import Path
import tempfile
import xarray as xr
import numpy as np

from rompy_ww3.data import Data
from rompy.core.source import SourceFile


def create_test_dataset():
    """Create a simple test dataset."""
    time = np.array(["2023-01-01", "2023-01-02", "2023-01-03"], dtype="datetime64")
    lon = np.linspace(0, 10, 5)
    lat = np.linspace(40, 50, 5)

    # Create sample wind data
    uwnd = np.random.random((3, 5, 5)) * 10  # 3 time steps, 5x5 grid
    vwnd = np.random.random((3, 5, 5)) * 10  # 3 time steps, 5x5 grid

    ds = xr.Dataset(
        {
            "UWND": (["time", "lat", "lon"], uwnd),
            "VWND": (["time", "lat", "lon"], vwnd),
        },
        coords={
            "time": time,
            "lon": lon,
            "lat": lat,
        },
    )

    return ds


class TestData:
    """Test WW3 Data class functionality."""

    def test_data_creation_basic(self):
        """Test basic data creation with required parameters."""
        # Create a temporary file to use as source data
        with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tmp_file:
            ds = create_test_dataset()
            ds.to_netcdf(tmp_file.name)
            source_file = SourceFile(uri=tmp_file.name)

            data = Data(
                source=source_file,
                data_type="winds",
                forcing_flag="T",
                start_time="20230101 000000",
                end_time="20230103 000000",
                grid_type="latlon",
                input_filename="input.nc",
            )

            assert data.data_type == "winds"
            assert data.forcing_flag == "T"
            assert data.start_time == "20230101 000000"
            assert data.end_time == "20230103 000000"
            assert data.grid_type == "latlon"
            assert data.input_filename == "input.nc"

    def test_data_validation(self):
        """Test data parameter validation."""
        with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tmp_file:
            ds = create_test_dataset()
            ds.to_netcdf(tmp_file.name)
            source_file = SourceFile(uri=tmp_file.name)

            # Test valid forcing flag
            data = Data(
                source=source_file,
                data_type="winds",
                forcing_flag="T",
                start_time="20230101 000000",
                end_time="20230103 000000",
                grid_type="latlon",
            )
            # Validation should pass without exception
            data.validate_data_parameters()

            # Test invalid forcing flag
            with pytest.raises(ValueError, match="forcing_flag must be one of"):
                Data(
                    source=source_file,
                    data_type="winds",
                    forcing_flag="X",
                    start_time="20230101 000000",
                    end_time="20230103 000000",
                    grid_type="latlon",
                )

            # Test invalid data type
            with pytest.raises(ValueError, match="data_type must be one of"):
                Data(
                    source=source_file,
                    data_type="invalid_type",
                    forcing_flag="T",
                    start_time="20230101 000000",
                    end_time="20230103 000000",
                    grid_type="latlon",
                )

            # Test invalid grid type
            with pytest.raises(ValueError, match="grid_type must be"):
                Data(
                    source=source_file,
                    data_type="winds",
                    forcing_flag="T",
                    start_time="20230101 000000",
                    end_time="20230103 000000",
                    grid_type="invalid_grid",
                )

    def test_data_validation_file_format(self):
        """Test file format validation."""
        with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tmp_file:
            ds = create_test_dataset()
            ds.to_netcdf(tmp_file.name)
            source_file = SourceFile(uri=tmp_file.name)

            with pytest.raises(
                ValueError, match="Currently only netcdf format is supported"
            ):
                Data(
                    source=source_file,
                    data_type="winds",
                    forcing_flag="T",
                    file_format="invalid_format",
                    start_time="20230101 000000",
                    end_time="20230103 000000",
                    grid_type="latlon",
                )

    def test_data_validation_time_step(self):
        """Test time step validation."""
        with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tmp_file:
            ds = create_test_dataset()
            ds.to_netcdf(tmp_file.name)
            source_file = SourceFile(uri=tmp_file.name)

            with pytest.raises(ValueError, match="time_step must be positive"):
                Data(
                    source=source_file,
                    data_type="winds",
                    forcing_flag="T",
                    time_step=-1,
                    start_time="20230101 000000",
                    end_time="20230103 000000",
                    grid_type="latlon",
                )

    def test_get_forcing_config(self):
        """Test getting forcing configuration."""
        with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tmp_file:
            ds = create_test_dataset()
            ds.to_netcdf(tmp_file.name)
            source_file = SourceFile(uri=tmp_file.name)

        data = Data(
            source=source_file,
            data_type="winds",
            forcing_flag="T",
            start_time="20230101 000000",
            end_time="20230103 000000",
            grid_type="latlon",
        )

        config = data.get_forcing_config()
        assert "FORCING%WINDS" in config
        assert config["FORCING%WINDS"] == "T"

        data2 = Data(
            source=source_file,
            data_type="currents",
            forcing_flag="F",  # Disabled
            start_time="20230101 000000",
            end_time="20230103 000000",
            grid_type="latlon",
        )

        config2 = data2.get_forcing_config()
        assert "FORCING%CURRENTS" in config2
        assert config2["FORCING%CURRENTS"] == "F"

    def test_get_assim_config(self):
        """Test getting assimilation configuration."""
        with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tmp_file:
            ds = create_test_dataset()
            ds.to_netcdf(tmp_file.name)
            source_file = SourceFile(uri=tmp_file.name)

        data = Data(
            source=source_file,
            data_type="spectra",
            assim_flag="T",
            start_time="20230101 000000",
            end_time="20230103 000000",
            grid_type="latlon",
        )

        config = data.get_assim_config()
        assert "ASSIM%SPEC2D" in config
        assert config["ASSIM%SPEC2D"] == "T"

        data2 = Data(
            source=source_file,
            data_type="mean",
            assim_flag="F",
            start_time="20230101 000000",
            end_time="20230103 000000",
            grid_type="latlon",
        )

        config2 = data2.get_assim_config()
        assert "ASSIM%MEAN" in config2
        assert config2["ASSIM%MEAN"] == "F"

    def test_generate_input_data_nml(self):
        """Test generating input data nml string."""
        with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tmp_file:
            ds = create_test_dataset()
            ds.to_netcdf(tmp_file.name)
            source_file = SourceFile(uri=tmp_file.name)

        data = Data(
            source=source_file,
            data_type="winds",
            forcing_flag="T",
            assim_flag="F",
            start_time="20230101 000000",
            end_time="20230103 000000",
            grid_type="latlon",
        )

        nml_str = data.generate_input_data_nml()
        assert "INPUT%FORCING%WINDS" in nml_str
        assert "'T'" in nml_str
        assert "INPUT%ASSIM" not in nml_str  # Since data_type is not assim type

    def test_write_data_config(self, tmp_path):
        """Test writing data configuration."""
        with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tmp_file:
            ds = create_test_dataset()
            ds.to_netcdf(tmp_file.name)
            source_file = SourceFile(uri=tmp_file.name)

        data = Data(
            source=source_file,
            data_type="winds",
            forcing_flag="T",
            start_time="20230101 000000",
            end_time="20230103 000000",
            grid_type="latlon",
            homogeneous_values=[10.0, 5.0],
        )

        workdir = tmp_path / "workdir"
        data.write_data_config(workdir)

        config_file = workdir / "data_config.txt"
        assert config_file.exists()

        content = config_file.read_text()
        assert "Data Type: winds" in content
        assert "Forcing Flag: T" in content
        assert "Start Time: 20230101 000000" in content
        assert "End Time: 20230103 000000" in content
        assert "Homogeneous Values: [10.0, 5.0]" in content

    def test_get_template_context(self):
        """Test getting template context."""
        with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tmp_file:
            ds = create_test_dataset()
            ds.to_netcdf(tmp_file.name)
            source_file = SourceFile(uri=tmp_file.name)

        data = Data(
            source=source_file,
            data_type="winds",
            forcing_flag="T",
            start_time="20230101 000000",
            end_time="20230103 000000",
            grid_type="latlon",
            homogeneous_values=[10.0, 5.0],
        )

        context = data.get_template_context()
        assert context["data_type"] == "winds"
        assert context["forcing_flag"] == "T"
        assert context["start_time"] == "20230101 000000"
        assert context["end_time"] == "20230103 000000"
        assert context["grid_type"] == "latlon"
        assert context["homogeneous_values"] == [10.0, 5.0]

    def test_flag_methods(self):
        """Test flag checking methods."""
        with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tmp_file:
            ds = create_test_dataset()
            ds.to_netcdf(tmp_file.name)
            source_file = SourceFile(uri=tmp_file.name)

        data_h = Data(
            source=source_file,
            data_type="winds",
            forcing_flag="H",
            start_time="20230101 000000",
            end_time="20230103 000000",
            grid_type="latlon",
        )

        data_t = Data(
            source=source_file,
            data_type="winds",
            forcing_flag="T",
            start_time="20230101 000000",
            end_time="20230103 000000",
            grid_type="latlon",
        )

        data_c = Data(
            source=source_file,
            data_type="winds",
            forcing_flag="C",
            start_time="20230101 000000",
            end_time="20230103 000000",
            grid_type="latlon",
        )

        data_f = Data(
            source=source_file,
            data_type="winds",
            forcing_flag="F",
            start_time="20230101 000000",
            end_time="20230103 000000",
            grid_type="latlon",
        )

        assert data_h.is_homogeneous()
        assert data_t.is_from_file()
        assert data_c.is_coupled()
        assert data_f.is_disabled()

    def test_get_forcing_nml(self):
        """Test getting Forcing namelist object."""
        with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tmp_file:
            ds = create_test_dataset()
            ds.to_netcdf(tmp_file.name)
            source_file = SourceFile(uri=tmp_file.name)

        data = Data(
            source=source_file,
            data_type="winds",
            forcing_flag="T",
            start_time="20230101 000000",
            end_time="20230103 000000",
            grid_type="latlon",
        )

        nml = data.get_forcing_nml()
        assert nml.timestart == "20230101 000000"
        assert nml.timestop == "20230103 000000"
        assert nml.field is not None
        assert nml.field.winds is True
        assert nml.grid is not None
        assert nml.grid.latlon is True

    def test_write_namelist(self, tmp_path):
        """Test writing namelist file."""
        with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tmp_file:
            ds = create_test_dataset()
            ds.to_netcdf(tmp_file.name)
            source_file = SourceFile(uri=tmp_file.name)

        data = Data(
            source=source_file,
            data_type="winds",
            forcing_flag="T",
            start_time="20230101 000000",
            end_time="20230103 000000",
            grid_type="latlon",
            input_filename="input.nc",
        )

        nml_file = tmp_path / "test.nml"
        data.write_namelist(nml_file)

        assert nml_file.exists()
        content = nml_file.read_text()
        assert "&FORCING_NML" in content
        assert "FORCING%TIMESTART = '20230101 000000'" in content
        assert "FORCING%TIMESTOP = '20230103 000000'" in content
        assert "FORCING%FIELD%WINDS = T" in content  # Boolean rendered as T
        assert "FORCING%GRID%LATLON = T" in content  # Boolean rendered as T
        assert "&FILE_NML" in content
        assert "FILE%FILENAME = 'input.nc'" in content
        assert "FILE%VAR(1) = 'UWND'" in content
        assert "FILE%VAR(2) = 'VWND'" in content  # Winds have 2 components

    def test_write_namelist_with_variable_mapping(self, tmp_path):
        """Test writing namelist file with custom variable mapping."""
        with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tmp_file:
            ds = create_test_dataset()
            ds.to_netcdf(tmp_file.name)
            source_file = SourceFile(uri=tmp_file.name)

        data = Data(
            source=source_file,
            data_type="winds",
            forcing_flag="T",
            start_time="20230101 000000",
            end_time="20230103 000000",
            grid_type="latlon",
            input_filename="input.nc",
            variable_mapping={"VAR(1)": "U10", "VAR(2)": "V10"},
        )

        nml_file = tmp_path / "test.nml"
        data.write_namelist(nml_file)

        assert nml_file.exists()
        content = nml_file.read_text()
        assert "FILE%VAR(1) = 'U10'" in content
        assert "FILE%VAR(2) = 'V10'" in content
        # Should not have default mappings
        assert "FILE%VAR(1) = 'UWND'" not in content

    def test_get_method_with_source(self, tmp_path):
        """Test the get method with a source."""
        # Create a test dataset file
        ds = create_test_dataset()
        source_file = tmp_path / "source.nc"
        ds.to_netcdf(source_file)

        source_obj = SourceFile(uri=str(source_file))

        data = Data(
            source=source_obj,
            data_type="winds",
            forcing_flag="T",
            start_time="20230101 000000",
            end_time="20230103 000000",
            grid_type="latlon",
            input_filename="input.nc",
        )

        # Test the get method
        with tempfile.TemporaryDirectory() as temp_dir:
            dest_dir = Path(temp_dir)
            data.get(dest_dir)

            # Check that the processed file was created
            expected_file = dest_dir / "input.nc"
            assert expected_file.exists()

            # Check that the namelist file was created
            nml_file = dest_dir / "ww3_prnc.nml"
            assert nml_file.exists()

    def test_get_method_homogeneous(self, tmp_path):
        """Test the get method with homogeneous forcing."""
        with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tmp_file:
            ds = create_test_dataset()
            ds.to_netcdf(tmp_file.name)
            source_file = SourceFile(uri=tmp_file.name)

        data = Data(
            source=source_file,
            data_type="winds",
            forcing_flag="H",  # Homogeneous
            start_time="20230101 000000",
            end_time="20230103 000000",
            grid_type="latlon",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            dest_dir = Path(temp_dir)
            result = data.get(dest_dir)

            # Should return homogeneous_data path
            assert result.name == "homogeneous_data"

            # Should not create a namelist file in this case
            nml_file = dest_dir / "ww3_prnc.nml"
            assert not nml_file.exists()

    def test_get_method_disabled(self, tmp_path):
        """Test the get method with disabled forcing."""
        with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tmp_file:
            ds = create_test_dataset()
            ds.to_netcdf(tmp_file.name)
            source_file = SourceFile(uri=tmp_file.name)

        data = Data(
            source=source_file,
            data_type="winds",
            forcing_flag="F",  # Disabled
            start_time="20230101 000000",
            end_time="20230103 000000",
            grid_type="latlon",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            dest_dir = Path(temp_dir)
            result = data.get(dest_dir)

            # Should return no_processing_needed path
            assert result.name == "no_processing_needed"

            # Should not create a namelist file in this case
            nml_file = dest_dir / "ww3_prnc.nml"
            assert not nml_file.exists()
