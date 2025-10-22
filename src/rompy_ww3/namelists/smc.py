"""SMC_NML namelist implementation for WW3."""

from typing import Optional, Union
from pydantic import Field
from .basemodel import NamelistBaseModel
from ..core.data import WW3DataBlob


class SMCFile(NamelistBaseModel):
    """File structure for SMC grid data."""

    filename: Optional[Union[str, WW3DataBlob]] = Field(
        default="unset", description="Filename"
    )
    idf: Optional[int] = Field(default=None, description="File unit number")
    idla: Optional[int] = Field(default=1, description="Layout indicator")
    idfm: Optional[int] = Field(default=1, description="Format indicator")
    format: Optional[str] = Field(default="(....)", description="Formatted read format")


class Smc(NamelistBaseModel):
    """SMC_NML namelist for WW3.

    Defines the spherical multiple-cell grid.
    """

    mcel: Optional[SMCFile] = Field(default=None, description="MCels data")
    iside: Optional[SMCFile] = Field(default=None, description="ISide data")
    jside: Optional[SMCFile] = Field(default=None, description="JSide data")
    subtr: Optional[SMCFile] = Field(default=None, description="Subtr data")
    bundy: Optional[SMCFile] = Field(default=None, description="Bundy data")
    mbarc: Optional[SMCFile] = Field(default=None, description="MBArc data")
    aisid: Optional[SMCFile] = Field(default=None, description="AISid data")
    ajsid: Optional[SMCFile] = Field(default=None, description="AJSid data")
