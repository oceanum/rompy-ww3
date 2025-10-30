"""FILE_NML namelist implementation for WW3 preprocessing."""

from typing import Optional, Union
from pydantic import Field, model_validator, field_validator
from .basemodel import NamelistBaseModel
from ..core.data import WW3DataBlob, WW3DataGrid
from rompy.logging import get_logger

logger = get_logger()
# Aliases allow for interoperability with WW3DataGrid


class File(NamelistBaseModel):
    """FILE_NML namelist for WW3 preprocessing.

    The FILE_NML namelist defines the content and structure of the input file for WW3 preprocessing (ww3_prnc).
    The input file must respect netCDF format and CF conventions with specific requirements:
    
    Required netCDF structure:
    - Dimensions: time (expected to be called 'time')
    - Dimensions: longitude/latitude (names can be defined in the namelist)
    - Variable: time defined along time dimension with:
      - attribute 'units' in ISO8601 convention
      - attribute 'calendar' set to 'standard' as per CF convention
    - Variable: longitude defined along longitude dimension
    - Variable: latitude defined along latitude dimension
    - Variable: field defined along time,latitude,longitude dimensions
    
    FILE%VAR(I) must be set for each field component where I is 1, 2, or 3 depending on the number of components.
    For example:
    - Single component: FILE%VAR(1) only
    - Two components: FILE%VAR(1), FILE%VAR(2)
    - Three components: FILE%VAR(1), FILE%VAR(2), FILE%VAR(3)
    
    The TIMESHIFT parameter shifts the time value to 'YYYYMMDD HHMMSS' format.
    """

    filename: Optional[Union[str, WW3DataBlob, WW3DataGrid]] = Field(
        default=None,
        description=(
            "Input filename, WW3DataBlob, or WW3DataGrid for preprocessing. "
            "The input file must respect netCDF format and CF conventions. "
            "The file must contain properly formatted time, longitude/latitude, and field variables."
        )
    )
    longitude: Optional[str] = Field(
        default="longitude",
        description=(
            "Longitude/x dimension name in the input file. This specifies the name of the "
            "longitude or x-coordinate variable in the netCDF file. Common names include "
            "'longitude', 'lon', 'x', etc. If WW3DataGrid is used, this will be automatically set."
        )
    )
    latitude: Optional[str] = Field(
        default="latitude",
        description=(
            "Latitude/y dimension name in the input file. This specifies the name of the "
            "latitude or y-coordinate variable in the netCDF file. Common names include "
            "'latitude', 'lat', 'y', etc. If WW3DataGrid is used, this will be automatically set."
        )
    )
    var1: Optional[str] = Field(
        default=None,
        description=(
            "Variable name for the first component of the field. This specifies the name of the "
            "first component variable in the netCDF file. For example, 'U' for the U-component "
            "of wind or current fields. This is required for single, double, or triple component fields."
        )
    )
    var2: Optional[str] = Field(
        default=None,
        description=(
            "Variable name for the second component of the field. This specifies the name of the "
            "second component variable in the netCDF file. For example, 'V' for the V-component "
            "of wind or current fields. This is required for double or triple component fields."
        )
    )
    var3: Optional[str] = Field(
        default=None,
        description=(
            "Variable name for the third component of the field. This specifies the name of the "
            "third component variable in the netCDF file. For example, for air-sea temperature "
            "difference. This is required only for triple component fields."
        )
    )

    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v):
        """Validate filename is not empty if provided."""
        if v is not None:
            if isinstance(v, str) and v.strip() == "":
                raise ValueError("Filename cannot be empty")
        return v

    @field_validator('longitude', 'latitude')
    @classmethod
    def validate_dimension_names(cls, v):
        """Validate dimension names are not empty."""
        if v is not None and v.strip() == "":
            raise ValueError("Dimension names cannot be empty")
        return v

    @field_validator('var1', 'var2', 'var3')
    @classmethod
    def validate_variable_names(cls, v):
        """Validate variable names are not empty."""
        if v is not None and v.strip() == "":
            raise ValueError("Variable names cannot be empty")
        return v

    @model_validator(mode="after")
    def set_latlon(self):
        """Ensure latitude and longitude are consistent with WW3DataGrid coords."""
        if isinstance(self.filename, WW3DataGrid):
            if self.longitude is None:
                self.longitude = self.filename.coords.x
            if self.latitude is None:
                self.latitude = self.filename.coords.y
        return self

    @model_validator(mode="after")
    def set_vars(self):
        """Ensure variables are consistent with WW3DataGrid."""
        if isinstance(self.filename, WW3DataGrid):
            if self.filename.variables:
                if self.var1 or self.var2 or self.var3:  # Fixed typo: was self.var1 or self.var1 or self.var3
                    logger.warning(
                        "Variables set in WW3DataGrid and File. File takes preference"
                    )
                    self.filename.variables = [
                        getattr(self, var)
                        for var in ["var1", "var2", "var3"]
                        if getattr(self, var)
                    ]
        return self

    @model_validator(mode="after")
    def validate_component_consistency(self):
        """Ensure component variable specifications are logically consistent."""
        # For 2-component fields (e.g., currents, winds), both var1 and var2 should be specified
        # For 3-component fields (e.g., winds with air-sea temp diff), all three should be specified
        # For 1-component fields, only var1 should be specified
        
        if self.var1 is not None and self.var2 is None and self.var3 is None:
            # Single component: OK
            pass
        elif self.var1 is not None and self.var2 is not None and self.var3 is None:
            # Two components: OK
            pass
        elif self.var1 is not None and self.var2 is not None and self.var3 is not None:
            # Three components: OK
            pass
        elif self.var1 is None:
            # var1 is None but others may be set - this is an error
            if self.var2 is not None or self.var3 is not None:
                raise ValueError("var1 must be specified if var2 or var3 is specified")
        
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
