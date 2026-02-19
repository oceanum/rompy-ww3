"""Boundary update component for WW3 configuration."""

from typing import Optional
from pydantic import Field
from .basemodel import WW3ComponentBaseModel
from ..namelists.bound import Bound


class Bounc(WW3ComponentBaseModel):
    """Component for ww3_bounc.nml containing boundary update configuration.

    The Bounc component represents the boundary update configuration for WW3 multi-grid runs.
    It contains the BOUND_NML namelist object needed for configuring the WW3 boundary update
    program (ww3_bounc.nml).

    This component manages:
    - BOUND_NML: Boundary preprocessing parameters including mode, interpolation, and verbosity

    The Bounc component is used for boundary update runs in multi-grid configurations and provides
    a clean interface for configuring all aspects of the WW3 boundary update program.

    Key Features:
    - **Boundary Processing**: Configuration for boundary data processing
    - **Interpolation**: Interpolation method selection for boundary data
    - **Verbosity**: Control over output verbosity during boundary processing
    - **File Handling**: Input/output file specification for boundary data

    Usage Examples:
        ```python
        from rompy_ww3.components import Bounc
        from rompy_ww3.namelists import Bound

        # Create a boundary update configuration
        bounc = Bounc(
            bound=Bound(
                mode="WRITE",
                interp=2,
                verbose=1
            )
        )

        # Render the namelist content
        content = bounc.render()

        # Write to a file
        bounc.write_nml("./namelists")
        ```
    """

    bound: Optional[Bound] = Field(
        default=None,
        description=(
            "BOUND_NML configuration for boundary preprocessing. "
            "Defines mode (WRITE/READ), interpolation method, verbosity level, "
            "and input/output file specification for boundary data processing."
        ),
    )
