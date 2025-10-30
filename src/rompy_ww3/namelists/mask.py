"""MASK_NML namelist implementation for WW3."""

from typing import Optional, Union
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel
from ..core.data import WW3DataBlob


class Mask(NamelistBaseModel):
    """MASK_NML namelist for WW3.

    The MASK_NML namelist defines the point status map for WAVEWATCH III grids.
    The mask defines the status of each grid point as land, sea, boundary, etc.
    This is used to determine which points participate in the wave modeling.
    
    If no mask is defined, the INBOUND option can be used to set active boundaries.
    The legend for the input map is:
     -2 : Excluded boundary point (covered by ice)
     -1 : Excluded sea point (covered by ice)
      0 : Excluded land point
      1 : Sea point
      2 : Active boundary point
      3 : Excluded grid point
      7 : Ice point
    """

    filename: Optional[Union[str, WW3DataBlob]] = Field(
        default=None,
        description=(
            "Filename or data blob containing the mask data for the grid. This file should contain "
            "the point status values in the format specified by the idfm and format parameters."
        )
    )
    idf: Optional[int] = Field(
        default=None,
        description=(
            "File unit number for the mask file. Each file in WW3 is assigned a unique "
            "unit number to distinguish between different input files during processing."
        ),
        ge=1  # Must be positive file unit number
    )
    idla: Optional[int] = Field(
        default=None,
        description=(
            "Layout indicator for reading mask data:\n"
            "  1: Read line-by-line from bottom to top (default)\n"
            "  2: Like 1, but with a single read statement\n"
            "  3: Read line-by-line from top to bottom\n"
            "  4: Like 3, but with a single read statement"
        ),
        ge=1,
        le=4
    )
    idfm: Optional[int] = Field(
        default=None,
        description=(
            "Format indicator for reading mask data:\n"
            "  1: Free format (default)\n"
            "  2: Fixed format\n"
            "  3: Unformatted"
        ),
        ge=1,
        le=3
    )
    format: Optional[str] = Field(
        default=None,
        description=(
            "Formatted read format specification, like '(f10.6)' for float type. "
            "Use '(....)' for auto detection of the format. This specifies how the "
            "mask values should be read from the file."
        )
    )

    @field_validator('idf')
    @classmethod
    def validate_file_unit(cls, v):
        """Validate file unit number."""
        if v is not None:
            if v <= 0:
                raise ValueError(f"File unit number must be positive, got {v}")
        return v

    @field_validator('idla')
    @classmethod
    def validate_idla(cls, v):
        """Validate layout indicator."""
        if v is not None and v not in [1, 2, 3, 4]:
            raise ValueError(f"Layout indicator (idla) must be between 1 and 4, got {v}")
        return v

    @field_validator('idfm')
    @classmethod
    def validate_idfm(cls, v):
        """Validate format indicator."""
        if v is not None and v not in [1, 2, 3]:
            raise ValueError(f"Format indicator (idfm) must be 1, 2, or 3, got {v}")
        return v
