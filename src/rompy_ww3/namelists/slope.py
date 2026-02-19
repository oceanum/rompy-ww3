"""SLOPE_NML namelist implementation for WW3."""

from typing import Optional, Union
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel
from ..core.data import WW3DataBlob


class Slope(NamelistBaseModel):
    """SLOPE_NML namelist for WW3.

    The SLOPE_NML namelist defines the reflection slope map for WAVEWATCH III grids.
    This map is used only if &REF1 REFMAP = 2 is defined in param.nml.

    The reflection slope values represent the characteristics of coastal slopes that
    affect wave reflection and dissipation. The scale factor converts the input values
    to the appropriate slope values needed by WW3's reflection calculations.

    In the case of unstructured grids, no reflection slope file can be added.
    """

    sf: Optional[float] = Field(
        default=None,
        description=(
            "Scale factor to apply to slope values from the input file. "
            "The final slope value is calculated as: value = value_read * scale_factor. "
            "This factor is used to convert the values from the input file to appropriate "
            "slope values for WW3's reflection calculations."
        ),
    )
    filename: Optional[Union[str, WW3DataBlob]] = Field(
        default=None,
        description=(
            "Filename or data blob containing the reflection slope data for the grid. This file should contain "
            "the slope values in the format specified by the idfm and format parameters."
        ),
    )
    idf: Optional[int] = Field(
        default=None,
        description=(
            "File unit number for the slope file. Each file in WW3 is assigned a unique "
            "unit number to distinguish between different input files during processing."
        ),
        ge=1,  # Must be positive file unit number
    )
    idla: Optional[int] = Field(
        default=None,
        description=(
            "Layout indicator for reading slope data:\n"
            "  1: Read line-by-line from bottom to top (default)\n"
            "  2: Like 1, but with a single read statement\n"
            "  3: Read line-by-line from top to bottom\n"
            "  4: Like 3, but with a single read statement"
        ),
        ge=1,
        le=4,
    )
    idfm: Optional[int] = Field(
        default=None,
        description=(
            "Format indicator for reading slope data:\n"
            "  1: Free format (default)\n"
            "  2: Fixed format\n"
            "  3: Unformatted"
        ),
        ge=1,
        le=3,
    )
    format: Optional[str] = Field(
        default=None,
        description=(
            "Formatted read format specification, like '(f10.6)' for float type. "
            "Use '(....)' for auto detection of the format. This specifies how the "
            "slope values should be read from the file."
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

    @field_validator("idla")
    @classmethod
    def validate_idla(cls, v):
        """Validate layout indicator."""
        if v is not None and v not in [1, 2, 3, 4]:
            raise ValueError(
                f"Layout indicator (idla) must be between 1 and 4, got {v}"
            )
        return v

    @field_validator("idfm")
    @classmethod
    def validate_idfm(cls, v):
        """Validate format indicator."""
        if v is not None and v not in [1, 2, 3]:
            raise ValueError(f"Format indicator (idfm) must be 1, 2, or 3, got {v}")
        return v
