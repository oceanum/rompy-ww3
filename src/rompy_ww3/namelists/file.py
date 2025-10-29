"""FILE_NML namelist implementation for WW3 preprocessing."""

from typing import Optional, Union
from pydantic import Field, model_validator
from .basemodel import NamelistBaseModel
from ..core.data import WW3DataBlob, WW3DataGrid
from rompy.logging import get_logger

logger = get_logger()
# Aliases allow for interoperability with WW3DataGrid


class File(NamelistBaseModel):
    """FILE_NML namelist for WW3 preprocessing.

    Defines the content of the input file for ww3_prnc.
    """

    filename: Optional[Union[str, WW3DataBlob, WW3DataGrid]] = Field(
        default=None, description="Input filename for preprocessing"
    )
    longitude: Optional[str] = Field(
        default="longitude", description="Longitude/x dimension name in the input file"
    )
    latitude: Optional[str] = Field(
        default="latitude", description="Latitude/y dimension name in the input file"
    )
    var1: Optional[str] = Field(
        default=None,
        description="Variable name for first component",
        # validation_alias=AliasPath("variables", 0),
    )
    var2: Optional[str] = Field(
        default=None,
        description="Variable name for second component",
        # validation_alias=AliasPath("variables", 1),
    )
    var3: Optional[str] = Field(
        default=None,
        description="Variable name for third component",
        # validation_alias=AliasPath("variables", 2),
    )

    @model_validator(mode="after")
    def set_latlon(self):
        """Ensure latitude and longitude are constent with WW3DataGrid coords"""
        if isinstance(self.filename, WW3DataGrid):
            if self.longitude is None:
                self.longitude = self.filename.coords.x
            if self.latitude is None:
                self.latitude = self.filename.coords.y
        return self

    @model_validator(mode="after")
    def set_vars(self):
        """Ensure variables are constent with WW3DataGrid"""
        if isinstance(self.filename, WW3DataGrid):
            if self.filename.variables:
                if self.var1 or self.var1 or self.var3:
                    logger.warning(
                        "Variables set in WW3DataGrid and File. File takes preference"
                    )
                    self.filename.variables = [
                        getattr(self, var)
                        for var in ["var1", "var2", "var3"]
                        if getattr(self, var)
                    ]
        return self

    def get_namelist_name(self) -> str:
        """Return the specific namelist name for FILE_NML."""
        return "FILE_NML"

    # def render(self, *args, **kwargs) -> str:
    #     """Render the namelist with special handling for VAR arrays."""
    #     lines = []
    #     lines.append(f"&{self.get_namelist_name()}")
    #
    #     # Add standard fields
    #     if self.filename is not None:
    #         lines.append(f"  FILE%FILENAME = '{self.filename}'")
    #     lines.append(f"  FILE%LONGITUDE = '{self.longitude}'")
    #     lines.append(f"  FILE%LATITUDE = '{self.latitude}'")
    #     if self.var1 is not None:
    #         lines.append(f"  FILE%VAR(1) = '{self.var1}'")
    #     if self.var2 is not None:
    #         lines.append(f"  FILE%VAR(2) = '{self.var2}'")
    #     if self.var3 is not None:
    #         lines.append(f"  FILE%VAR(3) = '{self.var3}'")
    #
    #     lines.append("/")
    #     return "\n".join(lines)
