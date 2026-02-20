"""INPUT_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field, field_validator, model_validator
from .basemodel import NamelistBaseModel
from .enums import FORCING, parse_enum


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
    water_levels: Optional[FORCING] = Field(
        default=None,
        description=(
            "Water level forcing flag. Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field\n"
            "Accepts Enum members, canonical values (exact/case-insensitive), or enum names."
        ),
    )
    currents: Optional[FORCING] = Field(
        default=None,
        description=(
            "Current forcing flag. Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field\n"
            "Accepts Enum members, canonical values (exact/case-insensitive), or enum names."
        ),
    )
    winds: Optional[FORCING] = Field(
        default=None,
        description=(
            "Wind forcing flag. Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field\n"
            "Accepts Enum members, canonical values (exact/case-insensitive), or enum names."
        ),
    )
    atm_momentum: Optional[FORCING] = Field(
        default=None,
        description=(
            "Atmospheric momentum forcing flag. Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field\n"
            "Accepts Enum members, canonical values (exact/case-insensitive), or enum names."
        ),
    )
    air_density: Optional[FORCING] = Field(
        default=None,
        description=(
            "Air density forcing flag. Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field\n"
            "Accepts Enum members, canonical values (exact/case-insensitive), or enum names."
        ),
    )
    ice_conc: Optional[FORCING] = Field(
        default=None,
        description=(
            "Ice concentration forcing flag. Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field\n"
            "Accepts Enum members, canonical values (exact/case-insensitive), or enum names."
        ),
    )
    ice_param1: Optional[FORCING] = Field(
        default=None,
        description=(
            "Ice parameter 1 forcing flag (typically ice thickness). Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field\n"
            "Accepts Enum members, canonical values (exact/case-insensitive), or enum names."
        ),
    )
    ice_param2: Optional[FORCING] = Field(
        default=None,
        description=(
            "Ice parameter 2 forcing flag (typically ice viscosity). Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field\n"
            "Accepts Enum members, canonical values (exact/case-insensitive), or enum names."
        ),
    )
    ice_param3: Optional[FORCING] = Field(
        default=None,
        description=(
            "Ice parameter 3 forcing flag (typically ice density). Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field\n"
            "Accepts Enum members, canonical values (exact/case-insensitive), or enum names."
        ),
    )
    ice_param4: Optional[FORCING] = Field(
        default=None,
        description=(
            "Ice parameter 4 forcing flag (typically ice modulus). Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field\n"
            "Accepts Enum members, canonical values (exact/case-insensitive), or enum names."
        ),
    )
    ice_param5: Optional[FORCING] = Field(
        default=None,
        description=(
            "Ice parameter 5 forcing flag (typically ice floe diameter). Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field\n"
            "Accepts Enum members, canonical values (exact/case-insensitive), or enum names."
        ),
    )
    mud_density: Optional[FORCING] = Field(
        default=None,
        description=(
            "Mud density forcing flag. Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field\n"
            "Accepts Enum members, canonical values (exact/case-insensitive), or enum names."
        ),
    )
    mud_thickness: Optional[FORCING] = Field(
        default=None,
        description=(
            "Mud thickness forcing flag. Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field\n"
            "Accepts Enum members, canonical values (exact/case-insensitive), or enum names."
        ),
    )
    mud_viscosity: Optional[FORCING] = Field(
        default=None,
        description=(
            "Mud viscosity forcing flag. Valid values are:\n"
            "  'F': No forcing (default)\n"
            "  'T': External forcing file\n"
            "  'H': Homogeneous forcing input\n"
            "  'C': Coupled forcing field\n"
            "Accepts Enum members, canonical values (exact/case-insensitive), or enum names."
        ),
    )

    @field_validator("*", mode="before")
    @classmethod
    def validate_forcing_flag(cls, v):
        """Validate that forcing flags are valid WW3 forcing values using parse_enum."""
        if v is not None:
            return parse_enum(FORCING, v)
        return v

    @model_validator(mode="after")
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
        ),
    )
    spec1d: Optional[str] = Field(
        default=None,
        description=(
            "1D spectrum assimilation flag. Valid values are:\n"
            "  'F': No assimilation (default)\n"
            "  'T': External assimilation file"
        ),
    )
    spec2d: Optional[str] = Field(
        default=None,
        description=(
            "2D spectrum assimilation flag. Valid values are:\n"
            "  'F': No assimilation (default)\n"
            "  'T': External assimilation file"
        ),
    )

    @field_validator("*", mode="before")
    @classmethod
    def validate_assim_flag(cls, v):
        """Validate that assimilation flags are valid WW3 forcing values using parse_enum."""
        if v is not None:
            return parse_enum(FORCING, v)
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
        default=None,
        description="Forcing input parameters including water levels, currents, winds, ice, etc.",
    )
    assim: Optional[InputAssim] = Field(
        default=None,
        description="Data assimilation parameters for mean waves and 1D/2D spectra",
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
        description="Name of the input grid, used to reference this input grid in multi-grid runs",
    )
    forcing: Optional[InputForcing] = Field(
        default=None,
        description="Forcing input parameters for this specific grid in multi-grid runs",
    )
    assim: Optional[InputAssim] = Field(
        default=None,
        description="Data assimilation parameters for this specific grid in multi-grid runs",
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
        ge=0,
    )
    group_id: Optional[int] = Field(
        default=None, description="Group number for this grid", ge=0
    )
    comm_frac_start: Optional[float] = Field(
        default=None,
        description="Start fraction of communicator allocation (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    comm_frac_end: Optional[float] = Field(
        default=None,
        description="End fraction of communicator allocation (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    bound_flag: Optional[bool] = Field(
        default=None,
        description="Flag identifying dumping of boundary data for this grid",
    )

    def render(self, *args, **kwargs) -> str:
        """Render as single-line RESOURCE for WW3 v6.07.1."""
        values = []
        if self.rank_id is not None:
            values.append(str(self.rank_id))
        if self.group_id is not None:
            values.append(str(self.group_id))
        if self.comm_frac_start is not None:
            values.append(f"{self.comm_frac_start:.2f}")
        if self.comm_frac_end is not None:
            values.append(f"{self.comm_frac_end:.2f}")
        if self.bound_flag is not None:
            values.append("T" if self.bound_flag else "F")

        if values:
            return f"RESOURCE = {' '.join(values)}"
        return ""


class ModelGrid(NamelistBaseModel):
    """MODEL_GRID_NML namelist for WW3 (multi-grid).

    Defines the configuration for a single model grid in multi-grid runs.
    Each grid has its own forcing configuration and resource allocation.
    """

    name: Optional[str] = Field(
        default=None,
        description="Name of the model grid, used to identify this grid in multi-grid runs",
    )
    forcing: Optional[ModelGridForcing] = Field(
        default=None,
        description="Forcing configuration for this model grid in multi-grid runs",
    )
    # Backward compatibility: support old nested resource object
    resource: Optional[ModelGridResource] = Field(
        default=None,
        description="Resource configuration (legacy - use flattened fields instead)",
    )
    # Resource fields flattened for v6.07.1 compatibility
    # v6.07.1 expects: MODEL(I)%RESOURCE = rank_id group_id comm_frac_start comm_frac_end bound_flag
    resource_rank_id: Optional[int] = Field(
        default=None,
        description="Rank number of the grid in the MPI process configuration",
        ge=0,
    )
    resource_group_id: Optional[int] = Field(
        default=None,
        description="Group number for this grid",
        ge=0,
    )
    resource_comm_frac_start: Optional[float] = Field(
        default=None,
        description="Start fraction of communicator allocation (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    resource_comm_frac_end: Optional[float] = Field(
        default=None,
        description="End fraction of communicator allocation (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    resource_bound_flag: Optional[bool] = Field(
        default=None,
        description="Flag identifying dumping of boundary data for this grid",
    )

    @model_validator(mode="before")
    @classmethod
    def convert_resource(cls, values):
        """Convert legacy nested resource to flattened fields."""
        if isinstance(values, dict):
            resource = values.get("resource")
            if resource is not None:
                # Handle both ModelGridResource objects and plain dicts
                if hasattr(resource, "model_dump"):
                    resource_data = resource.model_dump()
                else:
                    resource_data = resource
                if (
                    "resource_rank_id" not in values
                    or values["resource_rank_id"] is None
                ):
                    values["resource_rank_id"] = resource_data.get("rank_id")
                if (
                    "resource_group_id" not in values
                    or values["resource_group_id"] is None
                ):
                    values["resource_group_id"] = resource_data.get("group_id")
                if (
                    "resource_comm_frac_start" not in values
                    or values["resource_comm_frac_start"] is None
                ):
                    values["resource_comm_frac_start"] = resource_data.get(
                        "comm_frac_start"
                    )
                if (
                    "resource_comm_frac_end" not in values
                    or values["resource_comm_frac_end"] is None
                ):
                    values["resource_comm_frac_end"] = resource_data.get(
                        "comm_frac_end"
                    )
                if (
                    "resource_bound_flag" not in values
                    or values["resource_bound_flag"] is None
                ):
                    values["resource_bound_flag"] = resource_data.get("bound_flag")
        return values

    def render(self, *args, **kwargs) -> str:
        """Render ModelGrid with RESOURCE as single line for v6.07.1."""
        lines = []
        lines.append("&MODEL_GRID_NML")

        if self.name is not None:
            lines.append(f"  MODEL_GRID%NAME = '{self.name}'")

        if self.forcing is not None:
            forcing_rendered = self.forcing.render()
            for line in forcing_rendered.split("\n"):
                if (
                    line.strip()
                    and not line.strip().startswith("&")
                    and line.strip() != "/"
                ):
                    lines.append(
                        line.replace("MODEL_GRID_FORCING%", "MODEL_GRID%FORCING%")
                    )

        if any(
            [
                self.resource_rank_id is not None,
                self.resource_group_id is not None,
                self.resource_comm_frac_start is not None,
                self.resource_comm_frac_end is not None,
                self.resource_bound_flag is not None,
            ]
        ):
            values = []
            if self.resource_rank_id is not None:
                values.append(str(self.resource_rank_id))
            if self.resource_group_id is not None:
                values.append(str(self.resource_group_id))
            if self.resource_comm_frac_start is not None:
                values.append(f"{self.resource_comm_frac_start:.2f}")
            if self.resource_comm_frac_end is not None:
                values.append(f"{self.resource_comm_frac_end:.2f}")
            if self.resource_bound_flag is not None:
                values.append("T" if self.resource_bound_flag else "F")
            lines.append(f"  MODEL_GRID%RESOURCE = {' '.join(values)}")

        lines.append("/")
        return "\n".join(lines)
