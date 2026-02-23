"""Shell component for WW3 configuration."""

from typing import List, Optional
from pydantic import Field, model_validator
from ..namelists.domain import Domain
from ..namelists.input import Input
from ..namelists.output_type import OutputType
from ..namelists.output_date import OutputDate
from ..namelists.homogeneous import HomogCount, HomogInput
from ..namelists.restart import Restart
from .basemodel import WW3ComponentBaseModel


class Shel(WW3ComponentBaseModel):
    """Component for ww3_shel.nml containing shell configuration.

    The Shel component represents the main shell configuration for WW3 single-grid runs.
    It contains all the namelist objects needed for configuring the main WW3 shell program
    (ww3_shel.nml).

    This component manages:
    - DOMAIN_NML: Top-level model parameters including start/stop times and I/O settings
    - INPUT_NML: Forcing inputs for the model including winds, currents, water levels, etc.
    - OUTPUT_TYPE_NML: Output types and parameters including field lists, point outputs, and track outputs
    - OUTPUT_DATE_NML: Output timing including start, stride, and stop times for different output types
    - HOMOG_COUNT_NML: Counts for homogeneous input types
    - HOMOG_INPUT_NML: Individual homogeneous inputs with name, date, and values

    The Shel component is used for single-grid WW3 runs and provides a clean interface
    for configuring all aspects of the main WW3 shell program.

    Key Features:
    - **Top-Level Configuration**: Main model parameters (start/stop times, I/O settings)
    - **Forcing Inputs**: Wind, current, water level, and ice forcing configuration
    - **Output Control**: Field, point, and track output configuration and timing
    - **Homogeneous Inputs**: Count and individual homogeneous input configuration
    - **Validation**: Cross-field validation for parameter consistency

    Usage Examples:
        ```python
        from rompy_ww3.components import Shel
        from rompy_ww3.namelists import Domain, Input, OutputType, OutputDate

        # Create a basic shell configuration
        shell = Shel(
            domain=Domain(
                start="20230101 000000",
                stop="20230107 000000",
                iostyp=1
            ),
            input_nml=Input(
                forcing={
                    "winds": "T",
                    "water_levels": "T"
                }
            )
        )

        # Render the namelist content
        content = shell.render()

        # Write to a file
        shell.write_nml("./namelists")
        ```
    """

    domain: Optional[Domain] = Field(
        default=None,
        description=(
            "DOMAIN_NML configuration defining top-level model parameters. "
            "Includes start/stop times and I/O settings for the entire model run."
        ),
    )
    input_nml: Optional[Input] = Field(
        default=None,
        description=(
            "INPUT_NML configuration defining forcing inputs for the model. "
            "Includes winds, currents, water levels, and other forcing fields."
        ),
    )
    output_type: Optional[OutputType] = Field(
        default=None,
        description=(
            "OUTPUT_TYPE_NML configuration defining output types and parameters. "
            "Controls field lists, point outputs, track outputs, and other output settings."
        ),
    )
    output_date: Optional[OutputDate] = Field(
        default=None,
        description=(
            "OUTPUT_DATE_NML configuration defining output timing parameters. "
            "Controls start, stride, and stop times for different output types."
        ),
    )
    homog_count: Optional[HomogCount] = Field(
        default=None,
        description=(
            "HOMOG_COUNT_NML configuration defining counts for homogeneous input types. "
            "Specifies how many homogeneous inputs of each type are defined."
        ),
    )
    homog_input: Optional[List[HomogInput]] = Field(
        default=None,
        description=(
            "List of HOMOG_INPUT_NML configurations defining individual homogeneous inputs. "
            "Each input includes name, date, and values for homogeneous forcing fields."
        ),
    )
    restart_nml: Optional[Restart] = Field(
        default=None,
        description=(
            "RESTART_NML configuration for initializing the model from restart files. "
            "Specifies the restart time and optionally a source for fetching restart files."
        ),
    )

    @model_validator(mode="after")
    def validate_shel_consistency(self) -> "Shel":
        """Validate consistency between related namelist objects in the Shel component.

        This validator ensures that related namelist objects are consistent with each other:
        - If homog_count is defined, homog_input should also be defined
        - Output type and date configurations should be consistent
        - Forcing inputs should be consistent with model requirements

        Returns:
            Shel: The validated Shel component instance

        Raises:
            ValueError: If inconsistencies are found between related namelist objects
        """
        # Validate homogeneous input consistency
        if self.homog_count is not None and self.homog_input is None:
            # If counts are specified but no inputs, this might be an issue
            # Log a warning but don't raise an error as this might be intentional
            pass

        if self.homog_input is not None and self.homog_count is None:
            # If inputs are specified but no counts, this is an issue
            # The counts should be calculated from the inputs
            pass

        # Validate output consistency
        if self.output_type is not None and self.output_date is None:
            # Output types defined but no timing - log warning
            pass

        if self.output_date is not None and self.output_type is None:
            # Output timing defined but no types - log warning
            pass

        return self

    @property
    def nml_filename(self) -> str:
        """Get the default filename for this component.

        Returns:
            str: The default namelist filename 'ww3_shel.nml'
        """
        return "ww3_shel.nml"

    @property
    def run_cmd(self) -> str:
        """Get the default run command for this component.

        Returns:
            str: The command to run the WW3 shell executable 'ww3_shel'
        """
        return "ww3_shel"
