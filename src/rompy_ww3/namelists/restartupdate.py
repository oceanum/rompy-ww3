"""UPRSTR_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel
from .validation import validate_date_format


class RestartUpdate(NamelistBaseModel):
    """UPRSTR_NML namelist for WW3.

    The UPRSTR_NML namelist defines restart file update parameters for WAVEWATCH III.
    This namelist is used to update existing restart files with new data, allowing
    for adjustments to restart conditions without reinitializing the entire model state.
    
    The namelist allows updating various components of the restart file using different
    methods (replace, add, multiply) and provides control over which fields to update.
    """

    # Update configuration
    update_time: Optional[str] = Field(
        default=None,
        description=(
            "Time for restart file update in format 'YYYYMMDD HHMMSS'. "
            "This specifies when to perform the restart file update during the simulation. "
            "Example: '20100101 000000' for January 1, 2010 at 00:00:00 UTC."
        )
    )
    update_stride: Optional[str] = Field(
        default=None,
        description=(
            "Time stride for restart file updates in seconds as a string. "
            "This specifies the time interval between restart file updates. "
            "Example: '3600' for hourly updates, '21600' for 6-hourly updates."
        )
    )

    # File configuration
    input_restart: Optional[str] = Field(
        default=None,
        description=(
            "Path to the input restart file that will be updated. "
            "This should point to an existing restart file that will serve as the base "
            "for the update operation."
        )
    )
    output_restart: Optional[str] = Field(
        default=None,
        description=(
            "Path to the output restart file that will contain the updated data. "
            "The updated restart information will be written to this file."
        )
    )

    # Fields to update
    wave_field: Optional[bool] = Field(
        default=None,
        description="Flag to update wave field (T/F). If true, the wave spectral data will be updated."
    )
    water_level: Optional[bool] = Field(
        default=None,
        description="Flag to update water level (T/F). If true, the water level data will be updated."
    )
    current: Optional[bool] = Field(
        default=None,
        description="Flag to update current (T/F). If true, the ocean current data will be updated."
    )
    ice: Optional[bool] = Field(
        default=None,
        description="Flag to update ice fields (T/F). If true, ice-related data will be updated."
    )
    wind: Optional[bool] = Field(
        default=None,
        description="Flag to update wind fields (T/F). If true, wind field data will be updated."
    )

    # Update method
    update_method: Optional[str] = Field(
        default=None,
        description=(
            "Method for updating the restart fields:\n"
            "  'replace': Replace the field values with new values\n"
            "  'add': Add the new values to the existing field values\n"
            "  'multiply': Multiply the existing field values by the new values"
        )
    )

    @field_validator('update_time')
    @classmethod
    def validate_update_time_format(cls, v):
        """Validate date format for update_time."""
        if v is not None:
            return validate_date_format(v)
        return v

    @field_validator('update_method')
    @classmethod
    def validate_update_method(cls, v):
        """Validate update method is valid."""
        if v is not None:
            valid_methods = {'replace', 'add', 'multiply', 'REPLACE', 'ADD', 'MULTIPLY'}
            if v.upper() not in valid_methods:
                raise ValueError(f"Update method must be one of replace, add, multiply, got {v}")
        return v.upper() if v is not None else v

    @field_validator('wave_field', 'water_level', 'current', 'ice', 'wind')
    @classmethod
    def validate_boolean_flags(cls, v):
        """Validate boolean flags are actually boolean."""
        if v is not None and not isinstance(v, bool):
            raise ValueError(f"Flag must be boolean (T/F), got {type(v)}")
        return v
