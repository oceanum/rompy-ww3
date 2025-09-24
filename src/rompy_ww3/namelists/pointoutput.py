"""OUNP_NML namelist implementation for WW3."""

from typing import Optional, List
from pydantic import Field
from .basemodel import NamelistBaseModel


class PointOutput(NamelistBaseModel):
    """OUNP_NML namelist for WW3.
    
    Defines point output parameters for WW3.
    """
    
    # Output points configuration
    indices: Optional[str] = Field(
        default=None,
        description="List of point indices to output (space-separated integers)"
    )
    coordinates: Optional[str] = Field(
        default=None,
        description="List of point coordinates to output (space-separated 'lon lat' pairs)"
    )
    
    # Time configuration
    start: Optional[str] = Field(
        default=None,
        description="Point output start time (yyyymmdd hhmmss)"
    )
    stride: Optional[str] = Field(
        default=None,
        description="Point output time stride (seconds)"
    )
    stop: Optional[str] = Field(
        default=None,
        description="Point output stop time (yyyymmdd hhmmss)"
    )
    
    # Field configuration
    field_list: Optional[str] = Field(
        default=None,
        description="List of fields to output at points (space-separated)"
    )
    
    # File configuration
    single_file: Optional[bool] = Field(
        default=None,
        description="Flag to output all points to single file (T/F)"
    )
    buffer_size: Optional[int] = Field(
        default=None,
        description="Number of points to process per pass"
    )
    
    # Interpolation
    interp_method: Optional[str] = Field(
        default=None,
        description="Interpolation method ('nearest', 'linear')"
    )