"""TRACK_NML and FILE_NML namelist implementation for WW3."""

from datetime import datetime
from typing import Optional
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel


class Track(NamelistBaseModel):
    """TRACK_NML namelist for WW3.

    The TRACK_NML namelist defines the track output configuration for WAVEWATCH III.
    This namelist sets up the temporal parameters for track output processing.

    Track output is used to generate output for specific tracks or trajectories
    rather than regular grid points or points specified in a file.
    """

    timestart: Optional[datetime] = Field(
        default=None,
        description=(
            "Start date for the track output. Accepts datetime objects or strings in format 'YYYYMMDD HHMMSS'. "
            "This specifies when to begin writing track output during the simulation. "
            "Example: datetime(2010, 1, 1, 0, 0, 0) or '20100101 000000' for January 1, 2010 at 00:00:00 UTC."
        ),
    )
    timestride: Optional[int] = Field(
        default=None,
        description=(
            "Time stride for the track output in seconds. "
            "This specifies the time interval between track output writes. "
            "Example: 3600 for hourly output, 21600 for 6-hourly output."
        ),
    )
    timecount: Optional[int] = Field(
        default=None,
        description=(
            "Number of time steps for the track output. "
            "This specifies the total number of time steps for which track output will be generated. "
        ),
    )
    timesplit: Optional[int] = Field(
        default=None,
        description=(
            "Time splitting option for output file management:\n"
            "  4: Yearly splitting\n"
            "  6: Monthly splitting\n"
            "  8: Daily splitting\n"
            "  10: Hourly splitting\n"
            "This controls how output files are split over time periods."
        ),
        ge=4,
        le=10,
    )

    @field_validator("timestart")
    @classmethod
    def validate_timezone(cls, v):
        """Validate that datetime is timezone-naive."""
        if v is not None and v.tzinfo is not None:
            raise ValueError(
                "Timezone-aware datetimes not supported - use naive datetimes only"
            )
        return v


class TrackFile(NamelistBaseModel):
    """FILE_NML namelist for WW3 track output.

    Defines the content and naming of the track output file.
    """

    prefix: Optional[str] = Field(
        default=None,
        description=(
            "Prefix for the track output file name. This is used to create output file names "
            "for the track data. The actual output files will use this prefix followed by "
            "applicable extensions and numerical identifiers."
        ),
    )
    netcdf: Optional[int] = Field(
        default=None,
        description=(
            "NetCDF version for track output:\n"
            "  3: NetCDF-3 format (classic)\n"
            "  4: NetCDF-4 format (with HDF5 features)\n"
            "This specifies the version of NetCDF format to use for the output files."
        ),
        ge=3,
        le=4,
    )

    @field_validator("prefix")
    @classmethod
    def validate_prefix(cls, v):
        """Validate prefix is not empty if provided."""
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
