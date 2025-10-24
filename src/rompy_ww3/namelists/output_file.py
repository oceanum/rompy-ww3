"""FILE_NML namelist implementation for WW3 output configuration."""

from typing import Optional
from pydantic import Field
from .basemodel import NamelistBaseModel


class File(NamelistBaseModel):
    """FILE_NML namelist for WW3 output configuration (used in ww3_ounf.nml).

    Defines the output file parameters for WW3 field output post-processing.
    """

    # Output file parameters (for postprocessing in ww3_ounf)
    prefix: Optional[str] = Field(
        default="ww3.", description="Prefix for output file name"
    )
    netcdf: Optional[int] = Field(default=3, description="NetCDF version [3|4]")
    ix0: Optional[int] = Field(default=1, description="First X-axis or node index")
    ixn: Optional[int] = Field(
        default=1000000000, description="Last X-axis or node index"
    )
    iy0: Optional[int] = Field(default=1, description="First Y-axis index")
    iyn: Optional[int] = Field(default=1000000000, description="Last Y-axis index")

    def get_namelist_name(self) -> str:
        """Return the specific namelist name for FILE_NML."""
        return "FILE_NML"
