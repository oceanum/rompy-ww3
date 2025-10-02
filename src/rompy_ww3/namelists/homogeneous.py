"""HOMOG_COUNT_NML and HOMOG_INPUT_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field
from .basemodel import NamelistBaseModel


class HomogCount(NamelistBaseModel):
    """HOMOG_COUNT_NML namelist for WW3.

    Defines homogeneous input counts.
    """

    # Single-grid homogeneous input counts
    n_ic1: Optional[int] = Field(
        default=None, description="Number of ice concentration type 1 inputs"
    )
    n_ic2: Optional[int] = Field(
        default=None, description="Number of ice concentration type 2 inputs"
    )
    n_ic3: Optional[int] = Field(
        default=None, description="Number of ice concentration type 3 inputs"
    )
    n_ic4: Optional[int] = Field(
        default=None, description="Number of ice concentration type 4 inputs"
    )
    n_ic5: Optional[int] = Field(
        default=None, description="Number of ice concentration type 5 inputs"
    )
    n_mdn: Optional[int] = Field(
        default=None, description="Number of mud density inputs"
    )
    n_mth: Optional[int] = Field(
        default=None, description="Number of mud thickness inputs"
    )
    n_mvs: Optional[int] = Field(
        default=None, description="Number of mud viscosity inputs"
    )
    n_lev: Optional[int] = Field(
        default=None, description="Number of water level inputs"
    )
    n_cur: Optional[int] = Field(default=None, description="Number of current inputs")
    n_wnd: Optional[int] = Field(default=None, description="Number of wind inputs")
    n_ice: Optional[int] = Field(
        default=None, description="Number of ice concentration inputs"
    )
    n_tau: Optional[int] = Field(
        default=None, description="Number of wind stress inputs"
    )
    n_rho: Optional[int] = Field(
        default=None, description="Number of air density inputs"
    )
    n_mov: Optional[int] = Field(
        default=None, description="Number of moving inputs (multi-grid)"
    )


class HomogInput(NamelistBaseModel):
    """HOMOG_INPUT_NML namelist for WW3.

    Defines homogeneous inputs.
    """

    name: Optional[str] = Field(
        default=None,
        description="Input type name (IC1, IC2, IC3, IC4, IC5, MDN, MTH, MVS, LEV, CUR, WND, ICE, MOV)",
    )
    date: Optional[str] = Field(
        default=None, description="Input date (yyyymmdd hhmmss)"
    )
    value1: Optional[float] = Field(
        default=None, description="First input value (depends on input type)"
    )
    value2: Optional[float] = Field(
        default=None, description="Second input value (depends on input type)"
    )
    value3: Optional[float] = Field(
        default=None, description="Third input value (depends on input type)"
    )
