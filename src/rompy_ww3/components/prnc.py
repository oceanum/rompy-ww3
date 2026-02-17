"""Field preprocessor component for WW3 configuration."""

from typing import Optional
from pydantic import Field as PydanticField, model_validator
from ..namelists.forcing import Forcing
from ..namelists.file import File
from .basemodel import WW3ComponentBaseModel
from ..core.data import WW3DataBlob, WW3DataGrid


class Prnc(WW3ComponentBaseModel):
    """Component for ww3_prnc.nml containing field preprocessing configuration.

    The Prnc component represents the field preprocessing configuration for WW3.
    It contains the FORCING_NML and FILE_NML namelist objects needed for configuring
    the WW3 field preprocessing program (ww3_prnc.nml).

    This component manages:
    - FORCING_NML: Forcing field parameters for preprocessing
    - FILE_NML: Input file parameters for preprocessing

    The Prnc component is used for field preprocessing runs and provides a clean interface
    for configuring all aspects of the WW3 field preprocessing program.

    Key Features:
    - **Forcing Field Preprocessing**: Configuration for forcing field preprocessing
    - **File Input Processing**: Configuration for input file preprocessing
    - **Automatic Naming**: Automatic generation of namelist filenames based on forcing type
    - **Symbolic Linking**: Automatic setup of symbolic links for WW3 execution

    Usage Examples:
        ```python
        from rompy_ww3.components import Prnc
        from rompy_ww3.namelists import Forcing, File

        # Create a field preprocessing configuration
        prnc = Prnc(
            forcing=Forcing(
                timestart="20230101 000000",
                timestop="20230107 000000",
                field={"winds": "T"},
                grid={"latlon": "T"}
            ),
            file=File(
                filename="wind.nc",
                longitude="longitude",
                latitude="latitude",
                var1="U",
                var2="V"
            )
        )

        # Get the namelist filename
        filename = prnc.nml_filename  # Automatically generated based on forcing type

        # Get the prepend command
        cmd = prnc.prepend_cmd  # Sets up symbolic link

        # Render the namelist content
        content = prnc.render()

        # Write to a file
        prnc.write_nml("./namelists")
        ```
    """

    forcing: Optional[Forcing] = PydanticField(
        default=None,
        description=(
            "FORCING_NML configuration for field preprocessing. "
            "Defines forcing field parameters including start/stop times, field types, "
            "grid types, and tidal constituents for preprocessing input data."
        ),
    )
    file: Optional[File] = PydanticField(
        default=None,
        description=(
            "FILE_NML configuration for input file preprocessing. "
            "Defines input file parameters including filename, longitude/latitude dimension names, "
            "variable names (var1, var2, var3), and time shift for preprocessing input data."
        ),
    )

    @property
    def nml_filename(self) -> str:
        """Get the default filename for this component.

        Returns the WW3-standard filename for field preprocessing namelists based on
        the forcing variable name. For example, if the forcing variable is 'WND',
        returns 'ww3_prnc.wnd'.

        Returns:
            str: The default namelist filename based on forcing variable name
        """
        if self.forcing and hasattr(self.forcing, "ww3_var_name"):
            return f"ww3_prnc.{self.forcing.ww3_var_name}"
        return "ww3_prnc.nml"

    @property
    def prepend_cmd(self) -> str:
        """Get the string to prepend to the namelist file.

        Creates a symbolic link from the generated namelist filename to the standard
        WW3 preprocessing namelist name 'ww3_prnc.nml'. This is needed because WW3
        preprocessing programs expect the namelist file to be named 'ww3_prnc.nml'.

        Returns:
            str: Command to create symbolic link from generated filename to 'ww3_prnc.nml'
        """
        return f"ln -sf {self.nml_filename} ww3_prnc.nml"

    @model_validator(mode="after")
    def set_datasource_id(self):
        """Ensure id are constent with WW3DataGrid.

        This validator ensures that the datasource IDs are consistent with WW3DataGrid
        by setting the filename ID to match the forcing variable name in lowercase.

        This is needed to maintain consistency between the Prnc component and the
        WW3DataGrid data source specifications.

        Returns:
            Prnc: The validated Prnc component instance

        Raises:
            ValueError: If there are issues with the datasource ID configuration
        """
        if (
            self.file is not None
            and self.forcing is not None
            and self.forcing.ww3_var_name is not None
            and isinstance(self.file.filename, (WW3DataBlob, WW3DataGrid))
        ):
            self.file.filename.id = self.forcing.ww3_var_name.lower()
        return self
