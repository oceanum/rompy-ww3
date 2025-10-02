"""WW3 Rompy sources."""

import logging
from pathlib import Path
from typing import Literal, Optional, Dict, Any, List
from pydantic import Field, model_validator
import xarray as xr

from rompy.core.source import SourceBase


logger = logging.getLogger(__name__)

HERE = Path(__file__).parent


class Ww3Source(SourceBase):
    """Ww3 source class with WW3-specific data source capabilities.

    This class extends SourceBase with WW3-specific data source handling for wave model inputs.
    """

    model_type: Literal["ww3"] = Field(
        default="ww3",
        description="Model type discriminator",
    )
    uri: str | Path = Field(description="Path to the dataset")
    kwargs: dict = Field(
        default={},
        description="Keyword arguments to pass to xarray.open_dataset",
    )

    # WW3-specific source parameters
    data_type: Optional[str] = Field(
        default=None,
        description="Type of data: 'winds', 'currents', 'water_levels', 'ice_conc', 'spectra', etc.",
    )

    file_format: Optional[str] = Field(
        default=None,
        description="File format: 'netcdf', 'binary', 'ascii', 'grib', etc.",
    )

    # Temporal parameters
    start_time: Optional[str] = Field(
        default=None, description="Start time for data (yyyymmdd hhmmss)"
    )
    end_time: Optional[str] = Field(
        default=None, description="End time for data (yyyymmdd hhmmss)"
    )
    time_step: Optional[int] = Field(default=None, description="Time step in seconds")

    # Spatial parameters
    spatial_resolution: Optional[str] = Field(
        default=None, description="Spatial resolution description"
    )

    # Variable mapping for WW3
    variable_mapping: Optional[Dict[str, str]] = Field(
        default=None, description="Mapping of source variables to WW3 variable names"
    )

    # Data filtering parameters
    variables: Optional[List[str]] = Field(
        default=None, description="List of variables to extract from the source"
    )

    # Quality control parameters
    min_value: Optional[float] = Field(
        default=None, description="Minimum valid value for data"
    )
    max_value: Optional[float] = Field(
        default=None, description="Maximum valid value for data"
    )

    @model_validator(mode="after")
    def validate_source_parameters(self) -> "Ww3Source":
        """Validate source parameters."""
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

        # Validate value ranges
        if self.min_value is not None and self.max_value is not None:
            if self.min_value >= self.max_value:
                raise ValueError("min_value must be less than max_value")

        return self

    def __str__(self) -> str:
        """String representation for this source class."""
        return f"Ww3Source(uri={self.uri}, data_type={self.data_type})"

    def _open(self) -> xr.Dataset:
        """This method needs to return an xarray Dataset object."""
        ds = xr.open_dataset(self.uri, **self.kwargs)

        # Apply variable filtering if specified
        if self.variables:
            ds = ds[self.variables]

        return ds

    def get_ww3_variable_name(self, source_var: str) -> str:
        """Get the WW3 variable name for a source variable.

        Args:
            source_var: The variable name in the source data

        Returns:
            The corresponding WW3 variable name
        """
        if self.variable_mapping and source_var in self.variable_mapping:
            return self.variable_mapping[source_var]

        # Default mappings for common variables
        default_mapping = {
            # Winds
            "u_wind": "u10",
            "v_wind": "v10",
            "wind_u": "u10",
            "wind_v": "v10",
            "wind_speed": "wspd",
            "wind_direction": "wdir",
            # Currents
            "u_current": "uocn",
            "v_current": "vocn",
            "current_u": "uocn",
            "current_v": "vocn",
            # Water levels
            "sea_surface_height": "ssh",
            "water_level": "ssh",
            "ssh": "ssh",
            # Ice
            "ice_concentration": "aic",
            "ice_thickness": "hit",
            # Air density
            "air_density": "rhoair",
            # Spectra (for assimilation)
            "wave_spectrum": "spec",
            "wave_energy_spectrum": "spec",
        }

        return default_mapping.get(source_var, source_var)

    def generate_source_config(self) -> Dict[str, Any]:
        """Generate configuration dictionary for this source."""
        config = {
            "uri": str(self.uri),
            "data_type": self.data_type,
            "file_format": self.file_format,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "time_step": self.time_step,
            "spatial_resolution": self.spatial_resolution,
            "variables": self.variables,
            "min_value": self.min_value,
            "max_value": self.max_value,
        }

        # Remove None values
        config = {k: v for k, v in config.items() if v is not None}

        return config

    def write_source_config(
        self, workdir: Path, filename: str = "source_config.txt"
    ) -> None:
        """Write source configuration to a file."""
        workdir.mkdir(parents=True, exist_ok=True)

        config_file = workdir / filename
        config = self.generate_source_config()

        with open(config_file, "w") as f:
            f.write("# WW3 Source Configuration\n")
            for key, value in config.items():
                if isinstance(value, list):
                    f.write(f"{key}: {', '.join(map(str, value))}\n")
                else:
                    f.write(f"{key}: {value}\n")

        logger.info(f"Wrote source configuration to {config_file}")

    def get_template_context(self) -> Dict[str, Any]:
        """Generate template context for Jinja2 templates.

        Returns:
            Dictionary containing source parameters for templates.
        """
        return {
            "uri": str(self.uri),
            "data_type": self.data_type,
            "file_format": self.file_format,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "time_step": self.time_step,
            "spatial_resolution": self.spatial_resolution,
            "variables": self.variables,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "variable_mapping": self.variable_mapping,
        }

    def get_ww3_variable_mapping(self) -> Dict[str, str]:
        """Get the complete WW3 variable mapping.

        Returns:
            Dictionary mapping source variable names to WW3 variable names.
        """
        # Start with default mappings
        default_mapping = {
            # Winds
            "u_wind": "u10",
            "v_wind": "v10",
            "wind_u": "u10",
            "wind_v": "v10",
            "wind_speed": "wspd",
            "wind_direction": "wdir",
            # Currents
            "u_current": "uocn",
            "v_current": "vocn",
            "current_u": "uocn",
            "current_v": "vocn",
            # Water levels
            "sea_surface_height": "ssh",
            "water_level": "ssh",
            "ssh": "ssh",
            # Ice
            "ice_concentration": "aic",
            "ice_thickness": "hit",
            # Air density
            "air_density": "rhoair",
            # Spectra (for assimilation)
            "wave_spectrum": "spec",
            "wave_energy_spectrum": "spec",
        }

        # Update with custom mappings if provided
        if self.variable_mapping:
            default_mapping.update(self.variable_mapping)

        return default_mapping

    def is_time_range_valid(self) -> bool:
        """Check if the time range is valid.

        Returns:
            True if both start_time and end_time are provided and start_time < end_time, False otherwise.
        """
        if not self.start_time or not self.end_time:
            return False

        # Simple string comparison for yyyymmdd hhmmss format
        return self.start_time < self.end_time

    def get_data_info(self) -> Dict[str, Any]:
        """Get information about the data in this source.

        Returns:
            Dictionary with information about the data.
        """
        try:
            ds = self._open()
            info = {
                "variables": list(ds.data_vars.keys()),
                "dimensions": dict(ds.dims),
                "coordinates": list(ds.coords.keys()),
            }
            ds.close()
            return info
        except Exception as e:
            logger.warning(f"Could not get data info: {e}")
            return {
                "variables": [],
                "dimensions": {},
                "coordinates": [],
                "error": str(e),
            }
