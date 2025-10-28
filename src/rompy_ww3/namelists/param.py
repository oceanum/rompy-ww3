"""PARAM_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field
from .basemodel import NamelistBaseModel


class Param(NamelistBaseModel):
    """PARAM_NML namelist for WW3.

    Defines type 2 (mean parameter) output configuration for point output.
    """

    output: Optional[int] = Field(
        default=None,
        description=(
            "Output type: "
            "1=Forcing parameters, "
            "2=Mean wave parameters, "
            "3=Nondimensional pars. (U*), "
            "4=Nondimensional pars. (U10), "
            "5=Validation table, "
            "6=WMO standard output"
        ),
    )
