"""MASK_NML namelist implementation for WW3."""

from typing import Optional, Union
from pydantic import Field
from .basemodel import NamelistBaseModel
from ..core.data import WW3DataBlob


class Mask(NamelistBaseModel):
    """MASK_NML namelist for WW3.

    Defines the point status map.
    """

    filename: Optional[Union[str, WW3DataBlob]] = Field(
        default=None, description="Filename containing mask data"
    )
    idf: Optional[int] = Field(default=None, description="File unit number")
    idla: Optional[int] = Field(
        default=None, description="Layout indicator for mask data"
    )
    idfm: Optional[int] = Field(
        default=None, description="Format indicator for mask data"
    )
    format: Optional[str] = Field(
        default=None, description="Formatted read format for mask data"
    )
