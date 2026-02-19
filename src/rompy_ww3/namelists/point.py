"""POINT_NML and FILE_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel
from .validation import validate_date_format


class Point(NamelistBaseModel):
    """POINT_NML namelist for WW3.

    The POINT_NML namelist defines the point output configuration for WAVEWATCH III post-processing.
    This namelist controls how point output is generated from specific locations in the model domain.

    Point output can include various wave parameters for specific locations (buoys, stations, etc.)
    and can be written to NetCDF files with various formatting and temporal options.
    """

    timestart: Optional[str] = Field(
        default=None,
        description=(
            "Start date for the point output in format 'YYYYMMDD HHMMSS'. "
            "This specifies when to begin writing point output during the post-processing. "
            "Example: '20100101 000000' for January 1, 2010 at 00:00:00 UTC."
        ),
    )
    timestride: Optional[int] = Field(
        default=None,
        description=(
            "Time stride for the point output in seconds. "
            "This specifies the time interval between point output writes. "
            "Example: 3600 for hourly output, 21600 for 6-hourly output."
        ),
    )
    timecount: Optional[int] = Field(
        default=None,
        description=(
            "Number of time steps for the point output. "
            "This specifies the total number of time steps for which point output will be generated. "
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
            "List of point indices to output. Options are:\n"
            "  'all': Output all points in the point file\n"
            "  '1 2 3': Space-separated list of specific point indices\n"
            "  '1-3': Range notation for point indices (if supported)\n"
            "This specifies which points from the point file will be included in the output."
        ),
    )
    samefile: Optional[bool] = Field(
        default=None,
        description=(
            "Flag to put all points in the same file (T) or separate files (F). "
            "When True, all requested point output is written to a single NetCDF file. "
            "When False, each point may be written to separate files."
        ),
    )
    buffer: Optional[int] = Field(
        default=None,
        description=(
            "Number of points to process per pass. This controls memory usage during "
            "point output processing by limiting how many points are processed simultaneously. "
            "Higher values use more memory but may be faster. "
            "Lower values use less memory but may be slower."
        ),
        ge=1,
    )
    type: Optional[int] = Field(
        default=None,
        description=(
            "Output type for point data:\n"
            "  0: Inventory (basic point information)\n"
            "  1: Spectra (full wave spectra)\n"
            "  2: Mean parameters (HS, Tp, etc.)\n"
            "  3: Source terms (wind input, dissipation, etc.)\n"
            "This determines the type and amount of data output for each point."
        ),
        ge=0,
        le=3,
    )
    dimorder: Optional[bool] = Field(
        default=None,
        description=(
            "Dimension ordering for point output NetCDF files:\n"
            "  T: Time,Station (time varies fastest)\n"
            "  F: Station,Time (station varies fastest)\n"
            "This controls how data dimensions are organized in the output files."
        ),
    )

    @field_validator("timestart")
    @classmethod
    def validate_timestart_format(cls, v):
        """Validate date format for timestart."""
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
        if v is not None and v not in [0, 1, 2, 3]:
            raise ValueError(f"Type must be 0, 1, 2, or 3, got {v}")
        return v

    @field_validator("buffer")
    @classmethod
    def validate_buffer(cls, v):
        """Validate buffer value."""
        if v is not None and v < 1:
            raise ValueError(f"Buffer must be at least 1, got {v}")
        return v

    @field_validator("samefile", "dimorder")
    @classmethod
    def validate_boolean_flags(cls, v):
        """Validate boolean flags are actually boolean."""
        if v is not None and not isinstance(v, bool):
            raise ValueError(f"Flag must be boolean (T/F), got {type(v)}")
        return v


class PointFile(NamelistBaseModel):
    """FILE_NML namelist for WW3 point output.

    Defines the content and naming of the point output file.
    """

    prefix: Optional[str] = Field(
        default=None,
        description=(
            "Prefix for the point output file name. This is used to create output file names "
            "for the point data. The actual output files will use this prefix followed by "
            "applicable extensions, timestamps, and numerical identifiers. "
            "Example: 'points.' produces files like 'points.20100101.nc'"
        ),
    )
    netcdf: Optional[int] = Field(
        default=None,
        description=(
            "NetCDF version to use for point output files:\n"
            "  3: NetCDF-3 format (classic)\n"
            "  4: NetCDF-4 format (with HDF5 features)\n"
            "This specifies the version of NetCDF format to use for the point output files."
        ),
        ge=3,
        le=4,
    )

    def get_namelist_name(self) -> str:
        """Return the specific namelist name for FILE_NML."""
        return "FILE_NML"

    @field_validator("prefix")
    @classmethod
    def validate_prefix(cls, v):
        """Validate prefix is not empty."""
        if v is not None and v.strip() == "":
            raise ValueError("Output file prefix cannot be empty")
        return v

    @field_validator("netcdf")
    @classmethod
    def validate_netcdf_version(cls, v):
        """Validate NetCDF version."""
        if v is not None and v not in [3, 4]:
            raise ValueError(f"NetCDF version must be 3 or 4, got {v}")
        return v
