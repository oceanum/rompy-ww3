"""WW3 Rompy sources."""

import logging
from pathlib import Path
from typing import Literal, Optional
from pydantic import Field
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
        description="Type of data: 'winds', 'currents', 'water_levels', 'ice_conc', 'spectra', etc."
    )
    
    file_format: Optional[str] = Field(
        default=None,
        description="File format: 'netcdf', 'binary', 'ascii', 'grib', etc."
    )
    
    # Temporal parameters
    start_time: Optional[str] = Field(
        default=None,
        description="Start time for data (yyyymmdd hhmmss)"
    )
    end_time: Optional[str] = Field(
        default=None,
        description="End time for data (yyyymmdd hhmmss)"
    )
    time_step: Optional[int] = Field(
        default=None,
        description="Time step in seconds"
    )
    
    # Spatial parameters
    spatial_resolution: Optional[str] = Field(
        default=None,
        description="Spatial resolution description"
    )
    
    # Variable mapping for WW3
    variable_mapping: Optional[dict] = Field(
        default=None,
        description="Mapping of source variables to WW3 variable names"
    )

    def __str__(self) -> str:
        """String representation for this source class."""
        return f"Ww3Source(uri={self.uri}, data_type={self.data_type})"

    def _open(self) -> xr.Dataset:
        """This method needs to return an xarray Dataset object."""
        return xr.open_dataset(self.uri, **self.kwargs)
    
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
            
            # Spectra (for assimilation)
            "wave_spectrum": "spec",
            "wave_energy_spectrum": "spec"
        }
        
        return default_mapping.get(source_var, source_var)
    
    def generate_source_config(self) -> dict:
        """Generate configuration dictionary for this source."""
        config = {
            "uri": str(self.uri),
            "data_type": self.data_type,
            "file_format": self.file_format,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "time_step": self.time_step,
            "spatial_resolution": self.spatial_resolution
        }
        
        # Remove None values
        config = {k: v for k, v in config.items() if v is not None}
        
        return config
    
    def write_source_config(self, workdir: Path, filename: str = "source_config.txt") -> None:
        """Write source configuration to a file."""
        workdir.mkdir(parents=True, exist_ok=True)
        
        config_file = workdir / filename
        config = self.generate_source_config()
        
        with open(config_file, "w") as f:
            f.write("# WW3 Source Configuration\n")
            for key, value in config.items():
                f.write(f"{key}: {value}\n")
                
        logger.info(f"Wrote source configuration to {config_file}")
