"""WW3 Rompy data."""

import logging
from pathlib import Path
from typing import Literal, Optional, Dict, Any, List
from pydantic import Field, model_validator

from rompy.core.data import DataGrid


logger = logging.getLogger(__name__)

HERE = Path(__file__).parent


class Data(DataGrid):
    """Ww3 data class with WW3-specific data handling capabilities.

    This class extends DataGrid with WW3-specific data handling for wave model inputs.
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
        default="F",
        description="Forcing flag: 'F' (no), 'T' (file), 'H' (homogeneous), 'C' (coupled)",
    )

    # Data assimilation flags
    assim_flag: Optional[str] = Field(
        default="F", description="Assimilation flag: 'F' (no), 'T' (file)"
    )

    # File format information
    file_format: Optional[str] = Field(
        default=None,
        description="File format for input data (e.g., 'netcdf', 'binary', 'ascii')",
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

        # Validate file format
        valid_formats = ["netcdf", "binary", "ascii", "grib"]
        if self.file_format and self.file_format not in valid_formats:
            raise ValueError(f"file_format must be one of {valid_formats}")

        # Validate time step
        if self.time_step is not None and self.time_step <= 0:
            raise ValueError("time_step must be positive")

        return self

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
                config[forcing_mapping[self.data_type]] = self.forcing_flag

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
            if self.homogeneous_values:
                f.write(f"Homogeneous Values: {self.homogeneous_values}\n")
            if self.variable_mapping:
                f.write(f"Variable Mapping: {self.variable_mapping}\n")

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
            "homogeneous_values": self.homogeneous_values,
            "variable_mapping": self.variable_mapping,
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
