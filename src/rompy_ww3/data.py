"""WW3 Rompy data."""

import logging
from pathlib import Path
from typing import Literal, Optional, Dict, Any
from pydantic import Field

from rompy.core.data import DataBlob, DataGrid


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
        description="Type of data: 'winds', 'currents', 'water_levels', 'ice_conc', etc."
    )
    
    # Forcing flags that correspond to WW3 namelists
    forcing_flag: Optional[str] = Field(
        default="F",
        description="Forcing flag: 'F' (no), 'T' (file), 'H' (homogeneous), 'C' (coupled)"
    )
    
    # Data assimilation flags
    assim_flag: Optional[str] = Field(
        default="F",
        description="Assimilation flag: 'F' (no), 'T' (file)"
    )
    
    # File format information
    file_format: Optional[str] = Field(
        default=None,
        description="File format for input data (e.g., 'netcdf', 'binary', 'ascii')"
    )
    
    # Temporal information
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
                "atm_momentum": "FORCING%ATM_MOMENTUM"
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
                "spec1d": "ASSIM%SPEC1D"
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
            f.write(f"# WW3 Data Configuration\n")
            f.write(f"Data Type: {self.data_type or 'unspecified'}\n")
            f.write(f"Forcing Flag: {self.forcing_flag}\n")
            f.write(f"Assimilation Flag: {self.assim_flag}\n")
            f.write(f"File Format: {self.file_format or 'unspecified'}\n")
            f.write(f"Start Time: {self.start_time or 'unspecified'}\n")
            f.write(f"End Time: {self.end_time or 'unspecified'}\n")
            f.write(f"Time Step: {self.time_step or 'unspecified'}\n")
            
        logger.info(f"Wrote data configuration to {config_file}")
