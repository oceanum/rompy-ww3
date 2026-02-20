"""SMC_NML namelist implementation for WW3."""

from typing import Optional, Union
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel
from ..core.data import WW3DataBlob
from .enums import LAYOUT_INDICATOR, FORMAT_INDICATOR, parse_enum


class SMCFile(NamelistBaseModel):
    """File structure for SMC grid data in WW3.

    This structure defines how SMC (Spherical Multiple-Cell) grid data is read from files.
    It includes file specifications, unit numbers, and format information.
    """

    filename: Optional[Union[str, WW3DataBlob]] = Field(
        default="unset",
        description=(
            "Filename or data blob containing the SMC grid data. This file contains "
            "the specific SMC grid information (cells, sides, obstructions, etc.) "
            "required for the spherical multiple-cell grid configuration."
        ),
    )
    idf: Optional[int] = Field(
        default=None,
        description=(
            "File unit number for the SMC data file. Each file in WW3 is assigned a unique "
            "unit number to distinguish between different input files during processing."
        ),
        ge=1,  # Must be positive file unit number
    )
    idla: Optional[LAYOUT_INDICATOR] = Field(
        default=1,
        description=(
            "Layout indicator for reading SMC data:\n"
            "  1: Read line-by-line from bottom to top (default)\n"
            "  2: Like 1, but with a single read statement\n"
            "  3: Read line-by-line from top to bottom\n"
            "  4: Like 3, but with a single read statement"
        ),
    )
    idfm: Optional[FORMAT_INDICATOR] = Field(
        default=1,
        description=(
            "Format indicator for reading SMC data:\n"
            "  1: Free format (default)\n"
            "  2: Fixed format\n"
            "  3: Unformatted"
        ),
    )
    format: Optional[str] = Field(
        default="(....)",
        description=(
            "Formatted read format specification, like '(f10.6)' for float type. "
            "Use '(....)' for auto detection of the format. This specifies how the "
            "SMC grid values should be read from the file."
        ),
    )

    @field_validator("idf")
    @classmethod
    def validate_file_unit(cls, v):
        """Validate file unit number."""
        if v is not None:
            if v <= 0:
                raise ValueError(f"File unit number (idf) must be positive, got {v}")
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


class Smc(NamelistBaseModel):
    """SMC_NML namelist for WW3.

    The SMC_NML namelist defines the parameters for spherical multiple-cell (SMC) grids in WAVEWATCH III.
    SMC grids use a multi-resolution approach with nested grids for different regions.

    The SMC grid configuration involves multiple files containing:
    - MCELS: SMC cell arrays (MCels.dat)
    - ISIDE & JSIDE: Face arrays (ISide.dat, JSide.dat)
    - SUBTR: Obstruction ratio data (Subtr.dat)
    - BUNDY: Boundary cell list file (Bundy.dat) - only needed when NBISMC > 0
    - MBArc: Extra cell arrays for Arctic part (MBArc.dat) - if ARC switch selected
    - AISid & AJSid: Extra face arrays for Arctic part (AISid.dat, AJSid.dat)

    These grids are especially useful for global applications where higher resolution is
    needed in certain areas while maintaining coarser resolution elsewhere.
    """

    mcel: Optional[SMCFile] = Field(
        default=None,
        description=(
            "MCels (Multiple-Cell elements) data file containing the SMC cell array information. "
            "This file (typically 'S6125MCels.dat') contains the basic grid cell definitions "
            "for the SMC grid structure."
        ),
    )
    iside: Optional[SMCFile] = Field(
        default=None,
        description=(
            "ISide data file containing the I-direction face information for the SMC grid. "
            "This file (typically 'S6125ISide.dat') contains the face connections in the I-direction "
            "for the spherical multiple-cell grid."
        ),
    )
    jside: Optional[SMCFile] = Field(
        default=None,
        description=(
            "JSide data file containing the J-direction face information for the SMC grid. "
            "This file (typically 'S6125JSide.dat') contains the face connections in the J-direction "
            "for the spherical multiple-cell grid."
        ),
    )
    subtr: Optional[SMCFile] = Field(
        default=None,
        description=(
            "Subtr (Subtraction) data file containing the obstruction ratio information. "
            "This file (typically 'SMC25Subtr.dat') contains the data for handling "
            "obstructions at cell boundaries or centers in the SMC grid."
        ),
    )
    bundy: Optional[SMCFile] = Field(
        default=None,
        description=(
            "Bundy data file containing the boundary cell list information. "
            "This file (typically 'S6125Bundy.dat') is only needed when NBISMC > 0. "
            "The boundary cell ID numbers should be the sequential numbers in the "
            "cell array (unit 31) of the SMC cell file."
        ),
    )
    mbarc: Optional[SMCFile] = Field(
        default=None,
        description=(
            "MBArc (Multiple-Cell Arctic) data file containing extra cell arrays for Arctic regions. "
            "This file (typically 'S6125MBArc.dat') is used when Arctic part switches are selected "
            "to provide additional grid information for the Arctic region."
        ),
    )
    aisid: Optional[SMCFile] = Field(
        default=None,
        description=(
            "AISid (Arctic I-Side) data file containing extra face arrays for Arctic I-direction. "
            "This file (typically 'S6125AISid.dat') is used when Arctic part switches are selected "
            "to provide additional face information for the Arctic region."
        ),
    )
    ajsid: Optional[SMCFile] = Field(
        default=None,
        description=(
            "AJSid (Arctic J-Side) data file containing extra face arrays for Arctic J-direction. "
            "This file (typically 'S6125AJSid.dat') is used when Arctic part switches are selected "
            "to provide additional face information for the Arctic region."
        ),
    )

    @field_validator(
        "mcel", "iside", "jside", "subtr", "bundy", "mbarc", "aisid", "ajsid"
    )
    @classmethod
    def validate_smc_files(cls, v):
        """Validate SMC file specifications."""
        if v is not None:
            if not isinstance(v, SMCFile):
                raise ValueError(
                    f"SMC file data must be of type SMCFile, got {type(v)}"
                )
        return v
