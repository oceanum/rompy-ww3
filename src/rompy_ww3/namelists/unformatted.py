"""OUNF_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel


class UnformattedOutput(NamelistBaseModel):
    """OUNF_NML namelist for WW3.

    Defines unformatted output parameters for WW3.
    """

    # Output fields configuration
    field_list: Optional[str] = Field(
        default=None,
        description="List of fields to output in unformatted format (space-separated)",
    )

    # Time configuration
    start: Optional[str] = Field(
        default=None, description="Unformatted output start time (yyyymmdd hhmmss)"
    )
    stride: Optional[int] = Field(
        default=None, description="Unformatted output time stride (seconds)"
    )
    stop: Optional[str] = Field(
        default=None, description="Unformatted output stop time (yyyymmdd hhmmss)"
    )

    # File configuration
    file_format: Optional[str] = Field(
        default=None, description="File format for unformatted output ('bin', 'nc')"
    )
    single_file: Optional[bool] = Field(
        default=None, description="Flag to output all variables to single file (T/F)"
    )

    # Spatial subset
    x_first: Optional[int] = Field(
        default=None, description="First X index for spatial subset"
    )
    x_last: Optional[int] = Field(
        default=None, description="Last X index for spatial subset"
    )
    y_first: Optional[int] = Field(
        default=None, description="First Y index for spatial subset"
    )
    y_last: Optional[int] = Field(
        default=None, description="Last Y index for spatial subset"
    )

    @field_validator("stride", mode="before")
    @classmethod
    def parse_stride(cls, v):
        """Parse string inputs to integers (backward-compatible)."""
        if v is None:
            return v
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError as e:
                raise ValueError(
                    f"Invalid integer format for 'stride': {v}. Error: {e}"
                )
        if isinstance(v, int):
            return v
        return v
