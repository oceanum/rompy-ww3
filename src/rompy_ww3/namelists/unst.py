"""UNST_NML namelist implementation for WW3."""

from typing import Optional, Union
from pydantic import Field
from .basemodel import NamelistBaseModel
from ..core.data import WW3DataBlob


class Unst(NamelistBaseModel):
    """UNST_NML namelist for WW3.

    Defines the unstructured grid type.
    """

    sf: Optional[float] = Field(default=1.0, description="Unst scale factor")
    filename: Optional[Union[str, WW3DataBlob]] = Field(
        default="unset", description="Unst filename"
    )
    idf: Optional[int] = Field(default=20, description="Unst file unit number")
    idla: Optional[int] = Field(default=1, description="Unst layout indicator")
    idfm: Optional[int] = Field(default=1, description="Unst format indicator")
    format: Optional[str] = Field(
        default="(....)", description="Unst formatted read format"
    )
    ugobcfile: Optional[str] = Field(
        default="unset", description="Additional boundary list file"
    )
