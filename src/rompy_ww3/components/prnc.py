"""Field preprocessor component for WW3 configuration."""

from typing import Optional
from pydantic import Field
from ..namelists.forcing import Forcing
from ..namelists.file import File
from .basemodel import WW3ComponentBaseModel


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
    def run_cmd(self) -> str:
        """Get the default run command for this component"""
        cmd = [
            f"ln -sf {self.file.filename} ww3_prnc.nml \n",
            f"ww3_{self.__class__.__name__.lower()}",
        ]
        return "".join(cmd)
