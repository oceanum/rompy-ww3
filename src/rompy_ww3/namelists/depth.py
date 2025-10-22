"""DEPTH_NML namelist implementation for WW3."""

from typing import Optional, Union
from pydantic import Field
from .basemodel import NamelistBaseModel
from ..core.data import WW3DataBlob


class Depth(NamelistBaseModel):
    """DEPTH_NML namelist for WW3.

    Defines the depth to preprocess.
    """

    sf: Optional[float] = Field(
        default=None, description="Scale factor to apply to depth values"
    )
    filename: Optional[Union[str, WW3DataBlob]] = Field(
        default=None, description="Filename containing depth data"
    )
    idf: Optional[int] = Field(default=None, description="File unit number")
    idla: Optional[int] = Field(
        default=None, description="Layout indicator for depth data"
    )
    idfm: Optional[int] = Field(
        default=None, description="Format indicator for depth data"
    )
    format: Optional[str] = Field(
        default=None, description="Formatted read format for depth data"
    )
