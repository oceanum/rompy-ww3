"""OBST_NML namelist implementation for WW3."""

from typing import Optional, Union
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel
from ..core.data import WW3DataBlob
from .enums import LAYOUT_INDICATOR, FORMAT_INDICATOR, parse_enum


class Obstacle(NamelistBaseModel):
    """OBST_NML namelist for WW3.

    The OBST_NML namelist defines the obstruction map for WAVEWATCH III grids.
    This map is used only if &MISC FLAGTR = 1 in param.nml (transparencies at cell boundaries)
    or if &MISC FLAGTR = 2 in param.nml (transparencies at cell centers)
    or if &MISC FLAGTR = 3 in param.nml (transparencies at cell boundaries with continuous ice)
    or if &MISC FLAGTR = 4 in param.nml (transparencies at cell centers with continuous ice).

    The obstruction values represent the transparency or transmission coefficient of obstacles
    like vegetation, ice, structures, etc. The scale factor converts the input values to the
    appropriate obstruction values needed by WW3.

    In the case of unstructured grids, no obstruction file can be added.

    If the file unit number equals 10, then data is read from this file with special handling.
    No comment lines are allowed within the data input.
    """

    sf: Optional[float] = Field(
        default=None,
        description=(
            "Scale factor to apply to obstacle values from the input file. "
            "The final obstruction value is calculated as: value = value_read * scale_factor. "
            "This factor is used to convert the values from the input file to appropriate "
            "obstruction values for WW3's transmission calculations."
        ),
    )
    filename: Optional[Union[str, WW3DataBlob]] = Field(
        default=None,
        description=(
            "Filename or data blob containing the obstruction data for the grid. This file should contain "
            "the obstruction/transmission values in the format specified by the idfm and format parameters."
        ),
    )
    idf: Optional[int] = Field(
        default=None,
        description=(
            "File unit number for the obstacle file. Each file in WW3 is assigned a unique "
            "unit number to distinguish between different input files during processing."
        ),
        ge=1,  # Must be positive file unit number
    )
    idla: Optional[LAYOUT_INDICATOR] = Field(
        default=None,
        description=(
            "Layout indicator for reading obstacle data:\n"
            "  1: Read line-by-line from bottom to top (default)\n"
            "  2: Like 1, but with a single read statement\n"
            "  3: Read line-by-line from top to bottom\n"
            "  4: Like 3, but with a single read statement"
        ),
    )
    idfm: Optional[FORMAT_INDICATOR] = Field(
        default=None,
        description=(
            "Format indicator for reading obstacle data:\n"
            "  1: Free format (default)\n"
            "  2: Fixed format\n"
            "  3: Unformatted"
        ),
    )
    format: Optional[str] = Field(
        default=None,
        description=(
            "Formatted read format specification, like '(f10.6)' for float type. "
            "Use '(....)' for auto detection of the format. This specifies how the "
            "obstacle values should be read from the file."
        ),
    )

    @field_validator("sf")
    @classmethod
    def validate_scale_factor(cls, v):
        """Validate scale factor is not zero."""
        if v is not None:
            if v == 0:
                raise ValueError(f"Scale factor must not be zero, got {v}")
        return v

    @field_validator("idf")
    @classmethod
    def validate_file_unit(cls, v):
        """Validate file unit number."""
        if v is not None:
            if v <= 0:
                raise ValueError(f"File unit number must be positive, got {v}")
        return v

    @field_validator("idla", mode="before")
    @classmethod
    def validate_idla(cls, v):
        """Validate layout indicator."""
        if v is None:
            return v
        return parse_enum(LAYOUT_INDICATOR, v)

    @field_validator("idfm", mode="before")
    @classmethod
    def validate_idfm(cls, v):
        """Validate format indicator."""
        if v is None:
            return v
        return parse_enum(FORMAT_INDICATOR, v)
