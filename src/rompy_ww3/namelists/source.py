"""SOURCE_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel


class Source(NamelistBaseModel):
    """SOURCE_NML namelist for WW3.

    The SOURCE_NML namelist defines the type 3 (source terms) output configuration for point output in WAVEWATCH III.
    This namelist controls how source term information is output for specific points in the model domain.

    Type 3 output provides detailed information about the various source terms that contribute to
    wave growth and decay, including wind input, nonlinear wave-wave interactions, whitecapping
    dissipation, bottom friction, and ice effects. This output is valuable for process studies
    and understanding model physics.
    """

    output: Optional[int] = Field(
        default=None,
        description=(
            "Output type for source term data:\n"
            "  1: Print plots (human-readable source term plots)\n"
            "  2: Table of 1-D S(f) (frequency-dependent source functions)\n"
            "  3: Table of 1-D inverse time scales (1/T = S/F, frequency-dependent)\n"
            "  4: Transfer file (binary format for model-to-model transfer)\n"
            "This determines the format and content of the source term output."
        ),
        ge=1,
        le=4,
    )
    scale_fac: Optional[int] = Field(
        default=None,
        description=(
            "Scale factor for source term output. This controls scaling of source term values:\n"
            "  -1: Disabled (no scaling applied)\n"
            "  Other values: Scaling factor applied to source terms\n"
            "This is used to adjust units or magnitudes of source term values in output."
        ),
    )
    output_fac: Optional[int] = Field(
        default=None,
        description=(
            "Output factor for normalized source terms:\n"
            "  0: Normalized source terms (energy normalized to 1)\n"
            "  Other values: Non-normalized source terms with specified factor\n"
            "This controls whether source terms are normalized or output with original magnitudes."
        ),
    )
    table_fac: Optional[int] = Field(
        default=None,
        description=(
            "Table factor controlling dimensional/non-dimensional representation:\n"
            "  0: Dimensional source terms\n"
            "  1: Nondimensional in terms of U10 (10m wind speed scaled)\n"
            "  2: Nondimensional in terms of U* (friction velocity scaled)\n"
            "  3-5: Like 0-2 but with frequency normalized with peak frequency (fp)\n"
            "This controls the normalization scheme used for tabular source term output."
        ),
        ge=0,
        le=5,
    )
    spectrum: Optional[bool] = Field(
        default=None,
        description=(
            "Flag to include spectrum in source term output (T) or not (F). "
            "When True, the wave spectrum is included alongside source term data."
        ),
    )
    input: Optional[bool] = Field(
        default=None,
        description=(
            "Flag to include input source term in output (T) or not (F). "
            "When True, wind input source term information is included in the output."
        ),
    )
    interactions: Optional[bool] = Field(
        default=None,
        description=(
            "Flag to include nonlinear interactions in output (T) or not (F). "
            "When True, nonlinear wave-wave interaction source term information is included."
        ),
    )
    dissipation: Optional[bool] = Field(
        default=None,
        description=(
            "Flag to include dissipation source term in output (T) or not (F). "
            "When True, whitecapping and other dissipation source term information is included."
        ),
    )
    bottom: Optional[bool] = Field(
        default=None,
        description=(
            "Flag to include bottom source term in output (T) or not (F). "
            "When True, bottom friction source term information is included in the output."
        ),
    )
    ice: Optional[bool] = Field(
        default=None,
        description=(
            "Flag to include ice source term in output (T) or not (F). "
            "When True, ice-related source term information is included in the output."
        ),
    )
    total: Optional[bool] = Field(
        default=None,
        description=(
            "Flag to include total source term in output (T) or not (F). "
            "When True, the sum of all source terms is included in the output."
        ),
    )

    @field_validator("output")
    @classmethod
    def validate_output_type(cls, v):
        """Validate output type."""
        if v is not None and v not in [1, 2, 3, 4]:
            raise ValueError(f"Output type must be 1, 2, 3, or 4, got {v}")
        return v

    @field_validator("scale_fac")
    @classmethod
    def validate_scale_factor(cls, v):
        """Validate scale factor."""
        if v is not None and v == -1:
            # -1 is valid (disabled)
            pass
        elif v is not None and not isinstance(v, int):
            raise ValueError(f"Scale factor must be an integer, got {type(v)}")
        return v

    @field_validator("output_fac")
    @classmethod
    def validate_output_factor(cls, v):
        """Validate output factor."""
        if v is not None and not isinstance(v, int):
            raise ValueError(f"Output factor must be an integer, got {type(v)}")
        return v

    @field_validator("table_fac")
    @classmethod
    def validate_table_factor(cls, v):
        """Validate table factor."""
        if v is not None and (v < 0 or v > 5):
            raise ValueError(f"Table factor must be 0-5, got {v}")
        return v

    @field_validator(
        "spectrum", "input", "interactions", "dissipation", "bottom", "ice", "total"
    )
    @classmethod
    def validate_boolean_flags(cls, v):
        """Validate boolean flags are actually boolean."""
        if v is not None and not isinstance(v, bool):
            raise ValueError(f"Flag must be boolean (T/F), got {type(v)}")
        return v
