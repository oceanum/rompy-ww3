"""UNST_NML namelist implementation for WW3."""

from typing import Optional, Union
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel
from ..core.data import WW3DataBlob


class Unst(NamelistBaseModel):
    """UNST_NML namelist for WW3.

    The UNST_NML namelist defines the parameters for unstructured grids in WAVEWATCH III.
    Unstructured grids use triangular elements to represent the domain, allowing for
    flexible resolution that can be refined in areas of interest.

    The unstructured grid file must be a GMESH grid file containing node and element lists.
    The depth values must have negative values under the mean sea level, and the map values
    define different types of grid points as documented below.
    """

    sf: Optional[float] = Field(
        default=1.0,
        description=(
            "Unstructured grid scale factor used to convert from file values to model coordinates. "
            "The final coordinate value is calculated as: scale_factor * value_read. "
            "For depth files, use a negative value to ensure depths are negative (below sea level)."
        ),
    )
    filename: Optional[Union[str, WW3DataBlob]] = Field(
        default="unset",
        description=(
            "Filename or data blob containing the unstructured grid data. This file should be "
            "a GMESH grid file format containing the node and element lists for the triangular mesh."
        ),
    )
    idf: Optional[int] = Field(
        default=20,
        description=(
            "File unit number for the unstructured grid file. Each file in WW3 is assigned a unique "
            "unit number to distinguish between different input files during processing."
        ),
        ge=1,  # Must be positive file unit number
    )
    idla: Optional[int] = Field(
        default=1,
        description=(
            "Layout indicator for reading unstructured grid data:\n"
            "  1: Read line-by-line from bottom to top (default)\n"
            "  2: Like 1, with a single read statement\n"
            "  3: Read line-by-line from top to bottom\n"
            "  4: Like 3, with a single read statement"
        ),
        ge=1,
        le=4,
    )
    idfm: Optional[int] = Field(
        default=1,
        description=(
            "Format indicator for reading unstructured grid data:\n"
            "  1: Free format (default)\n"
            "  2: Fixed format\n"
            "  3: Unformatted"
        ),
        ge=1,
        le=3,
    )
    format: Optional[str] = Field(
        default="(....)",
        description=(
            "Formatted read format specification, like '(20f10.2)' for float type. "
            "Use '(....)' for auto detection of the format. This specifies how the "
            "unstructured grid values should be read from the file."
        ),
    )
    ugobcfile: Optional[str] = Field(
        default="unset",
        description=(
            "Additional boundary list file with UGOBCFILE in namelist. This file contains "
            "extra open boundary information for the unstructured grid. An example is given "
            "in the WW3 regression test ww3_tp2.7."
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
