"""INPUT_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field, field_validator, model_validator
from .basemodel import NamelistBaseModel
from .validation import validate_forcing_type


class InputForcing(NamelistBaseModel):
    """Forcing input parameters for WW3.

    The INPUT%FORCING namelist defines the forcing fields for the WAVEWATCH III model.
    Each forcing flag can take one of four values:
    - 'F': No forcing (flag default)
    - 'T': External forcing file
    - 'H': Homogeneous forcing input
    - 'C': Coupled forcing field
    """

    # Forcing flags can be: 'F' (no forcing), 'T' (external file), 'H' (homogeneous), 'C' (coupled)
    water_levels: Optional[str] = Field(
        default=None,
        description=(
            "Water level forcing flag. Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field"
        )
    )
    currents: Optional[str] = Field(
        default=None,
        description=(
            "Current forcing flag. Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field"
        )
    )
    winds: Optional[str] = Field(
        default=None,
        description=(
            "Wind forcing flag. Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field"
        )
    )
    atm_momentum: Optional[str] = Field(
        default=None,
        description=(
            "Atmospheric momentum forcing flag. Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field"
        ),
    )
    air_density: Optional[str] = Field(
        default=None,
        description=(
            "Air density forcing flag. Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field"
        )
    )
    ice_conc: Optional[str] = Field(
        default=None,
        description=(
            "Ice concentration forcing flag. Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field"
        )
    )
    ice_param1: Optional[str] = Field(
        default=None,
        description=(
            "Ice parameter 1 forcing flag (typically ice thickness). Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field"
        )
    )
    ice_param2: Optional[str] = Field(
        default=None,
        description=(
            "Ice parameter 2 forcing flag (typically ice viscosity). Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field"
        )
    )
    ice_param3: Optional[str] = Field(
        default=None,
        description=(
            "Ice parameter 3 forcing flag (typically ice density). Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field"
        )
    )
    ice_param4: Optional[str] = Field(
        default=None,
        description=(
            "Ice parameter 4 forcing flag (typically ice modulus). Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field"
        )
    )
    ice_param5: Optional[str] = Field(
        default=None,
        description=(
            "Ice parameter 5 forcing flag (typically ice floe diameter). Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field"
        )
    )
    mud_density: Optional[str] = Field(
        default=None,
        description=(
            "Mud density forcing flag. Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field"
        )
    )
    mud_thickness: Optional[str] = Field(
        default=None,
        description=(
            "Mud thickness forcing flag. Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field"
        )
    )
    mud_viscosity: Optional[str] = Field(
        default=None,
        description=(
            "Mud viscosity forcing flag. Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field"
        )
    )

    @field_validator("*")
    @classmethod
    def validate_forcing_flag(cls, v):
        """Validate that forcing flags are valid WW3 forcing values."""
        if v is not None:
            return validate_forcing_type(v)
        return v

    @model_validator(mode='after')
    def validate_cross_field(self):
        """Perform cross-field validation for forcing parameters."""
        # Validate certain logical consistencies between forcing fields
        # For example, if multiple forcing types are set to 'C' (coupled), 
        # they might need to be consistent with the coupled model configuration
        return self

    def render(self, *args, **kwargs) -> str:
        """Render the namelist with special handling for VAR arrays."""
        lines = []
        lines.append(f"&{self.get_namelist_name()}")

        for field_name, value in self.model_dump().items():
            if value is not None:
                lines.append(f"INPUT%FORCING%{field_name.upper()} = '{value}'")

        lines.append("/")
        return "\n".join(lines)


class InputAssim(NamelistBaseModel):
    """Data assimilation parameters for WW3.

    The INPUT%ASSIM namelist defines data assimilation flags for the WAVEWATCH III model.
    Each assimilation flag can take one of two values:
    - 'F': No assimilation (flag default)
    - 'T': External assimilation file
    """

    mean: Optional[str] = Field(
        default=None,
        description=(
            "Mean wave assimilation flag. Valid values are:\n"
            "  'F': No assimilation (default)\n"
            "  'T': External assimilation file"
        )
    )
    spec1d: Optional[str] = Field(
        default=None,
        description=(
            "1D spectrum assimilation flag. Valid values are:\n"
            "  'F': No assimilation (default)\n"
            "  'T': External assimilation file"
        )
    )
    spec2d: Optional[str] = Field(
        default=None,
        description=(
            "2D spectrum assimilation flag. Valid values are:\n"
            "  'F': No assimilation (default)\n"
            "  'T': External assimilation file"
        )
    )

    @field_validator("*")
    @classmethod
    def validate_assim_flag(cls, v):
        """Validate that assimilation flags are valid WW3 boolean values."""
        if v is not None:
            return validate_forcing_type(v)  # Reuse the forcing validation since assim values are similar: 'F'/'T'
        return v


class Input(NamelistBaseModel):
    """INPUT_NML namelist for WW3 (single-grid).

    The INPUT_NML namelist defines the forcing and data assimilation inputs for 
    single-grid WAVEWATCH III runs. This namelist is read by the ww3_shel program.

    The namelist contains:
    - FORCING: External forcing files for water levels, currents, winds, ice, etc.
    - ASSIM: Data assimilation flags for mean waves, 1D/2D spectra
    """

    forcing: Optional[InputForcing] = Field(
        default=None, description="Forcing input parameters including water levels, currents, winds, ice, etc."
    )
    assim: Optional[InputAssim] = Field(
        default=None, description="Data assimilation parameters for mean waves and 1D/2D spectra"
    )


class InputGrid(NamelistBaseModel):
    """INPUT_GRID_NML namelist for WW3 (multi-grid).

    This represents INPUT(I)%NAME and INPUT(I)%FORCING%... for multi-grid runs.
    We'll need to handle indexed fields specially in multi-grid configurations.
    """

    # This represents INPUT(I)%NAME and INPUT(I)%FORCING%...
    # We'll need to handle indexed fields specially
    name: Optional[str] = Field(
        default=None, 
        description="Name of the input grid, used to reference this input grid in multi-grid runs"
    )
    forcing: Optional[InputForcing] = Field(
        default=None, 
        description="Forcing input parameters for this specific grid in multi-grid runs"
    )
    assim: Optional[InputAssim] = Field(
        default=None, 
        description="Data assimilation parameters for this specific grid in multi-grid runs"
    )


class ModelGridForcing(NamelistBaseModel):
    """Forcing configuration for a model grid in multi-grid runs.

    Each field specifies the source for the forcing, which can be:
    - 'no': No forcing
    - 'native': Use the native grid's forcing
    - Input grid name: Use forcing from a specific input grid
    """

    water_levels: Optional[str] = Field(
        default=None,
        description="Water level forcing source. Can be 'no', 'native', or input grid name.",
    )
    currents: Optional[str] = Field(
        default=None,
        description="Current forcing source. Can be 'no', 'native', or input grid name.",
    )
    winds: Optional[str] = Field(
        default=None,
        description="Wind forcing source. Can be 'no', 'native', or input grid name.",
    )
    atm_momentum: Optional[str] = Field(
        default=None,
        description="Atmospheric momentum forcing source. Can be 'no', 'native', or input grid name.",
    )
    air_density: Optional[str] = Field(
        default=None,
        description="Air density forcing source. Can be 'no', 'native', or input grid name.",
    )
    ice_conc: Optional[str] = Field(
        default=None,
        description="Ice concentration forcing source. Can be 'no', 'native', or input grid name.",
    )
    ice_param1: Optional[str] = Field(
        default=None,
        description="Ice parameter 1 forcing source. Can be 'no', 'native', or input grid name.",
    )
    ice_param2: Optional[str] = Field(
        default=None,
        description="Ice parameter 2 forcing source. Can be 'no', 'native', or input grid name.",
    )
    ice_param3: Optional[str] = Field(
        default=None,
        description="Ice parameter 3 forcing source. Can be 'no', 'native', or input grid name.",
    )
    ice_param4: Optional[str] = Field(
        default=None,
        description="Ice parameter 4 forcing source. Can be 'no', 'native', or input grid name.",
    )
    ice_param5: Optional[str] = Field(
        default=None,
        description="Ice parameter 5 forcing source. Can be 'no', 'native', or input grid name.",
    )
    mud_density: Optional[str] = Field(
        default=None,
        description="Mud density forcing source. Can be 'no', 'native', or input grid name.",
    )
    mud_thickness: Optional[str] = Field(
        default=None,
        description="Mud thickness forcing source. Can be 'no', 'native', or input grid name.",
    )
    mud_viscosity: Optional[str] = Field(
        default=None,
        description="Mud viscosity forcing source. Can be 'no', 'native', or input grid name.",
    )


class ModelGridResource(NamelistBaseModel):
    """Resource configuration for a model grid in multi-grid runs."""

    rank_id: Optional[int] = Field(
        default=None, 
        description="Rank number of the grid in the MPI process configuration",
        ge=0
    )
    group_id: Optional[int] = Field(
        default=None, 
        description="Group number for this grid",
        ge=0
    )
    comm_frac_start: Optional[float] = Field(
        default=None, 
        description="Start fraction of communicator allocation (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    comm_frac_end: Optional[float] = Field(
        default=None, 
        description="End fraction of communicator allocation (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    bound_flag: Optional[bool] = Field(
        default=None, 
        description="Flag identifying dumping of boundary data for this grid"
    )


class ModelGrid(NamelistBaseModel):
    """MODEL_GRID_NML namelist for WW3 (multi-grid).

    Defines the configuration for a single model grid in multi-grid runs.
    Each grid has its own forcing configuration and resource allocation.
    """

    name: Optional[str] = Field(
        default=None, 
        description="Name of the model grid, used to identify this grid in multi-grid runs"
    )
    forcing: Optional[ModelGridForcing] = Field(
        default=None, 
        description="Forcing configuration for this model grid in multi-grid runs"
    )
    resource: Optional[ModelGridResource] = Field(
        default=None, 
        description="Resource configuration (MPI ranks, communicator allocation) for this model grid"
    )
