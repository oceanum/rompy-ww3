"""WW3 Rompy config."""

import logging
from pathlib import Path
from typing import Literal, Optional, List, Dict, Any
from pydantic import Field

from rompy.core.config import BaseConfig
from .grid import Grid
from .namelists import (
    Domain, Input, OutputType, OutputDate, HomogCount, HomogInput,
    Spectrum, Run, Timesteps, Rect, Bound, Forcing, Track,
    Field as FieldNML, Point, Restart, Update, UnformattedOutput, PointOutput,
    RestartUpdate, ModelParameters
)


logger = logging.getLogger(__name__)

HERE = Path(__file__).parent


class Config(BaseConfig):
    """Ww3 config class."""

    model_type: Literal["ww3"] = Field(
        default="ww3",
        description="Model type discriminator",
    )
    template: str = Field(
        default=str(HERE / "templates" / "base"),
        description="The model config template directory",
    )
    
    @property
    def main_template(self) -> str:
        """Return the path to the main template file."""
        return str(HERE / "templates" / "base" / "ww3_shel.nml")
    
    # WW3-specific namelist components
    domain: Optional[Domain] = Field(
        default=None,
        description="DOMAIN_NML namelist configuration"
    )
    input_nml: Optional[Input] = Field(
        default=None,
        description="INPUT_NML namelist configuration"
    )
    output_type: Optional[OutputType] = Field(
        default=None,
        description="OUTPUT_TYPE_NML namelist configuration"
    )
    output_date: Optional[OutputDate] = Field(
        default=None,
        description="OUTPUT_DATE_NML namelist configuration"
    )
    homog_count: Optional[HomogCount] = Field(
        default=None,
        description="HOMOG_COUNT_NML namelist configuration"
    )
    homog_input: Optional[List[HomogInput]] = Field(
        default=None,
        description="HOMOG_INPUT_NML namelist configurations"
    )
    spectrum: Optional[Spectrum] = Field(
        default=None,
        description="SPECTRUM_NML namelist configuration"
    )
    run: Optional[Run] = Field(
        default=None,
        description="RUN_NML namelist configuration"
    )
    timesteps: Optional[Timesteps] = Field(
        default=None,
        description="TIMESTEPS_NML namelist configuration"
    )
    grid: Optional[Grid] = Field(
        default=None,
        description="GRID_NML namelist configuration"
    )
    rect: Optional[Rect] = Field(
        default=None,
        description="RECT_NML namelist configuration"
    )
    bound: Optional[Bound] = Field(
        default=None,
        description="BOUND_NML namelist configuration"
    )
    forcing: Optional[Forcing] = Field(
        default=None,
        description="FORCING_NML namelist configuration"
    )
    track: Optional[Track] = Field(
        default=None,
        description="TRACK_NML namelist configuration"
    )
    field_nml: Optional[FieldNML] = Field(
        default=None,
        description="FIELD_NML namelist configuration"
    )
    point: Optional[Point] = Field(
        default=None,
        description="POINT_NML namelist configuration"
    )
    restart: Optional[Restart] = Field(
        default=None,
        description="RESTART_NML namelist configuration"
    )
    update: Optional[Update] = Field(
        default=None,
        description="UPDATE_NML namelist configuration"
    )
    unformatted: Optional[UnformattedOutput] = Field(
        default=None,
        description="OUNF_NML namelist configuration"
    )
    point_output: Optional[PointOutput] = Field(
        default=None,
        description="OUNP_NML namelist configuration"
    )
    restart_update: Optional[RestartUpdate] = Field(
        default=None,
        description="UPRSTR_NML namelist configuration"
    )
    parameters: Optional[ModelParameters] = Field(
        default=None,
        description="PARAMS_NML namelist configuration"
    )

    def __call__(self, runtime) -> dict:
        """Callable where data and config are interfaced and CMD is rendered."""
        staging_dir = runtime.staging_dir
        
        # Generate namelist files
        namelists_dir = Path(staging_dir) / "namelists"
        namelists_dir.mkdir(parents=True, exist_ok=True)
        
        # Render individual namelist files
        if self.domain:
            self.domain.write_nml(namelists_dir)
            
        if self.input_nml:
            self.input_nml.write_nml(namelists_dir)
            
        if self.output_type:
            self.output_type.write_nml(namelists_dir)
            
        if self.output_date:
            self.output_date.write_nml(namelists_dir)
            
        if self.homog_count:
            self.homog_count.write_nml(namelists_dir)
            
        # Handle multiple homogeneous inputs
        if self.homog_input:
            self._write_homog_input_nml(namelists_dir)
            
        # Additional WW3 namelist configurations
        if self.spectrum:
            self.spectrum.write_nml(namelists_dir)
            
        if self.run:
            self.run.write_nml(namelists_dir)
            
        if self.timesteps:
            self.timesteps.write_nml(namelists_dir)
            
        if self.grid:
            self.grid.write_grid_files(namelists_dir)
            
        if self.rect:
            self.rect.write_nml(namelists_dir)
            
        if self.bound:
            self.bound.write_nml(namelists_dir)
            
        if self.forcing:
            self.forcing.write_nml(namelists_dir)
            
        if self.track:
            self.track.write_nml(namelists_dir)
            
        if self.field_nml:
            self.field_nml.write_nml(namelists_dir)
            
        if self.point:
            self.point.write_nml(namelists_dir)
            
        if self.restart:
            self.restart.write_nml(namelists_dir)
            
        if self.update:
            self.update.write_nml(namelists_dir)
            
        if self.unformatted:
            self.unformatted.write_nml(namelists_dir)
            
        if self.point_output:
            self.point_output.write_nml(namelists_dir)
            
        if self.restart_update:
            self.restart_update.write_nml(namelists_dir)
            
        if self.parameters:
            self.parameters.write_nml(namelists_dir)
        
        ret = {
            "staging_dir": staging_dir,
            "namelists_dir": str(namelists_dir)
        }
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
                    homog_input_content += f"  HOMOG_INPUT({i})%NAME   = '{homog_input.name}'\\n"
                if homog_input.date:
                    homog_input_content += f"  HOMOG_INPUT({i})%DATE   = '{homog_input.date}'\\n"
                if homog_input.value1 is not None:
                    homog_input_content += f"  HOMOG_INPUT({i})%VALUE1 = {homog_input.value1}\\n"
                if homog_input.value2 is not None:
                    homog_input_content += f"  HOMOG_INPUT({i})%VALUE2 = {homog_input.value2}\\n"
                if homog_input.value3 is not None:
                    homog_input_content += f"  HOMOG_INPUT({i})%VALUE3 = {homog_input.value3}\\n"
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
            "field": self.field_nml,
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
            f.write("echo \"Running WW3 grid preprocessor...\"\\n")
            f.write("$WW3_DIR/bin/ww3_grid || exit 1\n\n")
            f.write("echo \"Running WW3 model...\"\\n")
            f.write("$WW3_DIR/bin/ww3_shel || exit 1\n\n")
            f.write("echo \"WW3 run completed successfully!\"\\n")
            
        # Make script executable
        import stat
        script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
        
        logger.info(f"Generated run script: {script_path}")
        return script_path
