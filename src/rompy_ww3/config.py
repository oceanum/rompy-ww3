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
            "ww3_grid",
            "ww3_bound",
            "boundary_update_component",
            "namelists",
            "ww3_prnc",
            "ww3_shel",
            "multi_component",
            "ww3_track",
            "ww3_ounf",
            "ww3_ounp",
            "ww3_upstr",
        ]

    def write_control_files(self, runtime) -> None:
        """Write all namelists to the specified working directory."""
        for component_name in self.components:
            component = getattr(self, component_name)
            if component is not None:
                if isinstance(component, list):
                    for idx, sub_component in enumerate(component):
                        sub_component.write_nml(
                            destdir=runtime.staging_dir,
                            grid=self.ww3_grid,
                            time=runtime.period,
                        )
                else:
                    component.write_nml(
                        destdir=runtime.staging_dir,
                        grid=self.ww3_grid,
                        time=runtime.period,
                    )

    def generate_run_script(self, destdir: Path) -> None:
        """Generate a basic WW3 run script."""
        run = ["#!/bin/bash"]
        preprocess = ["#!/bin/bash"]
        post = ["#!/bin/bash"]
        full = ["#!/bin/bash"]

        for component_name in self.components:
            if component_name == "namelists":
                continue  # Namelists component does not have a run command
            component = getattr(self, component_name)
            if component is not None:
                if component_name in ("multi_component", "ww3_shel"):
                    run.append(component.run_cmd)
                    full.append(component.run_cmd)
                elif component_name in (
                    "ww3_grid",
                    "ww3_bound",
                ):
                    preprocess.append(component.run_cmd)
                    full.append(component.run_cmd)
                elif component_name in ("ww3_prnc",):
                    if isinstance(component, list):
                        for sub_component in component:
                            preprocess.append(sub_component.run_cmd)
                            full.append(sub_component.run_cmd)
                    else:
                        preprocess.append(component.run_cmd)
                        full.append(component.run_cmd)
                elif component_name in (
                    "ww3_ounf",
                    "ww3_ounp",
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
    ww3_shel: Optional[Shel] = PydanticField(
        default=None, description="Shell component (ww3_shel.nml) configuration"
    )
    ww3_grid: Optional[Grid] = PydanticField(
        default=None, description="Grid component (ww3_grid.nml) configuration"
    )
    multi_component: Optional[Multi] = PydanticField(
        default=None, description="Multi-grid component (ww3_multi.nml) configuration"
    )
    ww3_bound: Optional[Bound] = PydanticField(
        default=None, description="Boundary component (ww3_bound.nml) configuration"
    )
    boundary_update_component: Optional[Bounc] = PydanticField(
        default=None,
        description="Boundary update component (ww3_bounc.nml) configuration",
    )
    ww3_prnc: Optional[list[Prnc]] = PydanticField(
        default=None,
        description="Field preprocessor component (ww3_prnc.nml) configuration",
    )
    ww3_track: Optional[Trnc] = PydanticField(
        default=None, description="Track component (ww3_trnc.nml) configuration"
    )
    ww3_ounf: Optional[Ounf] = PydanticField(
        default=None,
        description="Field output component (ww3_ounf.nml) configuration",
    )
    ww3_ounp: Optional[Ounp] = PydanticField(
        default=None, description="Point output component (ww3_ounp.nml) configuration"
    )
    ww3_upstr: Optional[Uptstr] = PydanticField(
        default=None,
        description="Restart update component (ww3_uprstr.nml) configuration",
    )
    namelists: Optional[Namelists] = PydanticField(
        default=None, description="Namelists component (namelists.nml) configuration"
    )

    def __call__(self, runtime) -> dict:
        """Callable where data and config are interfaced and CMD is rendered."""

        # Set default dates from the runtime period if available
        self._set_default_dates(runtime)

        # Generate WW3 control namelist files
        self.write_control_files(runtime)

        # Generate execution scripts based on what files and executables are needed
        self.generate_run_script(runtime.staging_dir)

    def _set_default_dates(self, runtime):
        """Set default start and end dates from the runtime period if not already set in components."""
        # Get the period from runtime if available
        period = getattr(runtime, "period", None)
        if not period:
            return  # No period to use for defaults

        # Iterate through all attributes of this config instance
        for attr_name in self.components:
            component = getattr(self, attr_name)
            if component is not None:
                self._set_component_dates_recursive(component, period)
            if isinstance(component, list):
                for sub_component in component:
                    self._set_component_dates_recursive(sub_component, period)

    def _set_component_dates_recursive(self, obj, period):
        """
        Recursively find and set date fields in a component and its nested objects.

        Args:
            obj: The object to process
            period: The time period to use for default dates
        """
        # If this is a namelist object, use its built-in date setting method
        if hasattr(obj, "set_default_dates"):
            obj.set_default_dates(period)
        # For non-namelist objects, process their fields recursively
        elif hasattr(obj, "__dict__") or hasattr(obj, "__pydantic_fields__"):
            if hasattr(obj, "model_fields"):
                # Process Pydantic model fields
                for field_name in obj.model_fields:
                    field_value = getattr(obj, field_name)
                    # Recursively process nested objects
                    if hasattr(field_value, "__dict__") or hasattr(
                        field_value, "__pydantic_fields__"
                    ):
                        if field_value is not None and not isinstance(
                            field_value, (str, int, float, bool, list, dict)
                        ):
                            self._set_component_dates_recursive(field_value, period)
                    # Also process lists of objects
                    elif isinstance(field_value, list):
                        for item in field_value:
                            if hasattr(item, "__dict__") or hasattr(
                                item, "__pydantic_fields__"
                            ):
                                if item is not None and not isinstance(
                                    item, (str, int, float, bool, dict)
                                ):
                                    self._set_component_dates_recursive(item, period)

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
    ww3_shel: Optional[Shel] = PydanticField(
        default=None, description="Shell component (ww3_shel.nml) configuration"
    )
    ww3_grid: Optional[Grid] = PydanticField(
        default=None, description="Grid component (ww3_grid.nml) configuration"
    )
    ww3_bound: Optional[Bound] = PydanticField(
        default=None, description="Boundary component (ww3_bound.nml) configuration"
    )
    boundary_update_component: Optional[Bounc] = PydanticField(
        default=None,
        description="Boundary update component (ww3_bounc.nml) configuration",
    )
    ww3_prnc: Optional[Prnc] = PydanticField(
        default=None,
        description="Field preprocessor component (ww3_prnc.nml) configuration",
    )
    ww3_track: Optional[Trnc] = PydanticField(
        default=None, description="Track component (ww3_trnc.nml) configuration"
    )
    ww3_ounf: Optional[Ounf] = PydanticField(
        default=None,
        description="Field output component (ww3_ounf.nml) configuration",
    )
    ww3_ounp: Optional[Ounp] = PydanticField(
        default=None, description="Point output component (ww3_ounp.nml) configuration"
    )
    ww3_upstr: Optional[Uptstr] = PydanticField(
        default=None,
        description="Restart update component (ww3_uprstr.nml) configuration",
    )
    namelists: Optional[Namelists] = PydanticField(
        default=None, description="Namelists component (namelists.nml) configuration"
    )

    def __call__(self, runtime) -> dict:
        """Callable where data and config are interfaced and CMD is rendered."""

        # Set default dates from the runtime period if available
        self._set_default_dates(runtime)
