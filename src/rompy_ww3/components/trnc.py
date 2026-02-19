"""Track component for WW3 configuration."""

from typing import Optional
from pydantic import Field as PydanticField
from ..namelists.track import Track
from .basemodel import WW3ComponentBaseModel


class Trnc(WW3ComponentBaseModel):
    """Component for ww3_trnc.nml containing track output configuration.

    The Trnc component represents the track output configuration for WW3.
    It contains the TRACK_NML namelist object needed for configuring the WW3 track
    output program (ww3_trnc.nml).

    This component manages:
    - TRACK_NML: Track output parameters including timing and format

    The Trnc component is used for track output runs and provides a clean interface
    for configuring all aspects of the WW3 track output program.

    Key Features:
    - **Track Output**: Configuration for track output generation
    - **Timing Control**: Control over track output timing (start, stride, stop)
    - **Format Selection**: Choice of formatted/unformatted output
    - **File Management**: Track output file naming and organization

    Usage Examples:
        ```python
        from rompy_ww3.components import Trnc
        from rompy_ww3.namelists import Track

        # Create a track output configuration
        trnc = Trnc(
            track=Track(
                timestart="20230101 000000",
                timestride="3600",
                timecount="100",
                timesplit=8
            )
        )

        # Render the namelist content
        content = trnc.render()

        # Write to a file
        trnc.write_nml("./namelists")
        ```
    """

    track: Optional[Track] = PydanticField(
        default=None,
        description=(
            "TRACK_NML configuration for track output. "
            "Defines track output parameters including timing (start, stride, count, split) "
            "and format for track output generation in WW3."
        ),
    )
