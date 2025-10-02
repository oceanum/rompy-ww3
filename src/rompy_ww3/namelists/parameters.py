"""PARAMS_NML namelist implementation for WW3 model parameters."""

from typing import Optional
from pydantic import Field
from .basemodel import NamelistBaseModel


class ModelParameters(NamelistBaseModel):
    """PARAMS_NML namelist for WW3 model parameters.

    Defines the model parameters from WW3 namelists.nml.
    """

    # Physics parameters
    grav: Optional[float] = Field(
        default=None, description="Acceleration due to gravity (m/s^2)"
    )
    rho: Optional[float] = Field(default=None, description="Density of water (kg/m^3)")
    rhon: Optional[float] = Field(default=None, description="Density of air (kg/m^3)")
    wind_fact: Optional[float] = Field(
        default=None, description="Wind velocity conversion factor"
    )
    wave_fact: Optional[float] = Field(
        default=None, description="Wave height conversion factor"
    )

    # Numerical parameters
    cdhmin: Optional[float] = Field(
        default=None, description="Minimum depth for computation (m)"
    )
    cdhred: Optional[float] = Field(
        default=None, description="Depth reduction for shallow water"
    )
    cdtmin: Optional[float] = Field(default=None, description="Minimum time step (s)")
    theta1: Optional[float] = Field(
        default=None, description="Theta parameter for frequency discretization"
    )
    theta2: Optional[float] = Field(
        default=None, description="Theta parameter for direction discretization"
    )

    # Friction parameters
    fric_type: Optional[str] = Field(
        default=None, description="Type of bottom friction formulation"
    )
    cfbot: Optional[float] = Field(
        default=None, description="Bottom friction coefficient"
    )
    cfshak: Optional[float] = Field(
        default=None, description="Shallow water wave breaking coefficient"
    )

    # Wind input parameters
    wind_type: Optional[str] = Field(
        default=None, description="Type of wind input formulation"
    )
    cdwind: Optional[float] = Field(default=None, description="Wind drag coefficient")
    ust_min: Optional[float] = Field(
        default=None, description="Minimum friction velocity"
    )

    # Whitecapping parameters
    wc_type: Optional[str] = Field(
        default=None, description="Type of whitecapping formulation"
    )
    alpha_bc: Optional[float] = Field(
        default=None, description="Beta parameter for Komen formulation"
    )
    alpha_j: Optional[float] = Field(
        default=None, description="Alpha parameter for Janssen formulation"
    )
    alpha_w: Optional[float] = Field(
        default=None, description="Alpha parameter for Westhuysen formulation"
    )

    # Nonlinear interaction parameters
    nln_type: Optional[str] = Field(
        default=None, description="Type of nonlinear interaction formulation"
    )
    nln_quad: Optional[bool] = Field(
        default=None, description="Flag for quadruplet nonlinear interactions"
    )
    nln_trip: Optional[bool] = Field(
        default=None, description="Flag for triad nonlinear interactions"
    )

    # Propagation parameters
    prop_scheme: Optional[str] = Field(
        default=None, description="Scheme for wave propagation"
    )
    prop_stab: Optional[float] = Field(
        default=None, description="Stability parameter for propagation"
    )

    # Source function parameters
    src_thres: Optional[float] = Field(
        default=None, description="Threshold for source function computation"
    )
    src_min: Optional[float] = Field(
        default=None, description="Minimum value for source function"
    )
