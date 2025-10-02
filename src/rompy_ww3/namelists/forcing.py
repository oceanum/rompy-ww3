"""FORCING_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field
from .basemodel import NamelistBaseModel


class ForcingField(NamelistBaseModel):
    """FORCING_NML field parameters for WW3."""

    ice_param1: Optional[bool] = Field(
        default=None, description="Ice thickness (1-component)"
    )
    ice_param2: Optional[bool] = Field(
        default=None, description="Ice viscosity (1-component)"
    )
    ice_param3: Optional[bool] = Field(
        default=None, description="Ice density (1-component)"
    )
    ice_param4: Optional[bool] = Field(
        default=None, description="Ice modulus (1-component)"
    )
    ice_param5: Optional[bool] = Field(
        default=None, description="Ice floe mean diameter (1-component)"
    )
    mud_density: Optional[bool] = Field(
        default=None, description="Mud density (1-component)"
    )
    mud_thickness: Optional[bool] = Field(
        default=None, description="Mud thickness (1-component)"
    )
    mud_viscosity: Optional[bool] = Field(
        default=None, description="Mud viscosity (1-component)"
    )
    water_levels: Optional[bool] = Field(
        default=None, description="Level (1-component)"
    )
    currents: Optional[bool] = Field(default=None, description="Current (2-components)")
    winds: Optional[bool] = Field(default=None, description="Wind (2-components)")
    wind_ast: Optional[bool] = Field(
        default=None, description="Wind and air-sea temp. dif. (3-components)"
    )
    atm_momentum: Optional[bool] = Field(
        default=None, description="Atmospheric momentum (2-components)"
    )
    air_density: Optional[bool] = Field(
        default=None, description="Air density (1-component)"
    )
    ice_conc: Optional[bool] = Field(
        default=None, description="Ice concentration (1-component)"
    )
    ice_berg: Optional[bool] = Field(
        default=None, description="Icebergs and sea ice concentration (2-components)"
    )
    data_assim: Optional[bool] = Field(
        default=None, description="Data for assimilation (1-component)"
    )


class ForcingGrid(NamelistBaseModel):
    """FORCING_NML grid parameters for WW3."""

    asis: Optional[bool] = Field(
        default=None, description="Transfer field 'as is' on the model grid"
    )
    latlon: Optional[bool] = Field(
        default=None, description="Define field on regular lat/lon or cartesian grid"
    )


class Forcing(NamelistBaseModel):
    """FORCING_NML namelist for WW3.

    Defines the forcing fields to preprocess.
    """

    timestart: Optional[str] = Field(
        default=None, description="Start date for the forcing field (yyyymmdd hhmmss)"
    )
    timestop: Optional[str] = Field(
        default=None, description="Stop date for the forcing field (yyyymmdd hhmmss)"
    )
    field: Optional[ForcingField] = Field(
        default=None, description="Forcing field parameters"
    )
    grid: Optional[ForcingGrid] = Field(
        default=None, description="Forcing grid parameters"
    )
    tidal: Optional[str] = Field(
        default=None, description="Tidal constituents [FAST | VFAST | 'M2 S2 N2']"
    )
