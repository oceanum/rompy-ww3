"""WW3 Rompy config."""

import logging
import os
from pathlib import Path
from typing import Literal, Optional, List, Dict, Any
from pydantic import Field as PydanticField

from rompy.core.config import BaseConfig
from .grid import AnyWw3Grid
from .data import Data as DataModel
from .components import (
    ShellComponent,
    GridComponent,
    MultiComponent,
    BoundaryComponent,
    BoundaryUpdateComponent,
    FieldPreprocessorComponent,
    TrackComponent,
    FieldOutputComponent,
    PointOutputComponent,
    RestartUpdateComponent,
    ParametersComponent,
)

logger = logging.getLogger(__name__)

HERE = Path(__file__).parent
WW3_DIR = os.getenv("WW3_DIR", "/path/to/ww3")  # Default path if WW3_DIR not set


class Config(BaseConfig):
    """Ww3 config class."""

    model_type: Literal["ww3"] = PydanticField(
        default="ww3",
        description="Model type discriminator",
    )
    template: str = PydanticField(
        default=str(HERE / "templates" / "base"),
        description="The model config template directory",
    )

    @property
    def main_template(self) -> str:
        """Return the path to the main template file."""
        return str(HERE / "templates" / "base" / "ww3_shel.nml")

    # WW3-specific component configurations
    shell_component: Optional[ShellComponent] = PydanticField(
        default=None, description="Shell component (ww3_shel.nml) configuration"
    )
    grid_component: Optional[GridComponent] = PydanticField(
        default=None, description="Grid component (ww3_grid.nml) configuration"
    )
    multi_component: Optional[MultiComponent] = PydanticField(
        default=None, description="Multi-grid component (ww3_multi.nml) configuration"
    )
    boundary_component: Optional[BoundaryComponent] = PydanticField(
        default=None, description="Boundary component (ww3_bound.nml) configuration"
    )
    boundary_update_component: Optional[BoundaryUpdateComponent] = PydanticField(
        default=None,
        description="Boundary update component (ww3_bounc.nml) configuration",
    )
    field_preprocessor_component: Optional[FieldPreprocessorComponent] = PydanticField(
        default=None,
        description="Field preprocessor component (ww3_prnc.nml) configuration",
    )
    track_component: Optional[TrackComponent] = PydanticField(
        default=None, description="Track component (ww3_trnc.nml) configuration"
    )
    field_output_component: Optional[FieldOutputComponent] = PydanticField(
        default=None,
        description="Field output component (ww3_ounf.nml) configuration",
    )
    point_output_component: Optional[PointOutputComponent] = PydanticField(
        default=None, description="Point output component (ww3_ounp.nml) configuration"
    )
    restart_update_component: Optional[RestartUpdateComponent] = PydanticField(
        default=None,
        description="Restart update component (ww3_uprstr.nml) configuration",
    )
    parameters_component: Optional[ParametersComponent] = PydanticField(
        default=None, description="Parameters component (namelists.nml) configuration"
    )

    def generate_run_script(self, staging_dir) -> str:
        """Generate a basic WW3 run script."""
        run = ["#!/bin/bash"]
        preprocess = ["#!/bin/bash"]
        post = ["#!/bin/bash"]
        full = ["#!/bin/bash"]
        if self.grid_component:
            cmd = f"{WW3_DIR}/ww3_grid > ww3_grid.log 2>&1"
            preprocess.append(cmd)
            full.append(cmd)
        if self.boundary_component:
            cmd = f"{WW3_DIR}/ww3_bound > ww3_bound.log 2>&1"
            preprocess.append(cmd)
            full.append(cmd)
        if self.field_preprocessor_component:
            cmd = f"{WW3_DIR}/ww3_prnc > ww3_prnc.log 2>&1"
            preprocess.append(cmd)
            full.append(cmd)
        if self.multi_component:
            cmd = f"{WW3_DIR}/ww3_multi > ww3_multi.log 2>&1"
            run.append(cmd)
            full.append(cmd)
        if self.shell_component:
            run.append(f"{WW3_DIR}/ww3_shel > ww3_shel.log 2>&1")
        if self.field_output_component:
            cmd = f"{WW3_DIR}/ww3_ounf > ww3_ounf.log 2>&1"
            post.append(cmd)
            full.append(cmd)
        if self.point_output_component:
            cmd = f"{WW3_DIR}/ww3_ounp > ww3_ounp.log 2>&1"
            post.append(cmd)
            full.append(cmd)
        with open(Path(staging_dir) / "run_ww3.sh", "w") as f:
            f.write("\n".join(run))
        with open(Path(staging_dir) / "preprocess_ww3.sh", "w") as f:
            f.write("\n".join(preprocess))
        with open(Path(staging_dir) / "postprocess_ww3.sh", "w") as f:
            f.write("\n".join(post))
        with open(Path(staging_dir) / "full_ww3.sh", "w") as f:
            f.write("\n".join(full))

    def __call__(self, runtime) -> dict:
        """Callable where data and config are interfaced and CMD is rendered."""
        staging_dir = runtime.staging_dir

        # Generate WW3 control namelist files
        namelists_dir = Path(staging_dir) / "namelists"
        namelists_dir.mkdir(parents=True, exist_ok=True)

        # Generate main shell namelist file (for single-grid models) using component
        if self.shell_component:
            shell_content = self.shell_component.render()
            with open(namelists_dir / "ww3_shel.nml", "w") as f:
                f.write(shell_content)

        # Generate multi-grid namelist file (for multi-grid models) using component
        if self.multi_component:
            multi_content = self.multi_component.render()
            with open(namelists_dir / "ww3_multi.nml", "w") as f:
                f.write(multi_content)

        # Generate grid preprocessing namelist using component
        if self.grid_component:
            grid_content = self.grid_component.render()
            with open(namelists_dir / "ww3_grid.nml", "w") as f:
                f.write(grid_content)

        # Generate boundary preprocessing namelist using component
        if self.boundary_component:
            boundary_content = self.boundary_component.render()
            with open(namelists_dir / "ww3_bound.nml", "w") as f:
                f.write(boundary_content)

        # Generate boundary update namelist using component
        if self.boundary_update_component:
            boundary_update_content = self.boundary_update_component.render()
            with open(namelists_dir / "ww3_bounc.nml", "w") as f:
                f.write(boundary_update_content)

        # Generate field preprocessor namelist using component
        if self.field_preprocessor_component:
            control_content = self.field_preprocessor_component.render()
            with open(namelists_dir / "ww3_prnc.nml", "w") as f:
                f.write(control_content)

        # Generate track output namelist using component
        if self.track_component:
            track_content = self.track_component.render()
            with open(namelists_dir / "ww3_trnc.nml", "w") as f:
                f.write(track_content)

        # Generate field output namelist using component
        if self.field_output_component:
            unformatted_content = self.field_output_component.render()
            with open(namelists_dir / "ww3_ounf.nml", "w") as f:
                f.write(unformatted_content)

        # Generate point output namelist using component
        if self.point_output_component:
            point_content = self.point_output_component.render()
            with open(namelists_dir / "ww3_ounp.nml", "w") as f:
                f.write(point_content)

        # Generate restart update namelist using component
        if self.restart_update_component:
            restart_content = self.restart_update_component.render()
            with open(namelists_dir / "ww3_uprstr.nml", "w") as f:
                f.write(restart_content)

        # Generate model parameters namelist using component
        if self.parameters_component:
            params_content = self.parameters_component.render()
            with open(namelists_dir / "namelists.nml", "w") as f:
                f.write(params_content)

        self.generate_runscript(staging_dir)

        ret = {
            "staging_dir": staging_dir,
            "namelists_dir": str(namelists_dir),
        }
        return ret

    def render_namelists(self) -> Dict[str, str]:
        """Render all namelists as strings and return as a dictionary."""
        namelists = {}

        # Use component-based rendering
        if self.shell_component:
            namelists["ww3_shel.nml"] = self.shell_component.render()

        if self.grid_component:
            namelists["ww3_grid.nml"] = self.grid_component.render()

        if self.multi_component:
            namelists["ww3_multi.nml"] = self.multi_component.render()

        if self.boundary_component:
            namelists["ww3_bound.nml"] = self.boundary_component.render()

        if self.boundary_update_component:
            namelists["ww3_bounc.nml"] = self.boundary_update_component.render()

        if self.field_preprocessor_component:
            namelists["ww3_prnc.nml"] = self.field_preprocessor_component.render()

        if self.track_component:
            namelists["ww3_trnc.nml"] = self.track_component.render()

        if self.field_output_component:
            namelists["ww3_ounf.nml"] = self.field_output_component.render()

        if self.point_output_component:
            namelists["ww3_ounp.nml"] = self.point_output_component.render()

        if self.restart_update_component:
            namelists["ww3_uprstr.nml"] = self.restart_update_component.render()

        if self.parameters_component:
            namelists["namelists.nml"] = self.parameters_component.render()

        return namelists

    def get_template_context(self) -> Dict[str, Any]:
        """Generate template context for Jinja2 templates.

        Returns:
            Dictionary containing context variables for templates
        """
        context = {
            "config": self,
        }

        # Add rendered namelists to context
        context["namelists"] = self.render_namelists()

        return context


class WW3Config(Config):
    """WW3 high-level config class that works with grid/data objects.

    This class accepts high-level objects (grid, data) and internally manages
    the conversion to appropriate namelist objects for WW3.
    """

    model_type: Literal["ww3"] = PydanticField(
        default="ww3",
        description="Model type discriminator",
    )
    template: str = PydanticField(
        default=str(HERE / "templates" / "base"),
        description="The model config template directory",
    )

    # WW3-specific component configurations
    shell_component: Optional[ShellComponent] = PydanticField(
        default=None, description="Shell component (ww3_shel.nml) configuration"
    )
    grid_component: Optional[GridComponent] = PydanticField(
        default=None, description="Grid component (ww3_grid.nml) configuration"
    )
    multi_component: Optional[MultiComponent] = PydanticField(
        default=None, description="Multi-grid component (ww3_multi.nml) configuration"
    )
    boundary_component: Optional[BoundaryComponent] = PydanticField(
        default=None, description="Boundary component (ww3_bound.nml) configuration"
    )
    boundary_update_component: Optional[BoundaryUpdateComponent] = PydanticField(
        default=None,
        description="Boundary update component (ww3_bounc.nml) configuration",
    )
    field_preprocessor_component: Optional[FieldPreprocessorComponent] = PydanticField(
        default=None,
        description="Field preprocessor component (ww3_prnc.nml) configuration",
    )
    track_component: Optional[TrackComponent] = PydanticField(
        default=None, description="Track component (ww3_trnc.nml) configuration"
    )
    field_output_component: Optional[FieldOutputComponent] = PydanticField(
        default=None,
        description="Field output component (ww3_ounf.nml) configuration",
    )
    point_output_component: Optional[PointOutputComponent] = PydanticField(
        default=None, description="Point output component (ww3_ounp.nml) configuration"
    )
    restart_update_component: Optional[RestartUpdateComponent] = PydanticField(
        default=None,
        description="Restart update component (ww3_uprstr.nml) configuration",
    )
    parameters_component: Optional[ParametersComponent] = PydanticField(
        default=None, description="Parameters component (namelists.nml) configuration"
    )

    # High-level WW3 configuration objects
    grid: Optional[AnyWw3Grid] = PydanticField(
        default=None, description="WW3 Grid object configuration"
    )
    grids: Optional[List[AnyWw3Grid]] = PydanticField(
        default=None,
        description="List of WW3 Grid objects (for multi-grid)",
    )
    data: Optional[DataModel] = PydanticField(
        default=None, description="WW3 Data object for forcing data"
    )

    def __call__(self, runtime) -> dict:
        """Callable where data and config are interfaced and CMD is rendered."""
        staging_dir = runtime.staging_dir

        # Prepare staging directory for WW3 run
        # This includes retrieving and staging data files using our new objects
        data_dir = Path(staging_dir) / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        grid_dir = Path(staging_dir) / "grid"
        grid_dir.mkdir(parents=True, exist_ok=True)

        # Use the new Grid object to get grid files and namelists
        if self.grid:  # The grid field is the WW3 Grid object
            logger.info("Processing grid data using WW3 Grid object...")
            self.grid.get(grid_dir)

        # Use the new Data object to get forcing data files
        if self.data:
            logger.info("Processing forcing data using WW3 Data object...")
            self.data.get(data_dir)

        # Generate WW3 control namelist files
        namelists_dir = Path(staging_dir) / "namelists"
        namelists_dir.mkdir(parents=True, exist_ok=True)

        # Generate main shell namelist file (for single-grid models) using component
        if self.shell_component:
            shell_content = self.shell_component.render()
            with open(namelists_dir / "ww3_shel.nml", "w") as f:
                f.write(shell_content)

        # Generate multi-grid namelist file (for multi-grid models) using component
        if self.multi_component:
            multi_content = self.multi_component.render()
            with open(namelists_dir / "ww3_multi.nml", "w") as f:
                f.write(multi_content)

        # Generate grid preprocessing namelist using component
        if self.grid_component:
            grid_content = self.grid_component.render()
            with open(namelists_dir / "ww3_grid.nml", "w") as f:
                f.write(grid_content)

        # Generate boundary preprocessing namelist using component
        if self.boundary_component:
            boundary_content = self.boundary_component.render()
            with open(namelists_dir / "ww3_bound.nml", "w") as f:
                f.write(boundary_content)

        # Generate boundary update namelist using component
        if self.boundary_update_component:
            boundary_update_content = self.boundary_update_component.render()
            with open(namelists_dir / "ww3_bounc.nml", "w") as f:
                f.write(boundary_update_content)

        # Generate field preprocessor namelist using component
        if self.field_preprocessor_component:
            control_content = self.field_preprocessor_component.render()
            with open(namelists_dir / "ww3_prnc.nml", "w") as f:
                f.write(control_content)

        # Generate track output namelist using component
        if self.track_component:
            track_content = self.track_component.render()
            with open(namelists_dir / "ww3_trnc.nml", "w") as f:
                f.write(track_content)

        # Generate field output namelist using component
        if self.field_output_component:
            unformatted_content = self.field_output_component.render()
            with open(namelists_dir / "ww3_ounf.nml", "w") as f:
                f.write(unformatted_content)

        # Generate point output namelist using component
        if self.point_output_component:
            point_content = self.point_output_component.render()
            with open(namelists_dir / "ww3_ounp.nml", "w") as f:
                f.write(point_content)

        # Generate restart update namelist using component
        if self.restart_update_component:
            restart_content = self.restart_update_component.render()
            with open(namelists_dir / "ww3_uprstr.nml", "w") as f:
                f.write(restart_content)

        # Generate model parameters namelist using component
        if self.parameters_component:
            params_content = self.parameters_component.render()
            with open(namelists_dir / "namelists.nml", "w") as f:
                f.write(params_content)

        ret = {
            "staging_dir": staging_dir,
            "namelists_dir": str(namelists_dir),
            "data_dir": str(data_dir) if self.data else None,
            "grid_dir": str(grid_dir) if self.grid else None,
        }
        return ret

    def render_namelists(self) -> Dict[str, str]:
        """Render all namelists as strings and return as a dictionary."""
        namelists = {}

        # Use component-based rendering
        if self.shell_component:
            namelists["ww3_shel.nml"] = self.shell_component.render()

        if self.grid_component:
            namelists["ww3_grid.nml"] = self.grid_component.render()

        if self.multi_component:
            namelists["ww3_multi.nml"] = self.multi_component.render()

        if self.boundary_component:
            namelists["ww3_bound.nml"] = self.boundary_component.render()

        if self.boundary_update_component:
            namelists["ww3_bounc.nml"] = self.boundary_update_component.render()

        if self.field_preprocessor_component:
            namelists["ww3_prnc.nml"] = self.field_preprocessor_component.render()

        if self.track_component:
            namelists["ww3_trnc.nml"] = self.track_component.render()

        if self.field_output_component:
            namelists["ww3_ounf.nml"] = self.field_output_component.render()

        if self.point_output_component:
            namelists["ww3_ounp.nml"] = self.point_output_component.render()

        if self.restart_update_component:
            namelists["ww3_uprstr.nml"] = self.restart_update_component.render()

        if self.parameters_component:
            namelists["namelists.nml"] = self.parameters_component.render()

        return namelists

    def get_template_context(self) -> Dict[str, Any]:
        """Generate template context for Jinja2 templates."""
        context = {
            "config": self,
        }

        # Add rendered namelists to context
        context["namelists"] = self.render_namelists()

        return context
