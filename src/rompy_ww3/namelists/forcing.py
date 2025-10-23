"""FORCING_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field, model_validator
from .basemodel import NamelistBaseModel


class ForcingField(NamelistBaseModel):
    """FORCING_NML field parameters for WW3.

    This class supports two ways of initialization:
    1. Boolean-based: Set one of the boolean fields to True (e.g., winds=True)
    2. String-based: Set the variable field to the desired WW3 variable name (e.g., variable="WINDS")
    """

    # String field to allow initialization with a specific variable
    variable: Optional[str] = Field(
        default=None,
        description="WW3 variable name to set as active. When provided, the corresponding boolean field will be set to True. This field is excluded from rendering output.",
        exclude=True,  # Exclude this from serialization/rendering
        choices=[
            "ICE_THICKNESS",
            "ICE_VISCOSITY",
            "ICE_DENSITY",
            "ICE_MODULUS",
            "ICE_FLOE_DIAMETER",
            "MUD_DENSITY",
            "MUD_THICKNESS",
            "MUD_VISCOSITY",
            "WATER_LEVELS",
            "CURRENTS",
            "WINDS",
            "WIND_AIR_SEA_TEMP_DIFF",
            "ATMOSPHERIC_MOMENTUM",
            "AIR_DENSITY",
            "ICE_CONCENTRATION",
            "ICEBERGS_SEA_ICE_CONC",
            "DATA_ASSIMILATION",
        ],
    )

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

    @model_validator(mode="before")
    @classmethod
    def set_boolean_field_from_variable(cls, values):
        """Set appropriate boolean field based on the variable string."""
        if isinstance(values, dict):
            variable = values.get("variable")
            if variable is not None:
                # Map the variable string to the corresponding field name (case-insensitive)
                var_to_field_map = {
                    # Full names
                    "ICE_THICKNESS": "ice_param1",
                    "ICE_VISCOSITY": "ice_param2",
                    "ICE_DENSITY": "ice_param3",
                    "ICE_MODULUS": "ice_param4",
                    "ICE_FLOE_DIAMETER": "ice_param5",
                    "MUD_DENSITY": "mud_density",
                    "MUD_THICKNESS": "mud_thickness",
                    "MUD_VISCOSITY": "mud_viscosity",
                    "WATER_LEVELS": "water_levels",
                    "CURRENTS": "currents",
                    "WINDS": "winds",
                    "WIND_AIR_SEA_TEMP_DIFF": "wind_ast",
                    "ATMOSPHERIC_MOMENTUM": "atm_momentum",
                    "AIR_DENSITY": "air_density",
                    "ICE_CONCENTRATION": "ice_conc",
                    "ICEBERGS_SEA_ICE_CONC": "ice_berg",
                    "DATA_ASSIMILATION": "data_assim",
                }

                # Add alternative forms to the mapping (like WIND, wind, etc.)
                var_to_field_map.update(
                    {
                        # Alternative forms for winds
                        "WIND": "winds",
                        "wind": "winds",
                        # Alternative forms for currents
                        "current": "currents",
                        "CURRENT": "currents",
                        # Alternative forms for water_levels
                        "water_level": "water_levels",
                        "WATER_LEVEL": "water_levels",
                        "level": "water_levels",
                        "LEVEL": "water_levels",
                        # Additional alternative forms for other fields as needed...
                    }
                )

                # Convert to uppercase to handle case-insensitive matching
                variable_upper = variable.upper()

                # Check if the uppercase version matches any of the original keys
                if variable_upper in var_to_field_map:
                    field_name = var_to_field_map[variable_upper]
                    # Set the specified field to True and others that aren't already set to False
                    for field_key in var_to_field_map.values():
                        if field_key not in values or values[field_key] is None:
                            values[field_key] = field_key == field_name
                elif (
                    variable in var_to_field_map
                ):  # Check the original case for alternative forms
                    field_name = var_to_field_map[variable]
                    # Set the specified field to True and others that aren't already set to False
                    for field_key in var_to_field_map.values():
                        if field_key not in values or values[field_key] is None:
                            values[field_key] = field_key == field_name
                else:
                    # If the variable is not found in the mapping, raise an error
                    valid_vars = list(var_to_field_map.keys())
                    raise ValueError(
                        f"Invalid variable: {variable}. Valid options are: {valid_vars}"
                    )

        return values

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

    @property
    def ww3_var_name(self) -> Optional[str]:
        """Get the WW3 variable name corresponding to the field set to True."""
        # If variable was explicitly set, return it
        if self.variable is not None:
            return self.variable

        field_to_var_map = {
            "ice_param1": "ICE_THICKNESS",
            "ice_param2": "ICE_VISCOSITY",
            "ice_param3": "ICE_DENSITY",
            "ice_param4": "ICE_MODULUS",
            "ice_param5": "ICE_FLOE_DIAMETER",
            "mud_density": "MUD_DENSITY",
            "mud_thickness": "MUD_THICKNESS",
            "mud_viscosity": "MUD_VISCOSITY",
            "water_levels": "WATER_LEVELS",
            "currents": "CURRENTS",
            "winds": "WINDS",
            "wind_ast": "WIND_AIR_SEA_TEMP_DIFF",
            "atm_momentum": "ATMOSPHERIC_MOMENTUM",
            "air_density": "AIR_DENSITY",
            "ice_conc": "ICE_CONCENTRATION",
            "ice_berg": "ICEBERGS_SEA_ICE_CONC",
            "data_assim": "DATA_ASSIMILATION",
        }

        for field_name, var_name in field_to_var_map.items():
            if getattr(self, field_name) is True:
                return var_name

        return None


class ForcingGrid(NamelistBaseModel):
    """FORCING_NML grid parameters for WW3.

    This class supports two ways of initialization:
    1. Boolean-based: Set one of the boolean fields to True (e.g., asis=True)
    2. String-based: Set the grid_type field to the desired grid type (e.g., grid_type="asis")
    """

    # String field to allow initialization with a specific grid type
    grid_type: Optional[str] = Field(
        default=None,
        description="Grid type to set as active. When provided, the corresponding boolean field will be set to True. This field is excluded from rendering output.",
        exclude=True,  # Exclude this from serialization/rendering
    )

    asis: Optional[bool] = Field(
        default=None, description="Transfer field 'as is' on the model grid"
    )
    latlon: Optional[bool] = Field(
        default=True, description="Define field on regular lat/lon or cartesian grid"
    )

    @model_validator(mode="before")
    @classmethod
    def set_boolean_field_from_grid_type(cls, values):
        """Set appropriate boolean field based on the grid_type string."""
        if isinstance(values, dict):
            grid_type = values.get("grid_type")
            if grid_type is not None:
                # Convert to lowercase for case-insensitive matching
                grid_type_lower = grid_type.lower()

                if grid_type_lower == "asis":
                    # Set asis to True and latlon to False (if not already set)
                    if "asis" not in values or values["asis"] is None:
                        values["asis"] = True
                    if "latlon" not in values or values["latlon"] is None:
                        values["latlon"] = False
                elif grid_type_lower == "latlon":
                    # Set latlon to True and asis to False (if not already set)
                    if "latlon" not in values or values["latlon"] is None:
                        values["latlon"] = True
                    if "asis" not in values or values["asis"] is None:
                        values["asis"] = False
                else:
                    # If the grid_type is not valid, raise an error
                    raise ValueError(
                        f"Invalid grid_type: {grid_type}. Valid options are: asis, latlon"
                    )

        return values

    @model_validator(mode="after")
    def validate_only_one_grid_true(self):
        """Ensure only one FORCING%grid is set to True."""
        grid_attributes = [self.asis, self.latlon]
        true_grids = [attr for attr in grid_attributes if attr is True]

        if len(true_grids) > 1:
            raise ValueError("Only one FORCING%grid can be set to True")

        return self

    @property
    def active_grid_type(self) -> Optional[str]:
        """Get the active grid type."""
        if self.asis is True:
            return "asis"
        elif self.latlon is True:
            return "latlon"
        return None


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

    @property
    def ww3_var_name(self) -> Optional[str]:
        """Get the WW3 variable name from the FORCING%FIELD."""
        if self.field is not None:
            return self.field.ww3_var_name
        return None
