"""Point output component for WW3 configuration."""

from typing import Optional
from pydantic import Field as PydanticField
from .basemodel import WW3ComponentBaseModel
from ..namelists.point import Point, PointFile
from ..namelists.spectra import Spectra
from ..namelists.param import Param
from ..namelists.source import Source


class Ounp(WW3ComponentBaseModel):
    """Component for ww3_ounp.nml containing point (NetCDF) output configuration.

    The Ounp component represents the point output configuration for WW3.
    It contains the POINT_NML, FILE_NML, SPECTRA_NML, PARAM_NML, and SOURCE_NML 
    namelist objects needed for configuring the WW3 point output program (ww3_ounp.nml).
    
    This component manages:
    - POINT_NML: Point output fields configuration
    - FILE_NML: Point output file configuration
    - SPECTRA_NML: Spectra output configuration (type 1)
    - PARAM_NML: Mean parameter output configuration (type 2)
    - SOURCE_NML: Source terms output configuration (type 3)
    
    The Ounp component is used for point output runs and provides a clean interface
    for configuring all aspects of the WW3 point output program.
    
    Key Features:
    - **Point Output**: Configuration for point output generation at specific locations
    - **Multiple Output Types**: Support for spectra (type 1), mean parameters (type 2), and source terms (type 3)
    - **Flexible Timing**: Control over point output timing (start, stride, stop)
    - **Location Specification**: Definition of point locations for output
    - **File Management**: Point output file naming and organization
    
    Usage Examples:
        ```python
        from rompy_ww3.components import Ounp
        from rompy_ww3.namelists import Point, PointFile, Spectra, Param, Source
        
        # Create a point output configuration
        ounp = Ounp(
            point_nml=Point(
                timestart="20230101 000000",
                timestride="3600",
                timecount="100",
                list="all"
            ),
            file_nml=PointFile(
                prefix="ww3_points.",
                netcdf=4
            ),
            spectra_nml=Spectra(
                output=1,
                scale_fac=1,
                output_fac=0
            )
        )
        
        # Render the namelist content
        content = ounp.render()
        
        # Write to a file
        ounp.write_nml("./namelists")
        ```
    """

    # POINT_NML - Output fields configuration
    point_nml: Optional[Point] = PydanticField(
        default=None, 
        description=(
            "POINT_NML configuration for output fields. "
            "Defines point output parameters including timing (start, stride, count), "
            "point lists, and format for point output generation in WW3."
        )
    )

    # FILE_NML - Output file configuration
    file_nml: Optional[PointFile] = PydanticField(
        default=None, 
        description=(
            "FILE_NML configuration for output files. "
            "Defines point output file parameters including naming prefix, NetCDF version, "
            "and format for point output files in WW3."
        )
    )

    # SPECTRA_NML - Spectra output configuration (type 1)
    spectra_nml: Optional[Spectra] = PydanticField(
        default=None, 
        description=(
            "SPECTRA_NML configuration for spectra output (type 1). "
            "Defines spectra output parameters including output type, scale factor, "
            "and output factor for spectra output generation in WW3."
        )
    )

    # PARAM_NML - Mean parameter output configuration (type 2)
    param_nml: Optional[Param] = PydanticField(
        default=None, 
        description=(
            "PARAM_NML configuration for mean parameter output (type 2). "
            "Defines mean parameter output parameters including output type "
            "for mean parameter output generation in WW3."
        )
    )

    # SOURCE_NML - Source terms output configuration (type 3)
    source_nml: Optional[Source] = PydanticField(
        default=None, 
        description=(
            "SOURCE_NML configuration for source terms output (type 3). "
            "Defines source terms output parameters including output type, scale factor, "
            "output factor, table factor, and flags for source terms output generation in WW3."
        )
    )
