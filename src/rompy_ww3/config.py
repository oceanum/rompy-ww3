"""WW3 Rompy config."""

import logging
import os
from pathlib import Path
from typing import Literal, Optional, List, Dict, Any
from pydantic import Field as PydanticField, model_validator

from rompy.core.config import BaseConfig

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

    @model_validator(mode="after")
    def sync_component_fields(self):
        """
        Synchronize field list between shell output_type and field output components.
        If ww3_shel.output_type.field.list is set but ww3_ounf.field.list is not set,
        then set ww3_ounf.field.list to the same value.
        Also synchronize forcing parameters: if ww3_prnc.forcing[n].field.winds='T',
        then ww3_shel.input_nml.forcing.winds should also be 'T' and so on for all forcing types.
        """
        # Check if ww3_shel and its output_type exist and have field.list set
        if (
            self.ww3_shel
            and self.ww3_shel.output_type
            and self.ww3_shel.output_type.field
        ):
            shel_field_list = self.ww3_shel.output_type.field.list
            # Check if ww3_ounf exists and its field.list is not set
            if (
                self.ww3_ounf
                and self.ww3_ounf.field
                and shel_field_list is not None
                and self.ww3_ounf.field.list is None
            ):
                # Set the field list from shel to ounf
                self.ww3_ounf.field.list = shel_field_list

        # Define mapping between forcing field boolean attributes and input forcing string attributes
        # Both share the same attribute names for the forcing types
        forcing_mapping = [
            "winds",
            "currents",
            "water_levels",
            "atm_momentum",
            "air_density",
            "ice_conc",
            "ice_param1",
            "ice_param2",
            "ice_param3",
            "ice_param4",
            "ice_param5",
            "mud_density",
            "mud_thickness",
            "mud_viscosity",
        ]

        # Synchronize forcing parameters between ww3_prnc and ww3_shel.input_nml
        # For each active forcing in ww3_prnc, set the corresponding input forcing flag to 'T'
        # Make it cumulative across multiple PRNC components
        if self.ww3_prnc and isinstance(self.ww3_prnc, list):
            # Process all PRNC components to collect all active forcing types
            active_forcings = {}

            for prnc_component in self.ww3_prnc:
                if (
                    prnc_component
                    and prnc_component.forcing
                    and prnc_component.forcing.field
                ):
                    # Check each forcing type in the mapping
                    for forcing_type in forcing_mapping:
                        forcing_attr = getattr(
                            prnc_component.forcing.field, forcing_type, None
                        )
                        if forcing_attr is True:  # If the forcing is active in prnc
                            active_forcings[forcing_type] = "T"

            # Apply all active forcings to the shel input
            if active_forcings:  # If we found any active forcings
                # Ensure ww3_shel exists
                if self.ww3_shel:
                    # Ensure input_nml exists
                    if not self.ww3_shel.input_nml:
                        from rompy_ww3.namelists.input import Input

                        self.ww3_shel.input_nml = Input()

                    # Ensure input_nml.forcing exists
                    if not self.ww3_shel.input_nml.forcing:
                        from rompy_ww3.namelists.input import InputForcing

                        self.ww3_shel.input_nml.forcing = InputForcing()

                    # Apply each active forcing if not already set
                    for forcing_type, value in active_forcings.items():
                        current_value = getattr(
                            self.ww3_shel.input_nml.forcing, forcing_type
                        )
                        if current_value is None:
                            setattr(
                                self.ww3_shel.input_nml.forcing, forcing_type, value
                            )
        return self

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

        # Convert interval to seconds if it exists
        interval_seconds = None
        if hasattr(period, "interval") and period.interval:
            interval_seconds = int(period.interval.total_seconds())

        # Special handling for shell component: if output_type is active but output_date is not set,
        # initialize output_date and its sub-components to ensure dates are set properly
        if self.ww3_shel and self.ww3_shel.output_type:
            from rompy_ww3.namelists.output_date import (
                OutputDate,
                OutputDateField,
                OutputDatePoint,
                OutputDateTrack,
                OutputDateRestart,
                OutputDatePartition,
                OutputDateCoupling,
            )

            # Check if any output type is active (not None) and initialize corresponding output_date components
            needs_output_date = (
                self.ww3_shel.output_type.field
                or self.ww3_shel.output_type.point
                or self.ww3_shel.output_type.track
                or self.ww3_shel.output_type.partition
                or self.ww3_shel.output_type.coupling
                or self.ww3_shel.output_type.restart
            )

            if needs_output_date:
                # If output_date is None, create an empty one
                if self.ww3_shel.output_date is None:
                    self.ww3_shel.output_date = OutputDate()

                # Initialize specific output_date components that correspond to active output_types
                if (
                    self.ww3_shel.output_type.field
                    and self.ww3_shel.output_date.field is None
                ):
                    self.ww3_shel.output_date.field = OutputDateField()
                if (
                    self.ww3_shel.output_type.point
                    and self.ww3_shel.output_date.point is None
                ):
                    self.ww3_shel.output_date.point = OutputDatePoint()
                if (
                    self.ww3_shel.output_type.track
                    and self.ww3_shel.output_date.track is None
                ):
                    self.ww3_shel.output_date.track = OutputDateTrack()
                if (
                    self.ww3_shel.output_type.restart
                    and self.ww3_shel.output_date.restart is None
                ):
                    self.ww3_shel.output_date.restart = OutputDateRestart()
                if (
                    self.ww3_shel.output_type.partition
                    and self.ww3_shel.output_date.partition is None
                ):
                    self.ww3_shel.output_date.partition = OutputDatePartition()
                if (
                    self.ww3_shel.output_type.coupling
                    and self.ww3_shel.output_date.coupling is None
                ):
                    self.ww3_shel.output_date.coupling = OutputDateCoupling()

        # Iterate through all attributes of this config instance
        for attr_name in self.components:
            component = getattr(self, attr_name)
            if component is not None:
                self._set_component_dates_recursive(component, period)
                # Also set stride if interval exists
                if interval_seconds is not None:
                    self._set_component_stride_recursive(component, interval_seconds)
            if isinstance(component, list):
                for sub_component in component:
                    self._set_component_dates_recursive(sub_component, period)
                    # Also set stride if interval exists
                    if interval_seconds is not None:
                        self._set_component_stride_recursive(
                            sub_component, interval_seconds
                        )

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

    def _set_component_stride_recursive(self, obj, interval_seconds):
        """
        Recursively find and set stride fields in a component and its nested objects.

        Args:
            obj: The object to process
            interval_seconds: The time interval in seconds to use for default stride
        """
        # If this is a namelist object with stride attribute, set it if not already set
        if hasattr(obj, "stride") and getattr(obj, "stride") is None:
            obj.stride = str(interval_seconds)
        # If this is a namelist object with timestride attribute, set it if not already set
        if hasattr(obj, "timestride") and getattr(obj, "timestride") is None:
            obj.timestride = str(interval_seconds)

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
                            self._set_component_stride_recursive(
                                field_value, interval_seconds
                            )
                    # Also process lists of objects
                    elif isinstance(field_value, list):
                        for item in field_value:
                            if hasattr(item, "__dict__") or hasattr(
                                item, "__pydantic_fields__"
                            ):
                                if item is not None and not isinstance(
                                    item, (str, int, float, bool, dict)
                                ):
                                    self._set_component_stride_recursive(
                                        item, interval_seconds
                                    )

    def render_namelists(self) -> Dict[str, str]:
        """Render all component namelists as a dictionary of strings.

        Returns:
            Dictionary containing rendered namelist content keyed by filename
        """
        namelists = {}

        # Render each component's namelist if it exists
        for component_name in self.components:
            component = getattr(self, component_name, None)
            if component is not None:
                # Handle both single components and lists of components
                if isinstance(component, list):
                    for idx, sub_component in enumerate(component):
                        if hasattr(sub_component, "render"):
                            key = f"{component_name}_{idx}.nml"
                            namelists[key] = sub_component.render()
                        elif hasattr(
                            sub_component, "get_template_context"
                        ):  # If it's a custom component
                            sub_context = sub_component.get_template_context()
                            if "namelists" in sub_context:
                                for sub_key, sub_content in sub_context[
                                    "namelists"
                                ].items():
                                    namelists[f"{component_name}_{idx}_{sub_key}"] = (
                                        sub_content
                                    )
                else:
                    if hasattr(component, "render"):
                        key = f"{component_name}.nml"
                        namelists[key] = component.render()
                    elif hasattr(
                        component, "get_template_context"
                    ):  # If it's a custom component
                        sub_context = component.get_template_context()
                        if "namelists" in sub_context:
                            for sub_key, sub_content in sub_context[
                                "namelists"
                            ].items():
                                namelists[f"{sub_key}"] = sub_content

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
