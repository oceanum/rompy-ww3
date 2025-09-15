"""POINT_NML and FILE_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field
from .basemodel import NamelistBaseModel


class Point(NamelistBaseModel):
    """POINT_NML namelist for WW3.
    
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
        description="[0(nodate),4(yearly),6(monthly),8(daily),10(hourly)]"
    )
    list: Optional[str] = Field(
        default=None,
        description="List of points index ['all'|'1 2 3']"
    )
    samefile: Optional[bool] = Field(
        default=None,
        description="All the points in the same file"
    )
    buffer: Optional[int] = Field(
        default=None,
        description="Number of points to process per pass"
    )
    type: Optional[int] = Field(
        default=None,
        description="[0=inventory | 1=spectra | 2=mean param | 3=source terms]"
    )
    dimorder: Optional[bool] = Field(
        default=None,
        description="[time,station=T | station,time=F]"
    )


class PointFile(NamelistBaseModel):
    """FILE_NML namelist for WW3 point output.
    
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