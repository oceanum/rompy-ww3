"""Field preprocessor component for WW3 configuration."""

from typing import Optional
from pydantic import Field
from ..namelists.forcing import Forcing
from ..namelists.file import File
from .basemodel import WW3ComponentBaseModel


class FieldPreprocessorComponent(WW3ComponentBaseModel):
    """Component for ww3_prnc.nml containing field preprocessing configuration."""

    forcing: Optional[Forcing] = None
    file: Optional[File] = Field(
        default=None, description="FILE_NML configuration for input file preprocessing"
    )
