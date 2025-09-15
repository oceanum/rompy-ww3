"""RUN_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field
from .basemodel import NamelistBaseModel


class Run(NamelistBaseModel):
    """RUN_NML namelist for WW3.
    
    Defines the run parameterization.
    """
    
    fldry: Optional[bool] = Field(
        default=None,
        description="Dry run (I/O only, no calculation)"
    )
    flcx: Optional[bool] = Field(
        default=None,
        description="X-component of propagation"
    )
    flcy: Optional[bool] = Field(
        default=None,
        description="Y-component of propagation"
    )
    flcth: Optional[bool] = Field(
        default=None,
        description="Direction shift"
    )
    flck: Optional[bool] = Field(
        default=None,
        description="Wavenumber shift"
    )
    flsou: Optional[bool] = Field(
        default=None,
        description="Source terms"
    )