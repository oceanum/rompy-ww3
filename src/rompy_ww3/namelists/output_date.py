"""OUTPUT_DATE_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel
from .validation import validate_date_format


class OutputDateField(NamelistBaseModel):
    """Field output date parameters for WW3.

    The DATE%FIELD namelist defines the timing parameters for field output in WW3.
    If time stride is equal '0', then output is disabled.
    Time stride is given in seconds.
    """

    start: Optional[str] = Field(
        default=None,
        description=(
            "Field output start time in format 'YYYYMMDD HHMMSS'. "
            "This specifies when to begin writing field output during the simulation. "
            "Example: '20100101 000000' for January 1, 2010 at 00:00:00 UTC."
        )
    )
    stride: Optional[str] = Field(
        default=None,
        description=(
            "Field output time stride in seconds as a string. "
            "This specifies the time interval between field output writes. "
            "If set to '0', field output is disabled. "
            "Example: '3600' for hourly output, '21600' for 6-hourly output."
        )
    )
    stop: Optional[str] = Field(
        default=None,
        description=(
            "Field output stop time in format 'YYYYMMDD HHMMSS'. "
            "This specifies when to stop writing field output during the simulation. "
            "Example: '20101231 000000' for December 31, 2010 at 00:00:00 UTC."
        )
    )

    @field_validator('start', 'stop')
    @classmethod
    def validate_date_fields(cls, v):
        """Validate date format for start and stop fields."""
        if v is not None:
            return validate_date_format(v)
        return v


class OutputDatePoint(NamelistBaseModel):
    """Point output date parameters for WW3.

    The DATE%POINT namelist defines the timing parameters for point output in WW3.
    If time stride is equal '0', then output is disabled.
    Time stride is given in seconds.
    """

    start: Optional[str] = Field(
        default=None,
        description=(
            "Point output start time in format 'YYYYMMDD HHMMSS'. "
            "This specifies when to begin writing point output during the simulation. "
            "Example: '20100101 000000' for January 1, 2010 at 00:00:00 UTC."
        )
    )
    stride: Optional[str] = Field(
        default=None,
        description=(
            "Point output time stride in seconds as a string. "
            "This specifies the time interval between point output writes. "
            "If set to '0', point output is disabled. "
            "Example: '3600' for hourly output, '21600' for 6-hourly output."
        )
    )
    stop: Optional[str] = Field(
        default=None,
        description=(
            "Point output stop time in format 'YYYYMMDD HHMMSS'. "
            "This specifies when to stop writing point output during the simulation. "
            "Example: '20101231 000000' for December 31, 2010 at 00:00:00 UTC."
        )
    )

    @field_validator('start', 'stop')
    @classmethod
    def validate_date_fields(cls, v):
        """Validate date format for start and stop fields."""
        if v is not None:
            return validate_date_format(v)
        return v


class OutputDateTrack(NamelistBaseModel):
    """Track output date parameters for WW3.

    The DATE%TRACK namelist defines the timing parameters for track output in WW3.
    If time stride is equal '0', then output is disabled.
    Time stride is given in seconds.
    """

    start: Optional[str] = Field(
        default=None,
        description=(
            "Track output start time in format 'YYYYMMDD HHMMSS'. "
            "This specifies when to begin writing track output during the simulation. "
            "Example: '20100101 000000' for January 1, 2010 at 00:00:00 UTC."
        )
    )
    stride: Optional[str] = Field(
        default=None,
        description=(
            "Track output time stride in seconds as a string. "
            "This specifies the time interval between track output writes. "
            "If set to '0', track output is disabled. "
            "Example: '3600' for hourly output, '21600' for 6-hourly output."
        )
    )
    stop: Optional[str] = Field(
        default=None,
        description=(
            "Track output stop time in format 'YYYYMMDD HHMMSS'. "
            "This specifies when to stop writing track output during the simulation. "
            "Example: '20101231 000000' for December 31, 2010 at 00:00:00 UTC."
        )
    )

    @field_validator('start', 'stop')
    @classmethod
    def validate_date_fields(cls, v):
        """Validate date format for start and stop fields."""
        if v is not None:
            return validate_date_format(v)
        return v


class OutputDateRestart(NamelistBaseModel):
    """Restart output date parameters for WW3.

    The DATE%RESTART namelist defines the timing parameters for restart output in WW3.
    If time stride is equal '0', then output is disabled.
    Time stride is given in seconds.
    """

    start: Optional[str] = Field(
        default=None,
        description=(
            "Restart output start time in format 'YYYYMMDD HHMMSS'. "
            "This specifies when to begin writing restart output during the simulation. "
            "Example: '20100101 000000' for January 1, 2010 at 00:00:00 UTC."
        )
    )
    stride: Optional[str] = Field(
        default=None,
        description=(
            "Restart output time stride in seconds as a string. "
            "This specifies the time interval between restart output writes. "
            "If set to '0', restart output is disabled. "
            "Example: '43200' for 12-hourly output, '86400' for daily output."
        )
    )
    stop: Optional[str] = Field(
        default=None,
        description=(
            "Restart output stop time in format 'YYYYMMDD HHMMSS'. "
            "This specifies when to stop writing restart output during the simulation. "
            "Example: '20101231 000000' for December 31, 2010 at 00:00:00 UTC."
        )
    )

    @field_validator('start', 'stop')
    @classmethod
    def validate_date_fields(cls, v):
        """Validate date format for start and stop fields."""
        if v is not None:
            return validate_date_format(v)
        return v


class OutputDateBoundary(NamelistBaseModel):
    """Boundary output date parameters for WW3.

    The DATE%BOUNDARY namelist defines the timing parameters for boundary output in WW3.
    If time stride is equal '0', then output is disabled.
    Time stride is given in seconds.
    """

    start: Optional[str] = Field(
        default=None,
        description=(
            "Boundary output start time in format 'YYYYMMDD HHMMSS'. "
            "This specifies when to begin writing boundary output during the simulation. "
            "Example: '20100101 000000' for January 1, 2010 at 00:00:00 UTC."
        )
    )
    stride: Optional[str] = Field(
        default=None,
        description=(
            "Boundary output time stride in seconds as a string. "
            "This specifies the time interval between boundary output writes. "
            "If set to '0', boundary output is disabled. "
            "Example: '3600' for hourly output, '21600' for 6-hourly output."
        )
    )
    stop: Optional[str] = Field(
        default=None,
        description=(
            "Boundary output stop time in format 'YYYYMMDD HHMMSS'. "
            "This specifies when to stop writing boundary output during the simulation. "
            "Example: '20101231 000000' for December 31, 2010 at 00:00:00 UTC."
        )
    )

    @field_validator('start', 'stop')
    @classmethod
    def validate_date_fields(cls, v):
        """Validate date format for start and stop fields."""
        if v is not None:
            return validate_date_format(v)
        return v


class OutputDatePartition(NamelistBaseModel):
    """Partition output date parameters for WW3.

    The DATE%PARTITION namelist defines the timing parameters for partition output in WW3.
    If time stride is equal '0', then output is disabled.
    Time stride is given in seconds.
    """

    start: Optional[str] = Field(
        default=None,
        description=(
            "Partition output start time in format 'YYYYMMDD HHMMSS'. "
            "This specifies when to begin writing partition output during the simulation. "
            "Example: '20100101 000000' for January 1, 2010 at 00:00:00 UTC."
        )
    )
    stride: Optional[str] = Field(
        default=None,
        description=(
            "Partition output time stride in seconds as a string. "
            "This specifies the time interval between partition output writes. "
            "If set to '0', partition output is disabled. "
            "Example: '3600' for hourly output, '21600' for 6-hourly output."
        )
    )
    stop: Optional[str] = Field(
        default=None,
        description=(
            "Partition output stop time in format 'YYYYMMDD HHMMSS'. "
            "This specifies when to stop writing partition output during the simulation. "
            "Example: '20101231 000000' for December 31, 2010 at 00:00:00 UTC."
        )
    )

    @field_validator('start', 'stop')
    @classmethod
    def validate_date_fields(cls, v):
        """Validate date format for start and stop fields."""
        if v is not None:
            return validate_date_format(v)
        return v


class OutputDateCoupling(NamelistBaseModel):
    """Coupling output date parameters for WW3.

    The DATE%COUPLING namelist defines the timing parameters for coupling output in WW3.
    If time stride is equal '0', then output is disabled.
    Time stride is given in seconds.
    """

    start: Optional[str] = Field(
        default=None,
        description=(
            "Coupling output start time in format 'YYYYMMDD HHMMSS'. "
            "This specifies when to begin writing coupling output during the simulation. "
            "Example: '20100101 000000' for January 1, 2010 at 00:00:00 UTC."
        )
    )
    stride: Optional[str] = Field(
        default=None,
        description=(
            "Coupling output time stride in seconds as a string. "
            "This specifies the time interval between coupling output writes. "
            "If set to '0', coupling output is disabled. "
            "Example: '3600' for hourly output, '21600' for 6-hourly output."
        )
    )
    stop: Optional[str] = Field(
        default=None,
        description=(
            "Coupling output stop time in format 'YYYYMMDD HHMMSS'. "
            "This specifies when to stop writing coupling output during the simulation. "
            "Example: '20101231 000000' for December 31, 2010 at 00:00:00 UTC."
        )
    )

    @field_validator('start', 'stop')
    @classmethod
    def validate_date_fields(cls, v):
        """Validate date format for start and stop fields."""
        if v is not None:
            return validate_date_format(v)
        return v


class OutputDate(NamelistBaseModel):
    """DATE section of OUTPUT_DATE_NML for WW3 (single-grid).

    The OUTPUT_DATE_NML namelist defines the output timing parameters for 
    single-grid WAVEWATCH III runs. This namelist is read by the ww3_shel program.

    The namelist contains sections for:
    - FIELD: Field output timing (start, stride, stop times)
    - POINT: Point output timing (start, stride, stop times)
    - TRACK: Track output timing (start, stride, stop times)
    - RESTART: Restart output timing (start, stride, stop times)
    - BOUNDARY: Boundary output timing (start, stride, stop times)
    - PARTITION: Partition output timing (start, stride, stop times)
    - COUPLING: Coupling output timing (start, stride, stop times)

    Timing parameters follow the format:
    - Start/Stop times in 'YYYYMMDD HHMMSS' format
    - Stride in seconds as a string (e.g., '3600' for 1 hour)
    - Setting stride to '0' disables that output type
    """

    field: Optional[OutputDateField] = Field(
        default=None, 
        description="Field output date parameters defining when and how frequently field output is written"
    )
    point: Optional[OutputDatePoint] = Field(
        default=None, 
        description="Point output date parameters defining when and how frequently point output is written"
    )
    track: Optional[OutputDateTrack] = Field(
        default=None, 
        description="Track output date parameters defining when and how frequently track output is written"
    )
    restart: Optional[OutputDateRestart] = Field(
        default=None, 
        description="Restart output date parameters defining when and how frequently restart output is written"
    )
    boundary: Optional[OutputDateBoundary] = Field(
        default=None, 
        description="Boundary output date parameters defining when and how frequently boundary output is written"
    )
    partition: Optional[OutputDatePartition] = Field(
        default=None, 
        description="Partition output date parameters defining when and how frequently partition output is written"
    )
    coupling: Optional[OutputDateCoupling] = Field(
        default=None, 
        description="Coupling output date parameters defining when and how frequently coupling output is written"
    )


class AllDate(NamelistBaseModel):
    """ALLDATE section of OUTPUT_DATE_NML for WW3 (multi-grid).

    The ALLDATE section applies output date parameters uniformly to all grids in multi-grid runs.
    """

    field: Optional[OutputDateField] = Field(
        default=None, 
        description="Field output date parameters applied to all grids in multi-grid runs"
    )
    point: Optional[OutputDatePoint] = Field(
        default=None, 
        description="Point output date parameters applied to all grids in multi-grid runs"
    )
    track: Optional[OutputDateTrack] = Field(
        default=None, 
        description="Track output date parameters applied to all grids in multi-grid runs"
    )
    restart: Optional[OutputDateRestart] = Field(
        default=None, 
        description="Restart output date parameters applied to all grids in multi-grid runs"
    )
    boundary: Optional[OutputDateBoundary] = Field(
        default=None, 
        description="Boundary output date parameters applied to all grids in multi-grid runs"
    )
    partition: Optional[OutputDatePartition] = Field(
        default=None, 
        description="Partition output date parameters applied to all grids in multi-grid runs"
    )
    coupling: Optional[OutputDateCoupling] = Field(
        default=None, 
        description="Coupling output date parameters applied to all grids in multi-grid runs"
    )


class IDate(NamelistBaseModel):
    """IDATE(I) section of OUTPUT_DATE_NML for WW3 (multi-grid).

    The IDATE(I) section applies output date parameters to a specific grid I in multi-grid runs.
    """

    field: Optional[OutputDateField] = Field(
        default=None, 
        description="Field output date parameters for specific grid I in multi-grid runs"
    )
    point: Optional[OutputDatePoint] = Field(
        default=None, 
        description="Point output date parameters for specific grid I in multi-grid runs"
    )
    track: Optional[OutputDateTrack] = Field(
        default=None, 
        description="Track output date parameters for specific grid I in multi-grid runs"
    )
    restart: Optional[OutputDateRestart] = Field(
        default=None, 
        description="Restart output date parameters for specific grid I in multi-grid runs"
    )
    boundary: Optional[OutputDateBoundary] = Field(
        default=None, 
        description="Boundary output date parameters for specific grid I in multi-grid runs"
    )
    partition: Optional[OutputDatePartition] = Field(
        default=None, 
        description="Partition output date parameters for specific grid I in multi-grid runs"
    )
    coupling: Optional[OutputDateCoupling] = Field(
        default=None, 
        description="Coupling output date parameters for specific grid I in multi-grid runs"
    )
