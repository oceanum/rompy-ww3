"""Boundary component for WW3 configuration."""

from typing import Optional
from pydantic import Field as PydanticField
from ..namelists.bound import Bound as BoundNML
from .basemodel import WW3ComponentBaseModel


class Bound(WW3ComponentBaseModel):
    """Component for ww3_bound.nml containing boundary configuration.

    The Bound component represents the boundary preprocessing configuration for WW3.
    It contains the BOUND_NML namelist object needed for configuring the WW3 boundary
    preprocessing program (ww3_bound.nml).

    This component manages:
    - BOUND_NML: Boundary preprocessing parameters including mode, interpolation, and verbosity

    The Bound component is used for boundary preprocessing runs and provides a clean interface
    for configuring all aspects of the WW3 boundary preprocessing program.

    Key Features:
    - **Boundary Processing**: Configuration for boundary data processing
    - **Interpolation**: Interpolation method selection for boundary data
    - **Verbosity**: Control over output verbosity during boundary processing
    - **File Handling**: Input/output file specification for boundary data

    Usage Examples:
        ```python
        from rompy_ww3.components import Bound
        from rompy_ww3.namelists import Bound as BoundNML

        # Create a boundary preprocessing configuration
        bound = Bound(
            bound=BoundNML(
                mode="READ",
                interp=2,
                verbose=1
            )
        )

        # Render the namelist content
        content = bound.render()

        # Write to a file
        bound.write_nml("./namelists")
        ```
    """

    bound: Optional[BoundNML] = PydanticField(
        default=None,
        description=(
            "BOUND_NML configuration for boundary preprocessing. "
            "Defines mode (READ/WRITE), interpolation method, verbosity level, "
            "and input/output file specification for boundary data processing."
        ),
    )
