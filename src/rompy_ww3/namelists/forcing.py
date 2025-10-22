"""FORCING_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field, model_validator
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

    @model_validator(mode="after")
    def validate_only_one_field_true(self):
        """Ensure only one FORCING%FIELD is set to True."""
        field_attributes = [
            self.ice_param1,
            self.ice_param2,
            self.ice_param3,
            self.ice_param4,
            self.ice_param5,
            self.mud_density,
            self.mud_thickness,
            self.mud_viscosity,
            self.water_levels,
            self.currents,
            self.winds,
            self.wind_ast,
            self.atm_momentum,
            self.air_density,
            self.ice_conc,
            self.ice_berg,
            self.data_assim,
        ]
        true_fields = [attr for attr in field_attributes if attr is True]

        if len(true_fields) > 1:
            raise ValueError("Only one FORCING%FIELD can be set to True")

        return self


class ForcingGrid(NamelistBaseModel):
    """FORCING_NML grid parameters for WW3."""

    asis: Optional[bool] = Field(
        default=None, description="Transfer field 'as is' on the model grid"
    )
    latlon: Optional[bool] = Field(
        default=None, description="Define field on regular lat/lon or cartesian grid"
    )

    @model_validator(mode="after")
    def validate_only_one_grid_true(self):
        """Ensure only one FORCING%grid is set to True."""
        grid_attributes = [self.asis, self.latlon]
        true_grids = [attr for attr in grid_attributes if attr is True]

        if len(true_grids) > 1:
            raise ValueError("Only one FORCING%grid can be set to True")

        return self


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

    @model_validator(mode="after")
    def validate_tidal_requirements(self):
        """Ensure tidal is only available on grid%asis with FIELD%level or FIELD%current."""
        if self.tidal is not None:
            # Check if grid.asis is True (if grid is defined)
            if self.grid is not None and self.grid.asis is not True:
                raise ValueError(
                    "Tidal constituents are only available with grid%asis set to True"
                )

            # Check if field.water_levels (level) or field.currents is True (if field is defined)
            if self.field is not None:
                level_or_current_set = (self.field.water_levels is True) or (
                    self.field.currents is True
                )
                if not level_or_current_set:
                    raise ValueError(
                        "Tidal constituents are only available with FIELD%level or FIELD%current"
                    )

            # If field is None, it's an error because we need at least one of level or current
            if self.field is None:
                raise ValueError(
                    "Tidal constituents require field to be defined with level or current"
                )

        return self
