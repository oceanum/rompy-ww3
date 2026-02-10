"""Multi-component for WW3 multi-grid configuration."""

from typing import Optional, List
from pydantic import Field as PydanticField
from ..namelists.domain import Domain
from ..namelists.input import InputGrid, ModelGrid
from ..namelists.output_type import OutputType
from ..namelists.output_date import OutputDate
from ..namelists.homogeneous import HomogCount
from .basemodel import WW3ComponentBaseModel


class Multi(WW3ComponentBaseModel):
    """Component for ww3_multi.nml containing multi-grid configuration.

    The Multi component represents the multi-grid configuration for WW3.
    It contains all the namelist objects needed for configuring the WW3 multi-grid
    program (ww3_multi.nml).

    This component manages:
    - DOMAIN_NML: Multi-grid model parameters including start/stop times and I/O settings
    - INPUT_GRID_NML: Input grid specification for multi-grid models
    - MODEL_GRID_NML: Model grid specification for multi-grid models
    - OUTPUT_TYPE_NML: Output type configuration for multi-grid models
    - OUTPUT_DATE_NML: Output date configuration for multi-grid models
    - HOMOG_COUNT_NML: Homogeneous input count configuration for multi-grid models

    The Multi component is used for multi-grid WW3 runs and provides a clean interface
    for configuring all aspects of the WW3 multi-grid program.

    Key Features:
    - **Multi-Grid Support**: Configuration for multiple interconnected grids
    - **Grid Communication**: Input/output grid specification and communication
    - **Output Management**: Multi-grid output type and date configuration
    - **Homogeneous Inputs**: Multi-grid homogeneous input count management

    Usage Examples:
        ```python
        from rompy_ww3.components import Multi
        from rompy_ww3.namelists import Domain, InputGrid, ModelGrid

        # Create a multi-grid configuration
        multi = Multi(
            domain=Domain(
                start="20230101 000000",
                stop="20230107 000000",
                iostyp=1
            ),
            input_grid=InputGrid(
                name="coarse_grid",
                forcing={"winds": "T"}
            )
        )

        # Render the namelist content
        content = multi.render()

        # Write to a file
        multi.write_nml("./namelists")
        ```
    """

    domain: Optional[Domain] = PydanticField(
        default=None,
        description=(
            "DOMAIN_NML configuration for multi-grid model parameters. "
            "Includes start/stop times, I/O settings, and multi-grid specific parameters "
            "such as number of input grids (nrinp) and number of model grids (nrgrd)."
        ),
    )
    input_grid: Optional[InputGrid] = PydanticField(
        default=None,
        description=(
            "INPUT_GRID_NML configuration for input grid specification. "
            "Defines the input grids for multi-grid models including grid names and forcing parameters."
        ),
    )
    model_grid: Optional[ModelGrid] = PydanticField(
        default=None,
        description=(
            "MODEL_GRID_NML configuration for model grid specification. "
            "Defines the model grids for multi-grid models including grid names and model parameters."
        ),
    )
    model_grids: Optional[List[ModelGrid]] = PydanticField(
        default=None,
        description=(
            "List of MODEL_GRID_NML configurations for multiple model grids. "
            "Each model grid includes grid names and model parameters for multi-grid runs."
        ),
    )
    output_type: Optional[OutputType] = PydanticField(
        default=None,
        description=(
            "OUTPUT_TYPE_NML configuration for multi-grid output types. "
            "Defines output types and parameters for multi-grid models including field lists and point outputs."
        ),
    )
    output_date: Optional[OutputDate] = PydanticField(
        default=None,
        description=(
            "OUTPUT_DATE_NML configuration for multi-grid output dates. "
            "Defines output timing parameters for multi-grid models including start, stride, and stop times."
        ),
    )
    homog_count: Optional[HomogCount] = PydanticField(
        default=None,
        description=(
            "HOMOG_COUNT_NML configuration for multi-grid homogeneous input counts. "
            "Defines the number of homogeneous inputs for multi-grid models."
        ),
    )

    def render(self, *args, **kwargs) -> str:
        """Render the multi-grid component as a combined namelist string.

        Generates the complete namelist content for the WW3 multi-grid configuration by
        rendering all contained namelist objects in the proper order.

        The rendering order follows WW3 conventions:
        1. DOMAIN_NML - Multi-grid model parameters
        2. INPUT_GRID_NML - Input grid specification
        3. MODEL_GRID_NML - Model grid specification
        4. OUTPUT_TYPE_NML - Multi-grid output types
        5. OUTPUT_DATE_NML - Multi-grid output dates
        6. HOMOG_COUNT_NML - Multi-grid homogeneous input counts

        Args:
            *args: Variable positional arguments (ignored but accepted for compatibility)
            **kwargs: Variable keyword arguments (ignored but accepted for compatibility)

        Returns:
            str: The rendered multi-grid configuration as a combined namelist string
        """
        multi_content = []
        multi_content.append("! WW3 multi-grid model configuration")
        multi_content.append("! Generated by rompy-ww3")
        multi_content.append("")

        # Add DOMAIN_NML (for multi-grid specific parameters)
        if self.domain:
            rendered = self.domain.render()
            multi_content.extend(rendered.split("\n"))
            multi_content.append("")

        # Add INPUT_GRID_NML if defined
        if self.input_grid:
            rendered = self.input_grid.render()
            multi_content.extend(rendered.split("\n"))
            multi_content.append("")
        elif self.model_grids:  # If we have model grids but no specific input grid
            for i, model_grid in enumerate(self.model_grids):
                # Assuming each model grid has corresponding input
                if model_grid.name:
                    input_grid_nml = f"&INPUT_GRID_NML\n  INPUT({i + 1})%NAME = '{model_grid.name}'\n/\n"
                    multi_content.append(input_grid_nml)
                    multi_content.append("")

        # Add MODEL_GRID_NML configurations
        if self.model_grids:
            for i, model_grid in enumerate(self.model_grids):
                rendered = model_grid.render()
                # Replace the namelist name to be MODEL_GRID_NML instead of whatever is in the render
                lines = rendered.split("\n")
                updated_lines = []
                for line in lines:
                    if line.strip().startswith("&"):
                        updated_lines.append("&MODEL_GRID_NML")
                    elif line.strip() == "/":
                        updated_lines.append(
                            f"  MODEL_NAME = '{model_grid.name}'  ! Index: {i + 1}"
                        )
                        updated_lines.append("/")
                    else:
                        updated_line = line.replace("MODEL_GRID%", f"MODEL({i + 1})%")
                        updated_lines.append(updated_line)
                multi_content.extend(updated_lines)
                multi_content.append("")
        elif self.model_grid:  # Single model grid
            rendered = self.model_grid.render()
            # Replace the namelist name and fields to use proper indexed format
            lines = rendered.split("\n")
            updated_lines = []
            for line in lines:
                if line.strip().startswith("&"):
                    updated_lines.append("&MODEL_GRID_NML")
                elif line.strip() == "/":
                    updated_lines.append(
                        f"  MODEL_NAME = '{self.model_grid.name}'  ! Index: 1"
                    )
                    updated_lines.append("/")
                else:
                    updated_line = line.replace("MODEL_GRID%", "MODEL(1)%")
                    updated_lines.append(updated_line)
            multi_content.extend(updated_lines)
            multi_content.append("")

        # Add OUTPUT_TYPE_NML
        if self.output_type:
            rendered = self.output_type.render()
            multi_content.extend(rendered.split("\n"))
            multi_content.append("")

        # Add OUTPUT_DATE_NML
        if self.output_date:
            rendered = self.output_date.render()
            multi_content.extend(rendered.split("\n"))
            multi_content.append("")

        # Add HOMOG_COUNT_NML if needed for multi-grid
        if self.homog_count:
            rendered = self.homog_count.render()
            multi_content.extend(rendered.split("\n"))
            multi_content.append("")

        return "\n".join(multi_content)
