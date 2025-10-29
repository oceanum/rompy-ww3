"""Field preprocessor component for WW3 configuration."""

from typing import Optional
from pydantic import Field, model_validator
from ..namelists.forcing import Forcing
from ..namelists.file import File
from .basemodel import WW3ComponentBaseModel
from ..core.data import WW3DataBlob, WW3DataGrid


class Prnc(WW3ComponentBaseModel):
    """Component for ww3_prnc.nml containing field preprocessing configuration."""

    forcing: Optional[Forcing] = None
    file: Optional[File] = Field(
        default=None, description="FILE_NML configuration for input file preprocessing"
    )

    @property
    def nml_filename(self) -> str:
        """Get the default filename for this component"""
        return f"ww3_prnc.{self.forcing.ww3_var_name}"

    @property
    def prepend_cmd(self) -> str:
        return f"ln -sf {self.nml_filename} ww3_prnc.nml"

    @model_validator(mode="after")
    def set_datasource_id(self):
        """Ensure id are constent with WW3DataGrid"""
        if isinstance(self.file.filename, (WW3DataBlob, WW3DataGrid)):
            self.file.filename.id = self.forcing.ww3_var_name.lower()
        return self
