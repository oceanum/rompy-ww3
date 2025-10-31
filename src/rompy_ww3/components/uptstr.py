"""Restart update component for WW3 configuration."""

from typing import Optional
from pydantic import Field
from ..namelists.restartupdate import RestartUpdate
from .basemodel import WW3ComponentBaseModel


class Uptstr(WW3ComponentBaseModel):
    """Component for ww3_uprstr.nml containing restart update configuration.

    The Uptstr component represents the restart configuration for WW3.
    It contains the RESTART_UPDATE_NML namelist object needed for configuring
    the WW3 restart update program (ww3_uprstr.nml).

    This component manages:
    - RESTART_UPDATE_NML: Restart file update parameters including timing and update method

    The Uptstr component is used for restart update runs and provides a clean interface
    for configuring all aspects of the WW3 restart update program.

    Key Features:
    - **Restart File Updates**: Configuration for updating existing restart files
    - **Timing Control**: Control over when restart updates occur (time, stride)
    - **Update Methods**: Choice of update method (replace, add, multiply)
    - **Field Selection**: Selection of which fields to update (wave, water level, current, ice, wind)
    - **File Management**: Input/output restart file specification

    Usage Examples:
        ```python
        from rompy_ww3.components import Uptstr
        from rompy_ww3.namelists import RestartUpdate

        # Create a restart update configuration
        uptstr = Uptstr(
            restart_update=RestartUpdate(
                update_time="20230101 000000",
                update_stride="43200",
                input_restart="restart_in.nc",
                output_restart="restart_out.nc",
                wave_field=True,
                water_level=True,
                current=True,
                ice=True,
                wind=True,
                update_method="replace"
            )
        )

        # Render the namelist content
        content = uptstr.render()

        # Write to a file
        uptstr.write_nml("./namelists")
        ```
    """

    restart_update: Optional[RestartUpdate] = Field(
        default=None,
        description=(
            "RESTART_UPDATE_NML configuration for restart file updates. "
            "Defines restart file update parameters including timing (time, stride), "
            "input/output file specification, field selection (wave, water level, current, ice, wind), "
            "and update method (replace, add, multiply) for restart file updates in WW3."
        ),
    )

    @property
    def nml_filename(self) -> str:
        """Get the default filename for this component.

        Returns:
            str: The default namelist filename 'ww3_uprstr.nml'
        """
        return "ww3_uprstr.nml"

    @property
    def run_cmd(self) -> str:
        """Get the default run command for this component.

        Returns:
            str: The command to run the WW3 restart update executable 'ww3_uprstr'
        """
        return "ww3_uprstr"

