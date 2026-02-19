"""Field output component for WW3 configuration."""

from typing import Optional
from pydantic import Field as PydanticField
from ..namelists.field import Field as FieldNML
from ..namelists.output_file import File as FileNML
from .basemodel import WW3ComponentBaseModel


class Ounf(WW3ComponentBaseModel):
    """Component for ww3_ounf.nml containing field (NetCDF) output configuration.

    The Ounf component represents the field output configuration for WW3.
    It contains the FIELD_NML and FILE_NML namelist objects needed for configuring
    the WW3 field output program (ww3_ounf.nml).

    This component manages:
    - FIELD_NML: Field output parameters including timing and field lists
    - FILE_NML: Output file parameters including naming and format

    The Ounf component is used for field output runs and provides a clean interface
    for configuring all aspects of the WW3 field output program.

    Key Features:
    - **Field Output**: Configuration for field output generation
    - **Timing Control**: Control over field output timing (start, stride, stop)
    - **Field Selection**: Choice of which fields to output
    - **Format Selection**: Choice of NetCDF format (version 3 or 4)
    - **File Management**: Field output file naming and organization

    Usage Examples:
        ```python
        from rompy_ww3.components import Ounf
        from rompy_ww3.namelists import Field, File

        # Create a field output configuration
        ounf = Ounf(
            field=Field(
                timestart="20230101 000000",
                timestride="3600",
                timecount="100",
                list="HS DIR SPR WND ICE CUR LEV"
            ),
            file=File(
                prefix="ww3_field.",
                netcdf=4
            )
        )

        # Render the namelist content
        content = ounf.render()

        # Write to a file
        ounf.write_nml("./namelists")
        ```
    """

    field: Optional[FieldNML] = PydanticField(
        default=None,
        description=(
            "FIELD_NML configuration for field output. "
            "Defines field output parameters including timing (start, stride, count), "
            "field lists, partitions, and format for field output generation in WW3."
        ),
    )
    file: Optional[FileNML] = PydanticField(
        default=None,
        description=(
            "FILE_NML configuration for output files. "
            "Defines output file parameters including naming prefix, NetCDF version, "
            "and spatial subsetting for field output files in WW3."
        ),
    )
