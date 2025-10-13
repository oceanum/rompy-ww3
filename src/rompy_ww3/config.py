"""WW3 Rompy config."""

import logging
from pathlib import Path
from typing import Literal, Optional, List, Dict, Any
from rompy.core.config import BaseConfig
from .grid import Grid as GridModel
from .namelists import (
    Domain,
    Input,
    InputGrid,
    ModelGrid,
    OutputType,
    OutputDate,
    HomogCount,
    HomogInput,
    Spectrum,
    Run,
    Timesteps,
    Field,
    Rect,
    Bound,
    Forcing,
    Track,
    Point,
    Restart,
    Update,
    UnformattedOutput,
    PointOutput,
    RestartUpdate,
    ModelParameters,
    Depth,
    Mask,
    Obstacle,
    Slope,
    Sediment,
    InboundCount,
    InboundPointList,
    ExcludedCount,
    ExcludedPointList,
    ExcludedBodyList,
    OutboundCount,
    OutboundLineList,
    Curv,
    Unst,
    Smc,
)
from pydantic import Field as PydanticField


logger = logging.getLogger(__name__)

HERE = Path(__file__).parent


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

    # WW3-specific namelist components
    domain: Optional[Domain] = PydanticField(
        default=None, description="DOMAIN_NML namelist configuration"
    )
    input_nml: Optional[Input] = PydanticField(
        default=None, description="INPUT_NML namelist configuration"
    )
    input_grid: Optional[InputGrid] = PydanticField(
        default=None,
        description="INPUT_GRID_NML namelist configuration (for multi-grid)",
    )
    model_grid: Optional[ModelGrid] = PydanticField(
        default=None,
        description="MODEL_GRID_NML namelist configuration (for multi-grid)",
    )
    model_grids: Optional[List[ModelGrid]] = PydanticField(
        default=None,
        description="List of MODEL_GRID_NML namelist configurations (for multi-grid)",
    )
    output_type: Optional[OutputType] = PydanticField(
        default=None, description="OUTPUT_TYPE_NML namelist configuration"
    )
    output_date: Optional[OutputDate] = PydanticField(
        default=None, description="OUTPUT_DATE_NML namelist configuration"
    )
    homog_count: Optional[HomogCount] = PydanticField(
        default=None, description="HOMOG_COUNT_NML namelist configuration"
    )
    homog_input: Optional[List[HomogInput]] = PydanticField(
        default=None, description="HOMOG_INPUT_NML namelist configurations"
    )
    spectrum: Optional[Spectrum] = PydanticField(
        default_factory=Spectrum, description="SPECTRUM_NML namelist configuration"
    )
    run: Optional[Run] = PydanticField(
        default=None, description="RUN_NML namelist configuration"
    )
    timesteps: Optional[Timesteps] = PydanticField(
        ..., description="TIMESTEPS_NML namelist configuration"
    )
    grid: Optional[GridModel] = PydanticField(
        default=None, description="GRID_NML namelist configuration"
    )
    grids: Optional[List[GridModel]] = PydanticField(
        default=None,
        description="List of GRID_NML namelist configurations (for multi-grid)",
    )
    rect: Optional[Rect] = PydanticField(
        default=None, description="RECT_NML namelist configuration"
    )
    bound: Optional[Bound] = PydanticField(
        default=None, description="BOUND_NML namelist configuration"
    )
    forcing: Optional[Forcing] = PydanticField(
        default=None, description="FORCING_NML namelist configuration"
    )
    track: Optional[Track] = PydanticField(
        default=None, description="TRACK_NML namelist configuration"
    )
    field_nml: Optional[Field] = PydanticField(
        default=None, description="FIELD_NML namelist configuration"
    )
    point: Optional[Point] = PydanticField(
        default=None, description="POINT_NML namelist configuration"
    )
    restart: Optional[Restart] = PydanticField(
        default=None, description="RESTART_NML namelist configuration"
    )
    update: Optional[Update] = PydanticField(
        default=None, description="UPDATE_NML namelist configuration"
    )
    unformatted: Optional[UnformattedOutput] = PydanticField(
        default=None, description="OUNF_NML namelist configuration"
    )
    point_output: Optional[PointOutput] = PydanticField(
        default=None, description="OUNP_NML namelist configuration"
    )
    restart_update: Optional[RestartUpdate] = PydanticField(
        default=None, description="UPRSTR_NML namelist configuration"
    )
    parameters: Optional[ModelParameters] = PydanticField(
        default=None, description="PARAMS_NML namelist configuration"
    )
    depth: Optional[Depth] = PydanticField(
        default=None, description="DEPTH_NML namelist configuration"
    )
    mask: Optional[Mask] = PydanticField(
        default=None, description="MASK_NML namelist configuration"
    )
    obstacle: Optional[Obstacle] = PydanticField(
        default=None, description="OBST_NML namelist configuration"
    )
    slope: Optional[Slope] = PydanticField(
        default=None, description="SLOPE_NML namelist configuration"
    )
    sediment: Optional[Sediment] = PydanticField(
        default=None, description="SED_NML namelist configuration"
    )
    inbound_count: Optional[InboundCount] = PydanticField(
        default=None, description="INBND_COUNT_NML namelist configuration"
    )
    inbound_points: Optional[InboundPointList] = PydanticField(
        default=None, description="INBND_POINT_NML namelist configuration"
    )
    excluded_count: Optional[ExcludedCount] = PydanticField(
        default=None, description="EXCL_COUNT_NML namelist configuration"
    )
    excluded_points: Optional[ExcludedPointList] = PydanticField(
        default=None, description="EXCL_POINT_NML namelist configuration"
    )
    excluded_bodies: Optional[ExcludedBodyList] = PydanticField(
        default=None, description="EXCL_BODY_NML namelist configuration"
    )
    outbound_count: Optional[OutboundCount] = PydanticField(
        default=None, description="OUTBND_COUNT_NML namelist configuration"
    )
    outbound_lines: Optional[OutboundLineList] = PydanticField(
        default=None, description="OUTBND_LINE_NML namelist configuration"
    )
    curv: Optional[Curv] = PydanticField(
        default=None, description="CURV_NML namelist configuration"
    )
    unst: Optional[Unst] = PydanticField(
        default=None, description="UNST_NML namelist configuration"
    )
    smc: Optional[Smc] = PydanticField(
        default=None, description="SMC_NML namelist configuration"
    )

    def __call__(self, runtime) -> dict:
        """Callable where data and config are interfaced and CMD is rendered."""
        staging_dir = runtime.staging_dir

        # Generate WW3 control namelist files
        namelists_dir = Path(staging_dir) / "namelists"
        namelists_dir.mkdir(parents=True, exist_ok=True)

        # Generate main shell namelist file (for single-grid models)
        self.generate_shell_namelist(namelists_dir / "ww3_shel.nml")

        # Generate multi-grid namelist file (for multi-grid models)
        self.generate_multi_namelist(namelists_dir / "ww3_multi.nml")

        # Generate grid preprocessing namelist
        self.generate_grid_namelist(namelists_dir / "ww3_grid.nml")

        # Generate boundary preprocessing namelist
        self.generate_boundary_namelist(namelists_dir / "ww3_bound.nml")

        # Generate boundary update namelist
        self.generate_boundary_update_namelist(namelists_dir / "ww3_bounc.nml")

        # Generate print control namelist
        self.generate_print_control_namelist(namelists_dir / "ww3_prnc.nml")

        # Generate track output namelist
        self.generate_track_namelist(namelists_dir / "ww3_trnc.nml")

        # Generate unformatted output namelist
        self.generate_unformatted_output_namelist(namelists_dir / "ww3_ounf.nml")

        # Generate point output namelist
        self.generate_point_output_namelist(namelists_dir / "ww3_ounp.nml")

        # Generate restart update namelist
        self.generate_restart_update_namelist(namelists_dir / "ww3_uprstr.nml")

        # Generate model parameters namelist
        self.generate_parameters_namelist(namelists_dir / "namelists.nml")

        ret = {"staging_dir": staging_dir, "namelists_dir": str(namelists_dir)}
        return ret

    def _write_homog_input_nml(self, workdir: Path) -> None:
        """Write HOMOG_INPUT_NML with multiple inputs."""
        filepath = workdir / "homog_input.nml"

        with open(filepath, "w") as f:
            f.write("! Generated by rompy-ww3\n")
            f.write("&HOMOG_INPUT_NML\n")

            for i, homog_input in enumerate(self.homog_input, 1):
                if homog_input.name:
                    f.write(f"  HOMOG_INPUT({i})%NAME   = '{homog_input.name}'\n")
                if homog_input.date:
                    f.write(f"  HOMOG_INPUT({i})%DATE   = '{homog_input.date}'\n")
                if homog_input.value1 is not None:
                    f.write(f"  HOMOG_INPUT({i})%VALUE1 = {homog_input.value1}\n")
                if homog_input.value2 is not None:
                    f.write(f"  HOMOG_INPUT({i})%VALUE2 = {homog_input.value2}\n")
                if homog_input.value3 is not None:
                    f.write(f"  HOMOG_INPUT({i})%VALUE3 = {homog_input.value3}\n")
                f.write("\n")

            f.write("/\n")

    def render_namelists(self) -> Dict[str, str]:
        """Render all namelists as strings and return as a dictionary."""
        namelists = {}

        if self.domain:
            namelists["domain.nml"] = self.domain.render()

        if self.input_nml:
            namelists["input.nml"] = self.input_nml.render()

        if self.output_type:
            namelists["output_type.nml"] = self.output_type.render()

        if self.output_date:
            namelists["output_date.nml"] = self.output_date.render()

        if self.homog_count:
            namelists["homog_count.nml"] = self.homog_count.render()

        # For homog_input, we need to combine them into a single namelist
        if self.homog_input:
            homog_input_content = "! Generated by rompy-ww3\\n&HOMOG_INPUT_NML\\n"
            for i, homog_input in enumerate(self.homog_input, 1):
                if homog_input.name:
                    homog_input_content += (
                        f"  HOMOG_INPUT({i})%NAME   = '{homog_input.name}'\\n"
                    )
                if homog_input.date:
                    homog_input_content += (
                        f"  HOMOG_INPUT({i})%DATE   = '{homog_input.date}'\\n"
                    )
                if homog_input.value1 is not None:
                    homog_input_content += (
                        f"  HOMOG_INPUT({i})%VALUE1 = {homog_input.value1}\\n"
                    )
                if homog_input.value2 is not None:
                    homog_input_content += (
                        f"  HOMOG_INPUT({i})%VALUE2 = {homog_input.value2}\\n"
                    )
                if homog_input.value3 is not None:
                    homog_input_content += (
                        f"  HOMOG_INPUT({i})%VALUE3 = {homog_input.value3}\\n"
                    )
                homog_input_content += "\\n"
            homog_input_content += "/\\n"
            namelists["homog_input.nml"] = homog_input_content

        # Additional WW3 namelist configurations
        if self.spectrum:
            namelists["spectrum.nml"] = self.spectrum.render()

        if self.run:
            namelists["run.nml"] = self.run.render()

        if self.timesteps:
            namelists["timesteps.nml"] = self.timesteps.render()

        if self.grid:
            namelists["grid.nml"] = self.grid.generate_grid_nml()
            namelists["rect.nml"] = self.grid.generate_rect_nml()

        if self.rect:
            namelists["rect.nml"] = self.rect.render()

        if self.bound:
            namelists["bound.nml"] = self.bound.render()

        if self.forcing:
            namelists["forcing.nml"] = self.forcing.render()

        if self.track:
            namelists["track.nml"] = self.track.render()

        if self.field_nml:
            namelists["field.nml"] = self.field_nml.render()

        if self.point:
            namelists["point.nml"] = self.point.render()

        if self.restart:
            namelists["restart.nml"] = self.restart.render()

        if self.update:
            namelists["update.nml"] = self.update.render()

        if self.unformatted:
            namelists["unformatted.nml"] = self.unformatted.render()

        if self.point_output:
            namelists["point_output.nml"] = self.point_output.render()

        if self.restart_update:
            namelists["restart_update.nml"] = self.restart_update.render()

        if self.parameters:
            namelists["parameters.nml"] = self.parameters.render()

        # Additional grid preprocessing namelist configurations
        if self.depth:
            namelists["depth.nml"] = self.depth.render()

        if self.mask:
            namelists["mask.nml"] = self.mask.render()

        if self.obstacle:
            namelists["obstacle.nml"] = self.obstacle.render()

        if self.slope:
            namelists["slope.nml"] = self.slope.render()

        if self.sediment:
            namelists["sediment.nml"] = self.sediment.render()

        if self.inbound_count:
            namelists["inbound_count.nml"] = self.inbound_count.render()

        if self.inbound_points:
            namelists["inbound_points.nml"] = self.inbound_points.render()

        if self.excluded_count:
            namelists["excluded_count.nml"] = self.excluded_count.render()

        if self.excluded_points:
            namelists["excluded_points.nml"] = self.excluded_points.render()

        if self.excluded_bodies:
            namelists["excluded_bodies.nml"] = self.excluded_bodies.render()

        if self.outbound_count:
            namelists["outbound_count.nml"] = self.outbound_count.render()

        if self.outbound_lines:
            namelists["outbound_lines.nml"] = self.outbound_lines.render()

        # Additional grid type namelist configurations
        if self.curv:
            namelists["curv.nml"] = self.curv.render()

        if self.unst:
            namelists["unst.nml"] = self.unst.render()

        if self.smc:
            namelists["smc.nml"] = self.smc.render()

        return namelists

    def get_template_context(self) -> Dict[str, Any]:
        """Generate template context for Jinja2 templates.

        Returns:
            Dictionary containing context variables for templates
        """
        context = {
            "config": self,
            "domain": self.domain,
            "input_nml": self.input_nml,
            "output_type": self.output_type,
            "output_date": self.output_date,
            "homog_count": self.homog_count,
            "homog_input": self.homog_input,
            "spectrum": self.spectrum,
            "run": self.run,
            "timesteps": self.timesteps,
            "grid": self.grid,
            "rect": self.rect,
            "bound": self.bound,
            "forcing": self.forcing,
            "track": self.track,
            "field_nml": self.field_nml,
            "point": self.point,
            "restart": self.restart,
            "update": self.update,
            "unformatted": self.unformatted,
            "point_output": self.point_output,
            "restart_update": self.restart_update,
            "parameters": self.parameters,
        }

        # Add rendered namelists to context
        context["namelists"] = self.render_namelists()

        # Add convenience variables
        if self.domain:
            context["start_time"] = self.domain.start
            context["stop_time"] = self.domain.stop
            context["iostyp"] = self.domain.iostyp

        # Add input forcing information
        if self.input_nml and self.input_nml.forcing:
            context["forcing"] = self.input_nml.forcing.model_dump()

        # Add output information
        if self.output_type:
            if self.output_type.field and self.output_type.field.list:
                context["output_fields"] = self.output_type.field.list.split()

        return context

    def generate_run_script(self, workdir: Path) -> Path:
        """Generate a basic WW3 run script.

        Args:
            workdir: Directory where to write the script

        Returns:
            Path to the generated script
        """
        workdir.mkdir(parents=True, exist_ok=True)

        script_path = workdir / "run_ww3.sh"

        with open(script_path, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("# WW3 run script generated by rompy-ww3\n\n")
            f.write("set -e\n\n")
            f.write("# Set up environment\n")
            f.write("export WW3_DIR=/path/to/ww3\n")
            f.write("export PATH=$WW3_DIR/bin:$PATH\n\n")
            f.write("# Run WW3 components\n")
            f.write('echo "Running WW3 grid preprocessor..."\\n')
            f.write("$WW3_DIR/bin/ww3_grid || exit 1\n\n")
            f.write('echo "Running WW3 model..."\\n')
            f.write("$WW3_DIR/bin/ww3_shel || exit 1\n\n")
            f.write('echo "WW3 run completed successfully!"\\n')

        # Make script executable
        import stat

        script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)

        logger.info(f"Generated run script: {script_path}")
        return script_path

    def generate_grid_namelist(self, output_path: Path) -> None:
        """Generate the complete ww3_grid.nml file for grid preprocessing.

        Args:
            output_path: Path where the grid namelist file should be written
        """
        grid_content = []
        grid_content.append("! WW3 grid preprocessing configuration")
        grid_content.append("! Generated by rompy-ww3")
        grid_content.append("")

        # Add SPECTRUM_NML
        if self.spectrum:
            rendered = self.spectrum.render().replace("\\n", "\n")
            grid_content.extend(rendered.split("\n"))
            grid_content.append("")

        # Add RUN_NML
        if self.run:
            rendered = self.run.render().replace("\\n", "\n")
            grid_content.extend(rendered.split("\n"))
            grid_content.append("")

        # Add GRID_NML
        if self.grid:
            grid_content.append(self.grid.generate_grid_nml())
            grid_content.append("")

        # Add RECT_NML
        if self.grid and self.grid.grid_type == "RECT":
            grid_content.append(self.grid.generate_rect_nml())
            grid_content.append("")

        # Add TIMESTEPS_NML
        if self.timesteps:
            rendered = self.timesteps.render().replace("\\n", "\n")
            grid_content.extend(rendered.split("\n"))
            grid_content.append("")

        # Add optional depth-related namelists
        if self.depth:
            rendered = self.depth.render().replace("\\n", "\n")
            grid_content.extend(rendered.split("\n"))
            grid_content.append("")

        if self.mask:
            rendered = self.mask.render().replace("\\n", "\n")
            grid_content.extend(rendered.split("\n"))
            grid_content.append("")

        if self.obstacle:
            rendered = self.obstacle.render().replace("\\n", "\n")
            grid_content.extend(rendered.split("\n"))
            grid_content.append("")

        if self.slope:
            rendered = self.slope.render().replace("\\n", "\n")
            grid_content.extend(rendered.split("\n"))
            grid_content.append("")

        if self.sediment:
            rendered = self.sediment.render().replace("\\n", "\n")
            grid_content.extend(rendered.split("\n"))
            grid_content.append("")

        # Add inbound boundary point namelists
        if self.inbound_count:
            rendered = self.inbound_count.render().replace("\\n", "\n")
            grid_content.extend(rendered.split("\n"))
            grid_content.append("")

        if self.inbound_points:
            rendered = self.inbound_points.render().replace("\\n", "\n")
            grid_content.extend(rendered.split("\n"))
            grid_content.append("")

        # Add excluded point and body namelists
        if self.excluded_count:
            rendered = self.excluded_count.render().replace("\\n", "\n")
            grid_content.extend(rendered.split("\n"))
            grid_content.append("")

        if self.excluded_points:
            rendered = self.excluded_points.render().replace("\\n", "\n")
            grid_content.extend(rendered.split("\n"))
            grid_content.append("")

        if self.excluded_bodies:
            rendered = self.excluded_bodies.render().replace("\\n", "\n")
            grid_content.extend(rendered.split("\n"))
            grid_content.append("")

        # Add outbound boundary line namelists
        if self.outbound_count:
            rendered = self.outbound_count.render().replace("\\n", "\n")
            grid_content.extend(rendered.split("\n"))
            grid_content.append("")

        if self.outbound_lines:
            rendered = self.outbound_lines.render().replace("\\n", "\n")
            grid_content.extend(rendered.split("\n"))
            grid_content.append("")

        # Add grid type specific namelists based on grid type
        if self.grid:
            if self.grid.grid_type == "CURV" and self.curv:
                rendered = self.curv.render().replace("\\n", "\n")
                grid_content.extend(rendered.split("\n"))
                grid_content.append("")
            elif self.grid.grid_type == "UNST" and self.unst:
                rendered = self.unst.render().replace("\\n", "\n")
                grid_content.extend(rendered.split("\n"))
                grid_content.append("")
            elif self.grid.grid_type == "SMC" and self.smc:
                rendered = self.smc.render().replace("\\n", "\n")
                grid_content.extend(rendered.split("\n"))
                grid_content.append("")

        with open(output_path, "w") as f:
            f.write("\n".join(grid_content))

    def generate_boundary_namelist(self, output_path: Path) -> None:
        """Generate the complete ww3_bound.nml file for boundary preprocessing.

        Args:
            output_path: Path where the boundary namelist file should be written
        """
        bound_content = []
        bound_content.append("! WW3 boundary preprocessing configuration")
        bound_content.append("! Generated by rompy-ww3")
        bound_content.append("")

        # Add BOUND_NML if defined
        if self.bound:
            rendered = self.bound.render().replace("\\n", "\n")
            bound_content.extend(rendered.split("\n"))
            bound_content.append("")
        else:
            # Default boundary configuration
            bound_content.append("&BOUND_NML")
            bound_content.append("  BOUND%MODE   = 'READ'")
            bound_content.append("  BOUND%FILE   = 'bound_spec.nc'")
            bound_content.append("  BOUND%INTERP =  2")
            bound_content.append("/")

        with open(output_path, "w") as f:
            f.write("\n".join(bound_content))

    def generate_shell_namelist(self, output_path: Path) -> None:
        """Generate the complete ww3_shel.nml file for the main model run.

        Args:
            output_path: Path where the shell namelist file should be written
        """
        shel_content = []

        # Add DOMAIN_NML
        if self.domain:
            rendered = self.domain.render().replace("\\n", "\n")
            shel_content.extend(rendered.split("\n"))
            shel_content.append("")

        # Add INPUT_NML
        if self.input_nml:
            rendered = self.input_nml.render().replace("\\n", "\n")
            shel_content.extend(rendered.split("\n"))
            shel_content.append("")

        # Add OUTPUT_TYPE_NML
        if self.output_type:
            rendered = self.output_type.render().replace("\\n", "\n")
            shel_content.extend(rendered.split("\n"))
            shel_content.append("")

        # Add OUTPUT_DATE_NML
        if self.output_date:
            rendered = self.output_date.render().replace("\\n", "\n")
            shel_content.extend(rendered.split("\n"))
            shel_content.append("")

        # Add HOMOG_COUNT_NML
        if self.homog_count:
            rendered = self.homog_count.render().replace("\\n", "\n")
            shel_content.extend(rendered.split("\n"))
            shel_content.append("")

        # Add HOMOG_INPUT_NML
        if self.homog_input:
            homog_input_content = "! Generated by rompy-ww3\n&HOMOG_INPUT_NML\n"
            for i, homog_input in enumerate(self.homog_input, 1):
                if homog_input.name:
                    homog_input_content += (
                        f"  HOMOG_INPUT({i})%NAME   = '{homog_input.name}'\n"
                    )
                if homog_input.date:
                    homog_input_content += (
                        f"  HOMOG_INPUT({i})%DATE   = '{homog_input.date}'\n"
                    )
                if homog_input.value1 is not None:
                    homog_input_content += (
                        f"  HOMOG_INPUT({i})%VALUE1 = {homog_input.value1}\n"
                    )
                if homog_input.value2 is not None:
                    homog_input_content += (
                        f"  HOMOG_INPUT({i})%VALUE2 = {homog_input.value2}\n"
                    )
                if homog_input.value3 is not None:
                    homog_input_content += (
                        f"  HOMOG_INPUT({i})%VALUE3 = {homog_input.value3}\n"
                    )
                homog_input_content += "\n"
            homog_input_content += "/\n"
            shel_content.extend(homog_input_content.split("\n"))
            shel_content.append("")

        with open(output_path, "w") as f:
            f.write("\n".join(shel_content))

    def generate_multi_namelist(self, output_path: Path) -> None:
        """Generate the complete ww3_multi.nml file for multi-grid models.

        Args:
            output_path: Path where the multi-grid namelist file should be written
        """
        multi_content = []
        multi_content.append("! WW3 multi-grid model configuration")
        multi_content.append("! Generated by rompy-ww3")
        multi_content.append("")

        # Add DOMAIN_NML (for multi-grid specific parameters)
        if self.domain:
            rendered = self.domain.render().replace("\\n", "\n")
            multi_content.extend(rendered.split("\n"))
            multi_content.append("")

        # Add INPUT_GRID_NML if defined
        if self.input_grid:
            rendered = self.input_grid.render().replace("\\n", "\n")
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
                rendered = model_grid.render().replace("\\n", "\n")
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
                        # Need to update the fields to use the proper indexed format
                        updated_line = line.replace("MODEL%", f"MODEL({i + 1})%")
                        updated_lines.append(updated_line)
                multi_content.extend(updated_lines)
                multi_content.append("")
        elif self.model_grid:  # Single model grid
            rendered = self.model_grid.render().replace("\\n", "\n")
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
                    updated_line = line.replace("MODEL%", "MODEL(1)%")
                    updated_lines.append(updated_line)
            multi_content.extend(updated_lines)
            multi_content.append("")

        # Add OUTPUT_TYPE_NML
        if self.output_type:
            rendered = self.output_type.render().replace("\\n", "\n")
            multi_content.extend(rendered.split("\n"))
            multi_content.append("")

        # Add OUTPUT_DATE_NML
        if self.output_date:
            rendered = self.output_date.render().replace("\\n", "\n")
            multi_content.extend(rendered.split("\n"))
            multi_content.append("")

        # Add HOMOG_COUNT_NML if needed for multi-grid
        if self.homog_count:
            rendered = self.homog_count.render().replace("\\n", "\n")
            multi_content.extend(rendered.split("\n"))
            multi_content.append("")

        with open(output_path, "w") as f:
            f.write("\n".join(multi_content))

    def generate_boundary_update_namelist(self, output_path: Path) -> None:
        """Generate the complete ww3_bounc.nml file for boundary updates.

        Args:
            output_path: Path where the boundary update namelist file should be written
        """
        bounc_content = []
        bounc_content.append("! WW3 boundary update configuration")
        bounc_content.append("! Generated by rompy-ww3")
        bounc_content.append("")

        # Add BOUND_UPDATE_NML if defined
        # Using update namelist which should handle boundary updates
        if self.update:
            rendered = self.update.render().replace("\\n", "\n")
            bounc_content.extend(rendered.split("\n"))
            bounc_content.append("")
        else:
            # Default boundary update configuration
            bounc_content.append("&BOUN_UPDATE_NML")
            bounc_content.append("  BOUN_UPDATE%UPDATE_TYPE  = 'FLUX'")
            bounc_content.append("  BOUN_UPDATE%INTERP_TYPE = 'LINEAR'")
            bounc_content.append("/")
            bounc_content.append("")

        with open(output_path, "w") as f:
            f.write("\n".join(bounc_content))

    def generate_print_control_namelist(self, output_path: Path) -> None:
        """Generate the complete ww3_prnc.nml file for print control.

        Args:
            output_path: Path where the print control namelist file should be written
        """
        prnc_content = []
        prnc_content.append("! WW3 print control configuration")
        prnc_content.append("! Generated by rompy-ww3")
        prnc_content.append("")

        # Add PRINT CONTROL NML if defined
        # Using parameters namelist which might contain print control options
        if self.parameters:
            rendered = self.parameters.render().replace("\\n", "\n")
            prnc_content.extend(rendered.split("\n"))
            prnc_content.append("")
        else:
            # Default print control configuration
            prnc_content.append("&PRINT_NML")
            prnc_content.append("  PRINT%CFLAG = 'T'  ! Enable console output")
            prnc_content.append("  PRINT%FFLAG = 'T'  ! Enable file output")
            prnc_content.append("  PRINT%LFLAG = 'T'  ! Enable log file output")
            prnc_content.append("/")
            prnc_content.append("")

        with open(output_path, "w") as f:
            f.write("\n".join(prnc_content))

    def generate_track_namelist(self, output_path: Path) -> None:
        """Generate the complete ww3_trnc.nml file for track output.

        Args:
            output_path: Path where the track output namelist file should be written
        """
        trnc_content = []
        trnc_content.append("! WW3 track output configuration")
        trnc_content.append("! Generated by rompy-ww3")
        trnc_content.append("")

        # Add TRACK_NML if defined
        if self.track:
            rendered = self.track.render().replace("\\n", "\n")
            trnc_content.extend(rendered.split("\n"))
            trnc_content.append("")
        else:
            # Default track output configuration
            trnc_content.append("&TRACK_NML")
            trnc_content.append("  TRACK%ACTIVE = 'T'  ! Enable track output")
            trnc_content.append("  TRACK%FORMAT = 1    ! Track format")
            trnc_content.append("/")
            trnc_content.append("")

        with open(output_path, "w") as f:
            f.write("\n".join(trnc_content))

    def generate_unformatted_output_namelist(self, output_path: Path) -> None:
        """Generate the complete ww3_ounf.nml file for unformatted output.

        Args:
            output_path: Path where the unformatted output namelist file should be written
        """
        ounf_content = []
        ounf_content.append("! WW3 unformatted output configuration")
        ounf_content.append("! Generated by rompy-ww3")
        ounf_content.append("")

        # Add UNFORMATTED OUTPUT NML if defined
        if self.unformatted:
            rendered = self.unformatted.render().replace("\\n", "\n")
            ounf_content.extend(rendered.split("\n"))
            ounf_content.append("")
        else:
            # Default unformatted output configuration
            ounf_content.append("&OUNF_NML")
            ounf_content.append("  OUNF%HSIGN = 'T'")
            ounf_content.append("  OUNF%TMM10 = 'T'")
            ounf_content.append("  OUNF%TM02 = 'T'")
            ounf_content.append("  OUNF%PDIR = 'T'")
            ounf_content.append("  OUNF%PENT = 'T'")
            ounf_content.append("/")
            ounf_content.append("")

        with open(output_path, "w") as f:
            f.write("\n".join(ounf_content))

    def generate_point_output_namelist(self, output_path: Path) -> None:
        """Generate the complete ww3_ounp.nml file for point output.

        Args:
            output_path: Path where the point output namelist file should be written
        """
        ounp_content = []
        ounp_content.append("! WW3 point output configuration")
        ounp_content.append("! Generated by rompy-ww3")
        ounp_content.append("")

        # Add POINT OUTPUT NML if defined
        if self.point_output:
            rendered = self.point_output.render().replace("\\n", "\n")
            ounp_content.extend(rendered.split("\n"))
            ounp_content.append("")
        else:
            # Default point output configuration
            ounp_content.append("&OUNP_NML")
            ounp_content.append("  OUNP%ACTIVE = 'T'  ! Enable point output")
            ounp_content.append("  OUNP%NSETS = 1     ! Number of point sets")
            ounp_content.append("/")
            ounp_content.append("")

        with open(output_path, "w") as f:
            f.write("\n".join(ounp_content))

    def generate_restart_update_namelist(self, output_path: Path) -> None:
        """Generate the complete ww3_uprstr.nml file for restart update.

        Args:
            output_path: Path where the restart update namelist file should be written
        """
        uprstr_content = []
        uprstr_content.append("! WW3 restart update configuration")
        uprstr_content.append("! Generated by rompy-ww3")
        uprstr_content.append("")

        # Add RESTART UPDATE NML if defined
        if self.restart_update:
            rendered = self.restart_update.render().replace("\\n", "\n")
            uprstr_content.extend(rendered.split("\n"))
            uprstr_content.append("")
        else:
            # Default restart update configuration
            uprstr_content.append("&UPRSTR_NML")
            uprstr_content.append("  UPRSTR%UPDATE_RESTART = 'T'")
            uprstr_content.append("/")
            uprstr_content.append("")

        with open(output_path, "w") as f:
            f.write("\n".join(uprstr_content))

    def generate_parameters_namelist(self, output_path: Path) -> None:
        """Generate the complete namelists.nml file for model parameters.

        Args:
            output_path: Path where the model parameters namelist file should be written
        """
        params_content = []
        params_content.append("! WW3 model parameters configuration")
        params_content.append("! Generated by rompy-ww3")
        params_content.append("")

        # Add MODEL PARAMETERS NML if defined
        if self.parameters:
            rendered = self.parameters.render().replace("\\n", "\n")
            params_content.extend(rendered.split("\n"))
            params_content.append("")
        else:
            # Default model parameters configuration
            params_content.append("&PARAMS_NML")
            params_content.append("  PARAMS%VISCOSITY = 1.0E-04")
            params_content.append("  PARAMS%DENST_REF = 1025.0")
            params_content.append("  PARAMS%LAPLACIAN = 'T'")
            params_content.append("/")
            params_content.append("")

        with open(output_path, "w") as f:
            f.write("\n".join(params_content))
