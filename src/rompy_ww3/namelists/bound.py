"""BOUND_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field
from .basemodel import NamelistBaseModel
from ..core.data import WW3DataBlob, WW3Boundary
from typing import Union


class Bound(NamelistBaseModel):
    """BOUND_NML namelist for WW3.

    Defines the input boundaries to preprocess.
    """

    mode: Optional[str] = Field(default=None, description="Mode: 'WRITE' or 'READ'")
    interp: Optional[int] = Field(
        default=2, description="Interpolation method: 1 (nearest), 2 (linear)"
    )
    verbose: Optional[int] = Field(default=1, description="Verbosity level: 0, 1, or 2")
    file: Optional[Union[str, WW3DataBlob, WW3Boundary]] = Field(
        default=None, description="Input spec.nc listing file"
    )
