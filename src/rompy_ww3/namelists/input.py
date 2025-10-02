"""INPUT_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel


class InputForcing(NamelistBaseModel):
    """Forcing input parameters for WW3."""

    # Forcing flags can be: 'F' (no forcing), 'T' (external file), 'H' (homogeneous), 'C' (coupled)
    water_levels: Optional[str] = Field(
        default=None, description="Water level forcing flag ('F', 'T', 'H', 'C')"
    )
    currents: Optional[str] = Field(
        default=None, description="Current forcing flag ('F', 'T', 'H', 'C')"
    )
    winds: Optional[str] = Field(
        default=None, description="Wind forcing flag ('F', 'T', 'H', 'C')"
    )
    atm_momentum: Optional[str] = Field(
        default=None,
        description="Atmospheric momentum forcing flag ('F', 'T', 'H', 'C')",
    )
    air_density: Optional[str] = Field(
        default=None, description="Air density forcing flag ('F', 'T', 'H', 'C')"
    )
    ice_conc: Optional[str] = Field(
        default=None, description="Ice concentration forcing flag ('F', 'T', 'H', 'C')"
    )
    ice_param1: Optional[str] = Field(
        default=None, description="Ice parameter 1 forcing flag ('F', 'T', 'H', 'C')"
    )
    ice_param2: Optional[str] = Field(
        default=None, description="Ice parameter 2 forcing flag ('F', 'T', 'H', 'C')"
    )
    ice_param3: Optional[str] = Field(
        default=None, description="Ice parameter 3 forcing flag ('F', 'T', 'H', 'C')"
    )
    ice_param4: Optional[str] = Field(
        default=None, description="Ice parameter 4 forcing flag ('F', 'T', 'H', 'C')"
    )
    ice_param5: Optional[str] = Field(
        default=None, description="Ice parameter 5 forcing flag ('F', 'T', 'H', 'C')"
    )
    mud_density: Optional[str] = Field(
        default=None, description="Mud density forcing flag ('F', 'T', 'H', 'C')"
    )
    mud_thickness: Optional[str] = Field(
        default=None, description="Mud thickness forcing flag ('F', 'T', 'H', 'C')"
    )
    mud_viscosity: Optional[str] = Field(
        default=None, description="Mud viscosity forcing flag ('F', 'T', 'H', 'C')"
    )

    @field_validator("*")
    @classmethod
    def validate_forcing_flag(cls, v):
        """Validate that forcing flags are valid."""
        if v is not None and v not in ["F", "T", "H", "C"]:
            raise ValueError("Forcing flag must be 'F', 'T', 'H', or 'C'")
        return v


class InputAssim(NamelistBaseModel):
    """Data assimilation parameters for WW3."""

    mean: Optional[str] = Field(
        default=None, description="Mean wave assimilation flag ('F', 'T')"
    )
    spec1d: Optional[str] = Field(
        default=None, description="1D spectrum assimilation flag ('F', 'T')"
    )
    spec2d: Optional[str] = Field(
        default=None, description="2D spectrum assimilation flag ('F', 'T')"
    )

    @field_validator("*")
    @classmethod
    def validate_assim_flag(cls, v):
        """Validate that assimilation flags are valid."""
        if v is not None and v not in ["F", "T"]:
            raise ValueError("Assimilation flag must be 'F' or 'T'")
        return v


class Input(NamelistBaseModel):
    """INPUT_NML namelist for WW3 (single-grid)."""

    forcing: Optional[InputForcing] = Field(
        default=None, description="Forcing input parameters"
    )
    assim: Optional[InputAssim] = Field(
        default=None, description="Data assimilation parameters"
    )


class InputGrid(NamelistBaseModel):
    """INPUT_GRID_NML namelist for WW3 (multi-grid)."""

    # This represents INPUT(I)%NAME and INPUT(I)%FORCING%...
    # We'll need to handle indexed fields specially
    name: Optional[str] = Field(default=None, description="Name of the input grid")
    forcing: Optional[InputForcing] = Field(
        default=None, description="Forcing input parameters for this grid"
    )
    assim: Optional[InputAssim] = Field(
        default=None, description="Data assimilation parameters for this grid"
    )


class ModelGridForcing(NamelistBaseModel):
    """Forcing configuration for a model grid."""

    water_levels: Optional[str] = Field(
        default=None,
        description="Water level forcing source ('no', 'native', or input grid name)",
    )
    currents: Optional[str] = Field(
        default=None,
        description="Current forcing source ('no', 'native', or input grid name)",
    )
    winds: Optional[str] = Field(
        default=None,
        description="Wind forcing source ('no', 'native', or input grid name)",
    )
    atm_momentum: Optional[str] = Field(
        default=None,
        description="Atmospheric momentum forcing source ('no', 'native', or input grid name)",
    )
    air_density: Optional[str] = Field(
        default=None,
        description="Air density forcing source ('no', 'native', or input grid name)",
    )
    ice_conc: Optional[str] = Field(
        default=None,
        description="Ice concentration forcing source ('no', 'native', or input grid name)",
    )
    ice_param1: Optional[str] = Field(
        default=None,
        description="Ice parameter 1 forcing source ('no', 'native', or input grid name)",
    )
    ice_param2: Optional[str] = Field(
        default=None,
        description="Ice parameter 2 forcing source ('no', 'native', or input grid name)",
    )
    ice_param3: Optional[str] = Field(
        default=None,
        description="Ice parameter 3 forcing source ('no', 'native', or input grid name)",
    )
    ice_param4: Optional[str] = Field(
        default=None,
        description="Ice parameter 4 forcing source ('no', 'native', or input grid name)",
    )
    ice_param5: Optional[str] = Field(
        default=None,
        description="Ice parameter 5 forcing source ('no', 'native', or input grid name)",
    )
    mud_density: Optional[str] = Field(
        default=None,
        description="Mud density forcing source ('no', 'native', or input grid name)",
    )
    mud_thickness: Optional[str] = Field(
        default=None,
        description="Mud thickness forcing source ('no', 'native', or input grid name)",
    )
    mud_viscosity: Optional[str] = Field(
        default=None,
        description="Mud viscosity forcing source ('no', 'native', or input grid name)",
    )


class ModelGridResource(NamelistBaseModel):
    """Resource configuration for a model grid."""

    rank_id: Optional[int] = Field(default=None, description="Rank number of grid")
    group_id: Optional[int] = Field(default=None, description="Group number")
    comm_frac_start: Optional[float] = Field(
        default=None, description="Start fraction of communicator"
    )
    comm_frac_end: Optional[float] = Field(
        default=None, description="End fraction of communicator"
    )
    bound_flag: Optional[bool] = Field(
        default=None, description="Flag identifying dumping of boundary data"
    )


class ModelGrid(NamelistBaseModel):
    """MODEL_GRID_NML namelist for WW3 (multi-grid)."""

    name: Optional[str] = Field(default=None, description="Name of the model grid")
    forcing: Optional[ModelGridForcing] = Field(
        default=None, description="Forcing configuration for this model grid"
    )
    resource: Optional[ModelGridResource] = Field(
        default=None, description="Resource configuration for this model grid"
    )
