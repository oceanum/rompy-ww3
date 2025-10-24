"""WW3 Rompy config."""

import logging
import os
from pathlib import Path
from typing import Literal, Optional, List, Dict, Any
from pydantic import Field as PydanticField

from rompy.core.config import BaseConfig
from rompy_ww3.data import AnyWW3Data
from rompy_ww3.grid import AnyWw3Grid

from .components import (
    Shel,
    Grid,
    Multi,
    Bound,
    Bounc,
    Prnc,
    Trnc,
    Ounf,
    Ounp,
    Uptstr,
    Namelists,
)

logger = logging.getLogger(__name__)

HERE = Path(__file__).parent


class BaseWW3Config(BaseConfig):
    """Base config class for WW3 models."""

    model_type: Literal["ww3_base"] = PydanticField(
        default="ww3_base",
        description="Model type discriminator",
    )
    template: str = PydanticField(
        default=str(HERE / "templates" / "base"),
        description="The model config template directory",
    )

    @property
    def components(self) -> List[str]:
        """Return a list of component names for WW3 namelists."""
        return [
            "grid_component",
            "boundary_component",
            "boundary_update_component",
            "parameters_component",
            "field_preprocessor_component",
            "shell_component",
            "multi_component",
            "track_component",
            "field_output_component",
            "point_output_component",
            "restart_update_component",
        ]

    def write_control_files(self, destdir: Path) -> None:
        """Write all namelists to the specified working directory."""
        for component_name in self.components:
            component = getattr(self, component_name)
            if component is not None:
                component.write_nml(destdir)


class NMLConfig(BaseWW3Config):
    """WW3 namelist-based config class.
    This class provides direct control over WW3 namelists via component objects.
    """

    model_type: Literal["nml"] = PydanticField(
        default="nml",
        description="Model type discriminator",
    )

    @property
    def main_template(self) -> str:
        """Return the path to the main template file."""
        return str(HERE / "templates" / "base" / "ww3_shel.nml")

    # WW3-specific component configurations
    shell_component: Optional[Shel] = PydanticField(
        default=None, description="Shell component (ww3_shel.nml) configuration"
    )
    grid_component: Optional[Grid] = PydanticField(
        default=None, description="Grid component (ww3_grid.nml) configuration"
    )
    multi_component: Optional[Multi] = PydanticField(
        default=None, description="Multi-grid component (ww3_multi.nml) configuration"
    )
    boundary_component: Optional[Bound] = PydanticField(
        default=None, description="Boundary component (ww3_bound.nml) configuration"
    )
    boundary_update_component: Optional[Bounc] = PydanticField(
        default=None,
        description="Boundary update component (ww3_bounc.nml) configuration",
    )
    field_preprocessor_component: Optional[Prnc] = PydanticField(
        default=None,
        description="Field preprocessor component (ww3_prnc.nml) configuration",
    )
    track_component: Optional[Trnc] = PydanticField(
        default=None, description="Track component (ww3_trnc.nml) configuration"
    )
    field_output_component: Optional[Ounf] = PydanticField(
        default=None,
        description="Field output component (ww3_ounf.nml) configuration",
    )
    point_output_component: Optional[Ounp] = PydanticField(
        default=None, description="Point output component (ww3_ounp.nml) configuration"
    )
    restart_update_component: Optional[Uptstr] = PydanticField(
        default=None,
        description="Restart update component (ww3_uprstr.nml) configuration",
    )
    parameters_component: Optional[Namelists] = PydanticField(
        default=None, description="Namelists component (namelists.nml) configuration"
    )

    def generate_run_script(self, destdir: Path) -> None:
        """Generate a basic WW3 run script."""
        run = ["#!/bin/bash"]
        preprocess = ["#!/bin/bash"]
        post = ["#!/bin/bash"]
        full = ["#!/bin/bash"]

        for component_name in self.components:
            if component_name == "parameters_component":
                continue  # Namelists component does not have a run command
            component = getattr(self, component_name)
            if component is not None:
                if component_name in ("multi_component", "shell_component"):
                    run.append(component.run_cmd)
                    full.append(component.run_cmd)
                elif component_name in (
                    "grid_component",
                    "boundary_component",
                    "field_preprocessor_component",
                ):
                    preprocess.append(component.run_cmd)
                    full.append(component.run_cmd)
                elif component_name in (
                    "field_output_component",
                    "point_output_component",
                ):
                    post.append(component.run_cmd)
                    full.append(component.run_cmd)
                else:
                    full.append(component.run_cmd)

        with open(Path(destdir) / "run_ww3.sh", "w") as f:
            f.write("\n".join(run))
            # Make the script executable
        os.chmod(Path(destdir) / "run_ww3.sh", 0o755)
        with open(Path(destdir) / "preprocess_ww3.sh", "w") as f:
            f.write("\n".join(preprocess))
        os.chmod(Path(destdir) / "preprocess_ww3.sh", 0o755)
        with open(Path(destdir) / "postprocess_ww3.sh", "w") as f:
            f.write("\n".join(post))
        os.chmod(Path(destdir) / "postprocess_ww3.sh", 0o755)
        with open(Path(destdir) / "full_ww3.sh", "w") as f:
            f.write("\n".join(full))
        os.chmod(Path(destdir) / "full_ww3.sh", 0o755)

    def __call__(self, runtime) -> dict:
        """Callable where data and config are interfaced and CMD is rendered."""

        # Generate WW3 control namelist files
        self.write_control_files(runtime.staging_dir)

        # Generate execution scripts based on what files and executables are needed
        self.generate_run_script(runtime.staging_dir)

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


class WW3ShelConfig(BaseConfig):
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

    grid: Optional[AnyWw3Grid] = PydanticField(
        default=None, description="WW3 Grid object configuration"
    )
    data: Optional[List["AnyWW3Data"]] = PydanticField(
        default=None, description="WW3 Data object for forcing data"
    )

    # Optional component configurations (for advanced users who need direct namelist control)
    shell_component: Optional[Shel] = PydanticField(
        default=None, description="Shell component (ww3_shel.nml) configuration"
    )
    grid_component: Optional[Grid] = PydanticField(
        default=None, description="Grid component (ww3_grid.nml) configuration"
    )
    boundary_component: Optional[Bound] = PydanticField(
        default=None, description="Boundary component (ww3_bound.nml) configuration"
    )
    boundary_update_component: Optional[Bounc] = PydanticField(
        default=None,
        description="Boundary update component (ww3_bounc.nml) configuration",
    )
    field_preprocessor_component: Optional[Prnc] = PydanticField(
        default=None,
        description="Field preprocessor component (ww3_prnc.nml) configuration",
    )
    track_component: Optional[Trnc] = PydanticField(
        default=None, description="Track component (ww3_trnc.nml) configuration"
    )
    field_output_component: Optional[Ounf] = PydanticField(
        default=None,
        description="Field output component (ww3_ounf.nml) configuration",
    )
    point_output_component: Optional[Ounp] = PydanticField(
        default=None, description="Point output component (ww3_ounp.nml) configuration"
    )
    restart_update_component: Optional[Uptstr] = PydanticField(
        default=None,
        description="Restart update component (ww3_uprstr.nml) configuration",
    )
    parameters_component: Optional[Namelists] = PydanticField(
        default=None, description="Namelists component (namelists.nml) configuration"
    )

    def __call__(self, runtime) -> dict:
        """Callable where data and config are interfaced and CMD is rendered."""
        staging_dir = Path(runtime.staging_dir)

        # Prepare staging directories for WW3 run
        data_dir = staging_dir / "data"
        grid_dir = staging_dir / "grid"
        namelists_dir = staging_dir / "namelists"

        data_dir.mkdir(parents=True, exist_ok=True)
        grid_dir.mkdir(parents=True, exist_ok=True)
        namelists_dir.mkdir(parents=True, exist_ok=True)

        # Process grid files using functional objects
        if self.grid:
            logger.info("Processing grid data using WW3 Grid object...")
            grid_files = self.grid.get(grid_dir)
        else:
            grid_files = {}

        # Process multiple grids if provided
        if self.grids:
            logger.info(f"Processing {len(self.grids)} grid objects...")
            for i, grid in enumerate(self.grids):
                sub_grid_dir = grid_dir / f"grid_{i}"
                sub_grid_dir.mkdir(parents=True, exist_ok=True)
                grid_files[f"grid_{i}"] = grid.get(sub_grid_dir)

        # Process data files using functional objects
        if self.data:
            logger.info("Processing forcing data using WW3 Data object...")
            data_files = self.data.get(data_dir)
        else:
            data_files = {}

        # Cross-validation between grid and data objects if both are provided
        if self.grid and self.data:
            try:
                self._validate_grid_data_consistency(self.grid, self.data)
            except Exception as e:
                logger.warning(f"Grid-data consistency validation failed: {str(e)}")
                # Continue execution but log the issue

        # Generate namelists from grid objects directly
        namelist_files = {}
        if self.grid:
            # Use grid object's namelist generation methods
            grid_nml_content = self.grid.grid_nml.render()
            with open(namelists_dir / "ww3_grid.nml", "w") as f:
                f.write(grid_nml_content)
            namelist_files["ww3_grid.nml"] = grid_nml_content

            # Add grid-specific namelist
            grid_specific_nml_content = self.grid.grid_specific_nml.render()
            grid_specific_filename = f"ww3_{self.grid.grid_specific_name}.nml"
            with open(namelists_dir / grid_specific_filename, "w") as f:
                f.write(grid_specific_nml_content)
            namelist_files[grid_specific_filename] = grid_specific_nml_content

            # Add optional namelists if grid has them
            optional_namelists = {}
            self.grid._add_optional_namelists(optional_namelists)
            for nml_name, nml_obj in optional_namelists.items():
                if hasattr(nml_obj, "render"):
                    filename = f"ww3_{nml_name}.nml"
                    with open(namelists_dir / filename, "w") as f:
                        f.write(nml_obj.render())
                    namelist_files[filename] = nml_obj.render()

        # Generate namelists from data objects directly
        if self.data:
            # Use data object's namelist generation methods
            forcing_nml = self.data.get_forcing_nml()
            forcing_content = forcing_nml.render()
            with open(namelists_dir / "ww3_prnc.nml", "w") as f:
                f.write(forcing_content)
            namelist_files["ww3_prnc.nml"] = forcing_content

        # Generate remaining namelists from components if provided
        # (for advanced users who need direct namelist control)
        if self.shell_component:
            shell_content = self.shell_component.render()
            with open(namelists_dir / "ww3_shel.nml", "w") as f:
                f.write(shell_content)
            namelist_files["ww3_shel.nml"] = shell_content

        if self.multi_component:
            multi_content = self.multi_component.render()
            with open(namelists_dir / "ww3_multi.nml", "w") as f:
                f.write(multi_content)
            namelist_files["ww3_multi.nml"] = multi_content

        if self.boundary_component:
            boundary_content = self.boundary_component.render()
            with open(namelists_dir / "ww3_bound.nml", "w") as f:
                f.write(boundary_content)
            namelist_files["ww3_bound.nml"] = boundary_content

        if self.boundary_update_component:
            boundary_update_content = self.boundary_update_component.render()
            with open(namelists_dir / "ww3_bounc.nml", "w") as f:
                f.write(boundary_update_content)
            namelist_files["ww3_bounc.nml"] = boundary_update_content

        if self.field_preprocessor_component:
            control_content = self.field_preprocessor_component.render()
            with open(namelists_dir / "ww3_prnc.nml", "w") as f:
                f.write(control_content)
            namelist_files["ww3_prnc.nml"] = (
                control_content  # Override with component if provided
            )

        if self.track_component:
            track_content = self.track_component.render()
            with open(namelists_dir / "ww3_trnc.nml", "w") as f:
                f.write(track_content)
            namelist_files["ww3_trnc.nml"] = track_content

        if self.field_output_component:
            unformatted_content = self.field_output_component.render()
            with open(namelists_dir / "ww3_ounf.nml", "w") as f:
                f.write(unformatted_content)
            namelist_files["ww3_ounf.nml"] = unformatted_content

        if self.point_output_component:
            point_content = self.point_output_component.render()
            with open(namelists_dir / "ww3_ounp.nml", "w") as f:
                f.write(point_content)
            namelist_files["ww3_ounp.nml"] = point_content

        if self.restart_update_component:
            restart_content = self.restart_update_component.render()
            with open(namelists_dir / "ww3_uprstr.nml", "w") as f:
                f.write(restart_content)
            namelist_files["ww3_uprstr.nml"] = restart_content

        if self.parameters_component:
            params_content = self.parameters_component.render()
            with open(namelists_dir / "namelists.nml", "w") as f:
                f.write(params_content)
            namelist_files["namelists.nml"] = params_content

        # Generate execution scripts based on what files and executables are needed
        self.generate_run_script(staging_dir)

        ret = {
            "staging_dir": str(staging_dir),
            "namelists_dir": str(namelists_dir),
            "data_dir": str(data_dir) if self.data else None,
            "grid_dir": str(grid_dir) if (self.grid or self.grids) else None,
            "grid_files": grid_files,
            "data_files": data_files,
            "namelist_files": namelist_files,
        }
        return ret

    def _validate_grid_data_consistency(
        self, grid: "AnyWw3Grid", data: "AnyWW3Data"
    ) -> None:
        """Validate consistency between grid and data objects."""
        # Check that temporal ranges are compatible
        if (
            data.start_time
            and data.end_time
            and hasattr(grid, "x")
            and hasattr(grid, "y")
        ):
            logger.info("Validating grid-data consistency...")
            # Additional validation logic would go here
            # For now, we'll just validate that both exist
            if grid and data:
                logger.debug("Grid and data objects are both present and valid.")

        # Check coordinate system compatibility if applicable
        # Additional cross-validation logic would go here

    def render_namelists(self) -> Dict[str, str]:
        """Render all namelists as strings and return as a dictionary."""
        namelists = {}

        # Generate namelists from grid objects directly
        if self.grid:
            namelists["ww3_grid.nml"] = self.grid.grid_nml.render()
            namelists[f"ww3_{self.grid.grid_specific_name}.nml"] = (
                self.grid.grid_specific_nml.render()
            )

            # Add optional namelists from grid
            optional_namelists = {}
            self.grid._add_optional_namelists(optional_namelists)
            for nml_name, nml_obj in optional_namelists.items():
                if hasattr(nml_obj, "render"):
                    namelists[f"ww3_{nml_name}.nml"] = nml_obj.render()

        # Generate namelists from data objects directly
        if self.data:
            forcing_nml = self.data.get_forcing_nml()
            namelists["ww3_prnc.nml"] = forcing_nml.render()

        # Generate remaining namelists from components if provided
        # (for advanced users who need direct namelist control)
        if self.shell_component:
            namelists["ww3_shel.nml"] = self.shell_component.render()

        if self.multi_component:
            namelists["ww3_multi.nml"] = self.multi_component.render()

        if self.boundary_component:
            namelists["ww3_bound.nml"] = self.boundary_component.render()

        if self.boundary_update_component:
            namelists["ww3_bounc.nml"] = self.boundary_update_component.render()

        if self.field_preprocessor_component:
            namelists["ww3_prnc.nml"] = (
                self.field_preprocessor_component.render()
            )  # Override with component if provided

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


#
#
# class WW3MultiConfig(BaseConfig):
#     # High-level WW3 configuration objects
#     grids: Optional[List[AnyWw3Grid]] = PydanticField(
#         default=None, description="WW3 Grid object configuration"
#     )
