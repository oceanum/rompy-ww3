"""TRACK_NML and FILE_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field
from .basemodel import NamelistBaseModel


class Track(NamelistBaseModel):
    """TRACK_NML namelist for WW3.
    
    Defines the output fields to postprocess.
    """
    
    timestart: Optional[str] = Field(
        default=None,
        description="Start date for the output field (yyyymmdd hhmmss)"
    )
    timestride: Optional[str] = Field(
        default=None,
        description="Time stride for the output field (seconds)"
    )
    timecount: Optional[str] = Field(
        default=None,
        description="Number of time steps"
    )
    timesplit: Optional[int] = Field(
        default=None,
        description="[4(yearly),6(monthly),8(daily),10(hourly)]"
    )


class TrackFile(NamelistBaseModel):
    """FILE_NML namelist for WW3 track output.
    
    Defines the content of the output file.
    """
    
    prefix: Optional[str] = Field(
        default=None,
        description="Prefix for output file name"
    )
    netcdf: Optional[int] = Field(
        default=None,
        description="Netcdf version [3|4]"
    )