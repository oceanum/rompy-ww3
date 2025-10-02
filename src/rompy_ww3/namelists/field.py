"""FIELD_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field
from .basemodel import NamelistBaseModel


class Field(NamelistBaseModel):
    """FIELD_NML namelist for WW3.

    Defines the output fields to postprocess.
    """

    timestart: Optional[str] = Field(
        default=None, description="Start date for the output field (yyyymmdd hhmmss)"
    )
    timestride: Optional[str] = Field(
        default=None, description="Time stride for the output field (seconds)"
    )
    timecount: Optional[str] = Field(default=None, description="Number of time steps")
    timesplit: Optional[int] = Field(
        default=None, description="[0(nodate),4(yearly),6(monthly),8(daily),10(hourly)]"
    )
    list: Optional[str] = Field(default=None, description="List of output fields")
    partition: Optional[str] = Field(
        default=None, description="List of wave partitions ['0 1 2 3']"
    )
    samefile: Optional[bool] = Field(
        default=None, description="All the variables in the same file"
    )
    vector: Optional[bool] = Field(
        default=None,
        description="Vector [T] or dir/magnitude [F] for directional fields",
    )
    type: Optional[int] = Field(
        default=None, description="[2 = SHORT, 3 = it depends , 4 = REAL]"
    )
    fcvars: Optional[bool] = Field(
        default=None, description="Generate auxiliary forecast variables"
    )
    timeref: Optional[str] = Field(default=None, description="Forecast reference time")
    timevar: Optional[str] = Field(
        default=None, description="Time var type ['D' = DOUBLE, 'I' = INT64]"
    )
    timeunit: Optional[str] = Field(
        default=None, description="Time units ['D' = days, 'I' = seconds]"
    )
    timeepoch: Optional[str] = Field(
        default=None, description="Epoch used for encoding of NC time variables"
    )
    noval: Optional[float] = Field(
        default=None, description="Value for wet cells that have an UNDEF value"
    )
    mapsta: Optional[bool] = Field(
        default=None, description="Output MAPSTA field in file?"
    )
