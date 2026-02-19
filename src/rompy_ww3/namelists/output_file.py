"""FILE_NML namelist implementation for WW3 output configuration."""

from typing import Optional
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel


class File(NamelistBaseModel):
    """FILE_NML namelist for WW3 output configuration (used in ww3_ounf.nml).

    The FILE_NML namelist defines the output file parameters for WAVEWATCH III field output post-processing.
    This namelist controls the naming and format of output files, as well as spatial subsetting options.

    The output files use the specified prefix for naming, and NetCDF format for data storage.
    Spatial subsetting is controlled by index ranges (ix0, ixn, iy0, iyn) to output only portions of the grid.
    """

    # Output file parameters (for postprocessing in ww3_ounf)
    prefix: Optional[str] = Field(
        default="ww3.",
        description=(
            "Prefix for the output file name. This is used to create output file names "
            "for the field data. The actual output files will use this prefix followed by "
            "applicable extensions, timestamps, and numerical identifiers. "
            "Example: 'ww3.' produces files like 'ww3.20100101.nc'"
        ),
    )
    netcdf: Optional[int] = Field(
        default=3,
        description=(
            "NetCDF version to use for output files:\n"
            "  3: NetCDF-3 format (classic)\n"
            "  4: NetCDF-4 format (with HDF5 features)\n"
            "This specifies the version of NetCDF format to use for the output files."
        ),
        ge=3,
        le=4,
    )
    ix0: Optional[int] = Field(
        default=1,
        description=(
            "First X-axis or node index for spatial subsetting. "
            "This defines the starting X-coordinate index for output. "
            "Values of 1 or higher are valid. Default is 1 for the first grid point."
        ),
        ge=1,
    )
    ixn: Optional[int] = Field(
        default=1000000000,
        description=(
            "Last X-axis or node index for spatial subsetting. "
            "This defines the ending X-coordinate index for output. "
            "Should be greater than or equal to IX0. Default is a very large number to include all points."
        ),
        ge=1,
    )
    iy0: Optional[int] = Field(
        default=1,
        description=(
            "First Y-axis index for spatial subsetting. "
            "This defines the starting Y-coordinate index for output. "
            "Values of 1 or higher are valid. Default is 1 for the first grid point."
        ),
        ge=1,
    )
    iyn: Optional[int] = Field(
        default=1000000000,
        description=(
            "Last Y-axis index for spatial subsetting. "
            "This defines the ending Y-coordinate index for output. "
            "Should be greater than or equal to IY0. Default is a very large number to include all points."
        ),
        ge=1,
    )

    def get_namelist_name(self) -> str:
        """Return the specific namelist name for FILE_NML."""
        return "FILE_NML"

    @field_validator("prefix")
    @classmethod
    def validate_prefix(cls, v):
        """Validate prefix is not empty."""
        if v is not None and v.strip() == "":
            raise ValueError("Output file prefix cannot be empty")
        return v

    @field_validator("netcdf")
    @classmethod
    def validate_netcdf_version(cls, v):
        """Validate NetCDF version."""
        if v is not None and v not in [3, 4]:
            raise ValueError(f"NetCDF version must be 3 or 4, got {v}")
        return v

    @field_validator("ixn")
    @classmethod
    def validate_ixn_greater_than_ix0(cls, v, info):
        """Validate IXN is greater than or equal to IX0."""
        if v is not None:
            ix0 = info.data.get("ix0")
            if ix0 is not None and v < ix0:
                raise ValueError(
                    f"IXN ({v}) must be greater than or equal to IX0 ({ix0})"
                )
        return v

    @field_validator("iyn")
    @classmethod
    def validate_iyn_greater_than_iy0(cls, v, info):
        """Validate IYN is greater than or equal to IY0."""
        if v is not None:
            iy0 = info.data.get("iy0")
            if iy0 is not None and v < iy0:
                raise ValueError(
                    f"IYN ({v}) must be greater than or equal to IY0 ({iy0})"
                )
        return v
