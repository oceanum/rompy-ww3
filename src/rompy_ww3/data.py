"""WW3 Rompy data."""

import logging
from pathlib import Path
from typing import Literal, Optional, Dict, Any, List, Union
from pydantic import Field, model_validator
import xarray as xr

from rompy.core.data import DataGrid
from rompy.core.source import SourceBase

# Import the existing WW3 namelist objects
from rompy_ww3.namelists.forcing import Forcing, ForcingField, ForcingGrid


logger = logging.getLogger(__name__)

HERE = Path(__file__).parent


class Data(DataGrid):
    """Ww3 data class with WW3-specific data handling capabilities.

    This class extends DataGrid with WW3-specific data handling for wave model inputs.
    It uses rompy Source objects to read large lazy datasets, crops the required
    area and time from the data, writes to the rompy WW3 workspace, and updates
    the appropriate nml objects internally to point to the processed files.
    """

    model_type: Literal["ww3"] = Field(
        default="ww3",
        description="Model type discriminator",
    )

    # WW3-specific data types
    data_type: Optional[str] = Field(
        default=None,
        description="Type of data: 'winds', 'currents', 'water_levels', 'ice_conc', etc.",
    )

    # Forcing flags that correspond to WW3 namelists
    forcing_flag: Optional[str] = Field(
        default="T",  # Changed default to 'T' (file) since we're processing netcdf
        description="Forcing flag: 'F' (no), 'T' (file), 'H' (homogeneous), 'C' (coupled)",
    )

    # Data assimilation flags
    assim_flag: Optional[str] = Field(
        default="F", description="Assimilation flag: 'F' (no), 'T' (file)"
    )

    # File format information
    file_format: Optional[str] = Field(
        default="netcdf",
        description="File format for input data (e.g., 'netcdf')",
    )

    # Temporal information
    start_time: Optional[str] = Field(
        default=None, description="Start time for data (yyyymmdd hhmmss)"
    )
    end_time: Optional[str] = Field(
        default=None, description="End time for data (yyyymmdd hhmmss)"
    )
    time_step: Optional[int] = Field(default=None, description="Time step in seconds")

    # Homogeneous data values (for forcing_flag = 'H')
    homogeneous_values: Optional[List[float]] = Field(
        default=None,
        description="Homogeneous values for data (used when forcing_flag = 'H')",
    )

    # Variable mapping for source data
    variable_mapping: Optional[Dict[str, str]] = Field(
        default=None,
        description="Mapping of WW3 variable names to source variable names",
    )

    # WW3 preprocessing specific parameters for ww3_prnc
    grid_type: str = Field(
        default="latlon",
        description="Grid type for forcing data: 'asis' or 'latlon'",
    )

    # Input file configuration for ww3_prnc
    input_filename: str = Field(
        default="input.nc",
        description="Name of the input file to be processed by ww3_prnc",
    )

    # Time shift for the input data (optional)
    time_shift: Optional[str] = Field(
        default=None,
        description="Time shift for input data (yyyymmdd hhmmss)",
    )

    # Output file type based on field processed
    output_file: Optional[str] = Field(
        default=None,
        description="Output file name after preprocessing (e.g., 'wind.ww3', 'current.ww3')",
    )

    @model_validator(mode="after")
    def validate_data_parameters(self) -> "Data":
        """Validate data parameters."""
        # Validate forcing flag
        if self.forcing_flag and self.forcing_flag not in ["F", "T", "H", "C"]:
            raise ValueError("forcing_flag must be one of 'F', 'T', 'H', or 'C'")

        # Validate assimilation flag
        if self.assim_flag and self.assim_flag not in ["F", "T"]:
            raise ValueError("assim_flag must be one of 'F' or 'T'")

        # Validate data type
        valid_data_types = [
            "winds",
            "currents",
            "water_levels",
            "ice_conc",
            "air_density",
            "atm_momentum",
            "spectra",
            "mean",
            "spec1d",
            "mud_density",
            "mud_thickness",
            "mud_viscosity",
        ]
        if self.data_type and self.data_type not in valid_data_types:
            raise ValueError(f"data_type must be one of {valid_data_types}")

        # Validate grid type
        if self.grid_type not in ["asis", "latlon"]:
            raise ValueError("grid_type must be 'asis' or 'latlon'")

        # Validate file format
        if self.file_format != "netcdf":
            raise ValueError("Currently only netcdf format is supported for ww3_prnc")

        # Validate time step
        if self.time_step is not None and self.time_step <= 0:
            raise ValueError("time_step must be positive")

        # If we're using file input (T) but don't have a source, that's an issue
        # We'll check this in the get method instead since the source comes from the parent class
        # The parent DataGrid class requires a source, but in WW3 we can have homogeneous data

        return self

    def get(self, destdir: Union[str, Path], *args, **kwargs) -> Path:
        """Retrieve, process and save WW3 forcing data.

        This method will use the source to retrieve data, then process it
        by cropping to the required time and area, and save the processed
        netCDF file to the specified destination. It also creates the namelist
        file needed for external ww3_prnc processing.

        Args:
            destdir: Destination directory to save the processed file and namelist
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            Path to the WW3-ready output file (after external ww3_prnc processing)
        """
        from datetime import datetime

        destdir = Path(destdir)
        destdir.mkdir(parents=True, exist_ok=True)

        # If we're using homogeneous forcing, no processing is needed
        if self.forcing_flag == "H":
            logger.info(f"No processing needed for homogeneous data: {self.data_type}")
            # Return a path indicating this data doesn't need binary files
            return destdir / "homogeneous_data"

        # If we're not using file input, return early
        if self.forcing_flag != "T":
            logger.info(f"No processing needed for forcing flag: {self.forcing_flag}")
            return destdir / "no_processing_needed"

        # Retrieve data from the source if it exists
        source = getattr(self, "source", None)
        if source:
            logger.info(f"Retrieving data from source: {source}")
            # Use the parent's get method to handle the source properly
            source_file = super().get(destdir, *args, **kwargs)

            # Open the source file to apply additional filtering if needed
            ds = xr.open_dataset(source_file)

            # Apply temporal cropping if needed
            if self.start_time or self.end_time:
                time_dim = "time"  # Default time dimension name
                if time_dim in ds.dims:
                    start_time = (
                        self.start_time
                        if self.start_time
                        else ds[time_dim].isel({time_dim: 0}).values
                    )
                    end_time = (
                        self.end_time
                        if self.end_time
                        else ds[time_dim].isel({time_dim: -1}).values
                    )

                    # Convert string times to datetime if needed
                    if isinstance(start_time, str):
                        start_time = datetime.strptime(start_time, "%Y%m%d %H%M%S")
                    if isinstance(end_time, str):
                        end_time = datetime.strptime(end_time, "%Y%m%d %H%M%S")

                    ds = ds.sel({time_dim: slice(start_time, end_time)})

            # Apply spatial cropping if grid is provided (this uses the inherited _filter_grid method)
            if "grid" in kwargs:
                from rompy.core.grid import RegularGrid, TriGrid

                grid = kwargs["grid"]
                if isinstance(grid, (RegularGrid, TriGrid)):
                    ds = self._filter_grid(ds, grid)

            # Close the dataset before saving to avoid file handle conflicts
            ds.close()

            # Create a temporary file to avoid file locking issues
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tmp_file:
                temp_path = Path(tmp_file.name)

            # Reopen dataset to save with changes
            ds = xr.open_dataset(source_file)

            # Apply temporal cropping if needed (reapply to the reopened dataset)
            if self.start_time or self.end_time:
                time_dim = "time"  # Default time dimension name
                if time_dim in ds.dims:
                    start_time = (
                        self.start_time
                        if self.start_time
                        else ds[time_dim].isel({time_dim: 0}).values
                    )
                    end_time = (
                        self.end_time
                        if self.end_time
                        else ds[time_dim].isel({time_dim: -1}).values
                    )

                    # Convert string times to datetime if needed
                    if isinstance(start_time, str):
                        start_time = datetime.strptime(start_time, "%Y%m%d %H%M%S")
                    if isinstance(end_time, str):
                        end_time = datetime.strptime(end_time, "%Y%m%d %H%M%S")

                    ds = ds.sel({time_dim: slice(start_time, end_time)})

            # Apply spatial cropping if grid is provided (reapply to the reopened dataset)
            if "grid" in kwargs:
                from rompy.core.grid import RegularGrid, TriGrid

                grid = kwargs["grid"]
                if isinstance(grid, (RegularGrid, TriGrid)):
                    ds = self._filter_grid(ds, grid)

            # Save the processed data to a temporary file first
            ds.to_netcdf(temp_path, mode="w")
            ds.close()

            # Now create the processed file with the correct name
            processed_file = destdir / self.input_filename

            # Move the temporary file to the final location with the correct name
            import shutil

            shutil.move(str(temp_path), processed_file)
        else:
            # If no source, assume the input file already exists
            processed_file = destdir / self.input_filename
            if not processed_file.exists():
                raise FileNotFoundError(f"Input file does not exist: {processed_file}")

        # Generate the namelist file for external ww3_prnc processing
        nml_file = destdir / "ww3_prnc.nml"
        self.write_namelist(nml_file)

        # Return the expected output path after external ww3_prnc processing
        output_path = self._get_output_path(destdir)
        logger.info(
            f"Successfully prepared WW3 forcing data. NetCDF: {processed_file}, Namelist: {nml_file}"
        )
        return output_path

    def _get_output_path(self, destdir: Path) -> Path:
        """Get the expected output file path based on data type."""
        output_file_map = {
            "winds": "wind.ww3",
            "currents": "current.ww3",
            "water_levels": "level.ww3",
            "ice_conc": "ice.ww3",
            "air_density": "air.ww3",  # Placeholder
            "atm_momentum": "atm.ww3",  # Placeholder
        }
        output_file = output_file_map.get(self.data_type, f"{self.data_type}.ww3")
        return destdir / output_file

    def write_namelist(self, nml_file: Union[str, Path]) -> None:
        """Write the ww3_prnc namelist file to disk for external use using existing namelist objects."""
        nml_file = Path(nml_file)

        # Create the Forcing namelist object
        forcing_nml = self.get_forcing_nml()

        # Write forcing namelist to file
        with open(nml_file, "w") as f:
            f.write(forcing_nml.render())
            # Add FILE_NML section since it's not part of the Forcing object
            f.write("\n&FILE_NML\n")
            f.write(f"  FILE%FILENAME = '{self.input_filename}'\n")

            # Add variable mapping if provided
            if self.variable_mapping:
                # Determine the number of components based on the data type
                n_components = 1
                if self.data_type in ["winds", "currents"]:
                    n_components = 2
                elif self.data_type == "wind_ast":  # wind with air-sea temp diff
                    n_components = 3

                for i in range(1, n_components + 1):
                    var_key = f"VAR({i})"
                    var_name = self.variable_mapping.get(var_key)
                    if var_name:
                        f.write(f"  FILE%{var_key} = '{var_name}'\n")

            # Set default variable names if not provided
            if not self.variable_mapping:
                default_vars = {
                    "winds": ["UWND", "VWND"],
                    "currents": ["UCUR", "VCUR"],
                    "water_levels": ["LEVEL"],
                    "ice_conc": ["ICEC"],
                }
                if self.data_type in default_vars:
                    for i, var_name in enumerate(default_vars[self.data_type], 1):
                        f.write(f"  FILE%VAR({i}) = '{var_name}'\n")

            f.write("&END\n")

        logger.info(f"Wrote ww3_prnc namelist to: {nml_file}")

    def get_forcing_nml(self):
        """Get the Forcing namelist object."""
        # Create ForcingField based on data_type
        field_params = {
            "winds": {"winds": True},
            "currents": {"currents": True},
            "water_levels": {"water_levels": True},
            "ice_conc": {"ice_conc": True},
            "air_density": {"air_density": True},
            "atm_momentum": {"atm_momentum": True},
            "mud_density": {"mud_density": True},
            "mud_thickness": {"mud_thickness": True},
            "mud_viscosity": {"mud_viscosity": True},
        }

        field_config = field_params.get(self.data_type, {})
        forcing_field = ForcingField(**field_config)

        # Create ForcingGrid based on grid_type
        grid_params = {self.grid_type: True}
        forcing_grid = ForcingGrid(**grid_params)

        # Create the main Forcing object
        forcing = Forcing(
            timestart=self.start_time or "19000101 000000",
            timestop=self.end_time or "29001231 000000",
            field=forcing_field,
            grid=forcing_grid,
        )

        return forcing

    def get_forcing_config(self) -> Dict[str, Any]:
        """Get configuration for INPUT_NML forcing parameters."""
        config = {}

        if self.data_type:
            # Map data types to WW3 forcing parameters
            forcing_mapping = {
                "winds": "FORCING%WINDS",
                "currents": "FORCING%CURRENTS",
                "water_levels": "FORCING%WATER_LEVELS",
                "ice_conc": "FORCING%ICE_CONC",
                "air_density": "FORCING%AIR_DENSITY",
                "atm_momentum": "FORCING%ATM_MOMENTUM",
                "mud_density": "FORCING%MUD_DENSITY",
                "mud_thickness": "FORCING%MUD_THICKNESS",
                "mud_viscosity": "FORCING%MUD_VISCOSITY",
            }

            if self.data_type in forcing_mapping:
                # After processing, forcing flag should be 'T' if successful
                config[forcing_mapping[self.data_type]] = (
                    "T" if self.output_file else self.forcing_flag
                )

        return config

    def get_assim_config(self) -> Dict[str, Any]:
        """Get configuration for INPUT_NML assimilation parameters."""
        config = {}

        if self.data_type:
            # Map data types to WW3 assimilation parameters
            assim_mapping = {
                "spectra": "ASSIM%SPEC2D",
                "mean": "ASSIM%MEAN",
                "spec1d": "ASSIM%SPEC1D",
            }

            if self.data_type in assim_mapping:
                config[assim_mapping[self.data_type]] = self.assim_flag

        return config

    def generate_input_data_nml(self) -> str:
        """Generate namelist entries for input data configuration."""
        lines = []

        # Add forcing configuration
        forcing_config = self.get_forcing_config()
        for key, value in forcing_config.items():
            lines.append(f"  INPUT%{key} = '{value}'")

        # Add assimilation configuration
        assim_config = self.get_assim_config()
        for key, value in assim_config.items():
            lines.append(f"  INPUT%{key} = '{value}'")

        return "\n".join(lines)

    def write_data_config(self, workdir: Path) -> None:
        """Write data configuration files."""
        workdir.mkdir(parents=True, exist_ok=True)

        # Write data configuration info
        config_file = workdir / "data_config.txt"
        with open(config_file, "w") as f:
            f.write("# WW3 Data Configuration\n")
            f.write(f"Data Type: {self.data_type or 'unspecified'}\n")
            f.write(f"Forcing Flag: {self.forcing_flag}\n")
            f.write(f"Assimilation Flag: {self.assim_flag}\n")
            f.write(f"File Format: {self.file_format or 'unspecified'}\n")
            f.write(f"Start Time: {self.start_time or 'unspecified'}\n")
            f.write(f"End Time: {self.end_time or 'unspecified'}\n")
            f.write(f"Time Step: {self.time_step or 'unspecified'}\n")
            f.write(f"Grid Type: {self.grid_type}\n")
            f.write(f"Input Filename: {self.input_filename}\n")
            f.write(f"Output File: {self.output_file or 'unspecified'}\n")
            if self.homogeneous_values:
                f.write(f"Homogeneous Values: {self.homogeneous_values}\n")
            if self.variable_mapping:
                f.write(f"Variable Mapping: {self.variable_mapping}\n")
            source = getattr(self, "source", None)
            if source:
                f.write(f"Source: {source}\n")

        logger.info(f"Wrote data configuration to {config_file}")

    def get_template_context(self) -> Dict[str, Any]:
        """Generate template context for Jinja2 templates.

        Returns:
            Dictionary containing data parameters for templates.
        """
        return {
            "data_type": self.data_type,
            "forcing_flag": self.forcing_flag,
            "assim_flag": self.assim_flag,
            "file_format": self.file_format,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "time_step": self.time_step,
            "grid_type": self.grid_type,
            "input_filename": self.input_filename,
            "output_file": self.output_file,
            "homogeneous_values": self.homogeneous_values,
            "variable_mapping": self.variable_mapping,
            "source": getattr(self, "source", None),
            "forcing_config": self.get_forcing_config(),
            "assim_config": self.get_assim_config(),
        }

    def is_homogeneous(self) -> bool:
        """Check if this data is homogeneous.

        Returns:
            True if forcing_flag is 'H', False otherwise.
        """
        return self.forcing_flag == "H"

    def is_from_file(self) -> bool:
        """Check if this data is from a file.

        Returns:
            True if forcing_flag is 'T', False otherwise.
        """
        return self.forcing_flag == "T"

    def is_coupled(self) -> bool:
        """Check if this data is coupled.

        Returns:
            True if forcing_flag is 'C', False otherwise.
        """
        return self.forcing_flag == "C"

    def is_disabled(self) -> bool:
        """Check if this data is disabled.

        Returns:
            True if forcing_flag is 'F', False otherwise.
        """
        return self.forcing_flag == "F"
