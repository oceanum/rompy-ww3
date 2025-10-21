"""Base model for WW3 components."""

from typing import Any, Union
from pathlib import Path
import logging
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class WW3ComponentBaseModel(BaseModel):
    """Base class for WW3 components with common rendering functionality."""

    def render(self) -> str:
        """Render namelist as a string."""

        content = []
        # Get the model data
        model_data = self.model_dump()
        for key, value in model_data.items():
            if value is None:
                continue
            nml = getattr(self, key)
            content.append(nml.render())
        return "\n".join(content)

    def write_nml(self, workdir: Union[Path, str]) -> None:
        """Write the rendered component to a namelist file.

        Args:
            workdir: Directory to write the namelist file to
        """
        workdir = Path(workdir)
        workdir.mkdir(parents=True, exist_ok=True)

        # Use lowercase class name for filename
        filename = f"{self.__class__.__name__.lower()}.nml"
        filepath = workdir / filename

        with open(filepath, "w") as f:
            f.write(self.render())

        logger.info(f"Wrote component to {filepath}")

    def model_dump(self, *args, **kwargs) -> dict:
        """Return the component as a dictionary.

        This is needed to maintain compatibility with NamelistBaseModel interface.
        """
        return super().model_dump(*args, **kwargs)

    def model_dump_json(self, *args, **kwargs) -> str:
        """Return the component as a JSON string.

        This is needed to maintain compatibility with NamelistBaseModel interface.
        """
        return super().model_dump_json(*args, **kwargs)

    def process_value(self, value: Any) -> Any:
        """Process value for namelist formatting (from NamelistBaseModel)."""
        if isinstance(value, bool):
            return self.boolean_to_string(value)
        elif isinstance(value, str):
            # Don't quote Fortran booleans
            if value in ["T", "F"]:
                return value
            return f"'{value}'"
        elif isinstance(value, list):
            return ", ".join([str(self.process_value(v)) for v in value])
        return value

    def boolean_to_string(self, value: bool) -> str:
        """Convert boolean to Fortran-style string."""
        return "T" if value else "F"

    def get_namelist_name(self) -> str:
        """Get the namelist name for this model.

        This method should be overridden by subclasses to provide the appropriate namelist name.
        """
        # Default implementation - should be overridden by subclasses
        class_name = self.__class__.__name__
        return f"{class_name.upper()}_NML"

    @property
    def component_name(self) -> str:
        """Get the component name for this model"""
        class_name = self.__class__.__name__
        return f"{class_name.upper()}_NML"
