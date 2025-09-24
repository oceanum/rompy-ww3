"""UPRSTR_NML namelist implementation for WW3."""

from typing import Optional, List
from pydantic import Field
from .basemodel import NamelistBaseModel


class RestartUpdate(NamelistBaseModel):
    """UPRSTR_NML namelist for WW3.
    
    Defines restart file update parameters for WW3.
    """
    
    # Update configuration
    update_time: Optional[str] = Field(
        default=None,
        description="Time for restart file update (yyyymmdd hhmmss)"
    )
    update_stride: Optional[str] = Field(
        default=None,
        description="Time stride for restart file updates (seconds)"
    )
    
    # File configuration
    input_restart: Optional[str] = Field(
        default=None,
        description="Input restart file path"
    )
    output_restart: Optional[str] = Field(
        default=None,
        description="Output restart file path"
    )
    
    # Fields to update
    wave_field: Optional[bool] = Field(
        default=None,
        description="Flag to update wave field (T/F)"
    )
    water_level: Optional[bool] = Field(
        default=None,
        description="Flag to update water level (T/F)"
    )
    current: Optional[bool] = Field(
        default=None,
        description="Flag to update current (T/F)"
    )
    ice: Optional[bool] = Field(
        default=None,
        description="Flag to update ice fields (T/F)"
    )
    wind: Optional[bool] = Field(
        default=None,
        description="Flag to update wind fields (T/F)"
    )
    
    # Update method
    update_method: Optional[str] = Field(
        default=None,
        description="Method for updating ('replace', 'add', 'multiply')"
    )