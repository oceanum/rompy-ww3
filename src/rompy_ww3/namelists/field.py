"""FIELD_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel
from .validation import validate_date_format


class Field(NamelistBaseModel):
    """FIELD_NML namelist for WW3.

    The FIELD_NML namelist defines the field output configuration for WAVEWATCH III post-processing.
    This namelist controls how field (gridded) output is generated from the model results.

    The field output can include various wave parameters like significant wave height,
    mean period, direction, etc., and can be written to NetCDF files with various
    formatting and temporal options.
    """

    timestart: Optional[str] = Field(
        default=None,
        description=(
            "Start date for the output field in format 'YYYYMMDD HHMMSS'. "
            "This specifies when to begin writing field output during the post-processing. "
            "Example: '20100101 000000' for January 1, 2010 at 00:00:00 UTC."
        ),
    )
    timestride: Optional[int] = Field(
        default=None,
        description=(
            "Time stride for the output field in seconds. "
            "This specifies the time interval between field output writes. "
            "Example: 3600 for hourly output, 21600 for 6-hourly output."
        ),
    )
    timecount: Optional[int] = Field(
        default=None,
        description=(
            "Number of time steps for the output field. "
            "This specifies the total number of time steps for which field output will be generated. "
        ),
    )
    timesplit: Optional[int] = Field(
        default=None,
        description=(
            "Time splitting option for output file management:\n"
            "  0: No date in filename\n"
            "  4: Yearly splitting\n"
            "  6: Monthly splitting\n"
            "  8: Daily splitting\n"
            "  10: Hourly splitting\n"
            "This controls how output files are split over time periods."
        ),
        ge=0,
        le=10,
    )
    list: Optional[str] = Field(
        default=None,
        description=(
            "List of output fields to include in the output file. "
            "This is a space-separated list of parameter names to output, such as: "
            "'HS T02 DIR SPR' for significant wave height, mean period, direction, and spread."
        ),
    )
    partition: Optional[str] = Field(
        default=None,
        description=(
            "List of wave partitions to output, specified as a space-separated string. "
            "Examples: '0 1 2 3' for partitions 0-3, '0' for total wave field only. "
            "Partition 0 is the total wave field, partitions 1-N are individual swell partitions."
        ),
    )
    samefile: Optional[bool] = Field(
        default=None,
        description=(
            "Flag to put all variables in the same file (T) or separate files (F). "
            "When True, all requested output variables are written to a single NetCDF file. "
            "When False, each variable may be written to separate files."
        ),
    )
    vector: Optional[bool] = Field(
        default=None,
        description=(
            "Vector format [T] or direction/magnitude format [F] for directional fields. "
            "When True, directional fields like currents/winds are output as vector components. "
            "When False, they are output as direction and magnitude separately."
        ),
    )
    type: Optional[int] = Field(
        default=None,
        description=(
            "Data type for output variables:\n"
            "  2: SHORT (16-bit integer)\n"
            "  3: Depends on the variable type\n"
            "  4: REAL (32-bit float)\n"
            "This controls the precision and storage format of the output variables."
        ),
        ge=2,
        le=4,
    )
    fcvars: Optional[bool] = Field(
        default=None,
        description=(
            "Flag to generate auxiliary forecast variables. "
            "When True, additional forecast-related variables are included in the output."
        ),
    )
    timeref: Optional[str] = Field(
        default=None,
        description=(
            "Forecast reference time in format 'YYYYMMDD HHMMSS'. "
            "This specifies the reference time for forecast variables in the output. "
            "Example: '20100101 000000' for January 1, 2010 at 00:00:00 UTC."
        ),
    )
    timevar: Optional[str] = Field(
        default=None,
        description=(
            "Time variable type for NetCDF encoding:\n"
            "  'D': DOUBLE precision time variable\n"
            "  'I': INT64 time variable\n"
            "This controls the data type of the time coordinate variable in NetCDF output."
        ),
    )
    timeunit: Optional[str] = Field(
        default=None,
        description=(
            "Time units for NetCDF encoding:\n"
            "  'D': Days since epoch\n"
            "  'S': Seconds since epoch\n"
            "This controls the units of the time coordinate in the NetCDF output."
        ),
    )
    timeepoch: Optional[str] = Field(
        default=None,
        description=(
            "Epoch used for encoding of NetCDF time variables in format 'YYYY-MM-DD HH:MM:SS'. "
            "This specifies the reference date/time for NetCDF time encoding. "
            "Example: '1900-01-01 00:00:00' for the standard 1900 epoch."
        ),
    )
    noval: Optional[float] = Field(
        default=None,
        description=(
            "Value to use for wet cells that have an undefined (UNDEF) value. "
            "This is a fill value used in the NetCDF output for cells that are "
            "wet but have no valid data for the specific variable."
        ),
    )
    mapsta: Optional[bool] = Field(
        default=None,
        description=(
            "Flag to output MAPSTA field in file (T) or not (F). "
            "When True, the MAPSTA field (mapping status) is included in the output file."
        ),
    )

    @field_validator("timestart", "timeref")
    @classmethod
    def validate_time_format(cls, v):
        """Validate date format for time fields."""
        if v is not None:
            return validate_date_format(v)
        return v

    @field_validator("timestride", "timecount", mode="before")
    @classmethod
    def parse_integer_fields(cls, v):
        """Parse string inputs to integers (backward-compatible)."""
        if v is None:
            return v
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError as e:
                raise ValueError(f"Invalid integer format: {v}. Error: {e}")
        if isinstance(v, int):
            return v
        return v

    @field_validator("timesplit")
    @classmethod
    def validate_timesplit(cls, v):
        """Validate timesplit value."""
        if v is not None and v not in [0, 4, 6, 8, 10]:
            raise ValueError(f"Time split must be 0, 4, 6, 8, or 10, got {v}")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        """Validate type value."""
        if v is not None and v not in [2, 3, 4]:
            raise ValueError(f"Type must be 2, 3, or 4, got {v}")
        return v

    @field_validator("timevar")
    @classmethod
    def validate_timevar(cls, v):
        """Validate timevar value."""
        if v is not None:
            valid_values = {"D", "I", "d", "i"}
            if v.upper() not in valid_values:
                raise ValueError(f"Timevar must be 'D' or 'I', got {v}")
        return v.upper() if v is not None else v

    @field_validator("timeunit")
    @classmethod
    def validate_timeunit(cls, v):
        """Validate timeunit value."""
        if v is not None:
            valid_values = {"D", "S", "d", "s"}
            if v.upper() not in valid_values:
                raise ValueError(f"Timeunit must be 'D' or 'S', got {v}")
        return v.upper() if v is not None else v  # Use 'S' for seconds, not 'I'

    @field_validator("samefile", "vector", "fcvars", "mapsta")
    @classmethod
    def validate_boolean_flags(cls, v):
        """Validate boolean flags are actually boolean."""
        if v is not None and not isinstance(v, bool):
            raise ValueError(f"Flag must be boolean (T/F), got {type(v)}")
        return v
