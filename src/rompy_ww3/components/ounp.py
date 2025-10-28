"""Point output component for WW3 configuration."""

from typing import Optional
from pydantic import Field
from .basemodel import WW3ComponentBaseModel
from ..namelists.point import Point, PointFile
from ..namelists.spectra import Spectra
from ..namelists.param import Param
from ..namelists.source import Source


class Ounp(WW3ComponentBaseModel):
    """Component for ww3_ounp.nml containing point (NetCDF) output configuration."""

    # POINT_NML - Output fields configuration
    point_nml: Optional[Point] = Field(
        default=None, description="POINT_NML configuration for output fields"
    )

    # FILE_NML - Output file configuration
    file_nml: Optional[PointFile] = Field(
        default=None, description="FILE_NML configuration for output files"
    )

    # SPECTRA_NML - Spectra output configuration (type 1)
    spectra_nml: Optional[Spectra] = Field(
        default=None, description="SPECTRA_NML configuration for spectra output"
    )

    # PARAM_NML - Mean parameter output configuration (type 2)
    param_nml: Optional[Param] = Field(
        default=None, description="PARAM_NML configuration for mean parameter output"
    )

    # SOURCE_NML - Source terms output configuration (type 3)
    source_nml: Optional[Source] = Field(
        default=None, description="SOURCE_NML configuration for source terms output"
    )
