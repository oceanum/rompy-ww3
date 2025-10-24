"""Base model for WW3 namelists."""

import logging
import re
from pathlib import Path
from typing import Any, Dict, Union
from pydantic import BaseModel, model_serializer, model_validator
from rompy.model import RompyBaseModel

logger = logging.getLogger(__name__)


def boolean_to_string(value: bool) -> str:
    """Convert boolean to Fortran-style string."""
    return "T" if value else "F"


def camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case."""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\\1_\\2", name)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\\1_\\2", s1)
    return s2.upper()


class NamelistBaseModel(BaseModel):
    """Base model for WW3 namelists with render capabilities."""

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """Serialize model excluding None and private fields."""
        serialized = {}
        for field_name, field_info in self.__class__.model_fields.items():
            value = getattr(self, field_name)
            if value is not None and not field_name.startswith("_"):
                serialized[field_name] = value
        return serialized

    @model_validator(mode="before")
    @classmethod
    def __lowercase_property_keys__(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Convert all dictionary keys to lowercase."""
        if isinstance(values, dict):
            return {k.lower(): v for k, v in values.items()}
        return values

    def process_value(self, value: Any) -> Any:
        """Process value for namelist formatting."""
        if isinstance(value, bool):
            return boolean_to_string(value)
        elif isinstance(value, str):
            # Don't quote Fortran booleans
            # if value in ["T", "F"]:
            #     return value
            return f"'{value}'"
        elif isinstance(value, list):
            return ", ".join([str(self.process_value(v)) for v in value])
        return value

    def get_namelist_name(self) -> str:
        """Get the namelist name for this model.

        This method can be overridden by subclasses to provide custom namelist names.
        """
        class_name = self.__class__.__name__
        # Special handling for specific classes to match WW3 namelist names
        namelist_mapping = {
            "Domain": "DOMAIN_NML",
            "Input": "INPUT_NML",
            "OutputType": "OUTPUT_TYPE_NML",
            "OutputDate": "OUTPUT_DATE_NML",
            "HomogCount": "HOMOG_COUNT_NML",
            "HomogInput": "HOMOG_INPUT_NML",
            "Spectrum": "SPECTRUM_NML",
            "Run": "RUN_NML",
            "Timesteps": "TIMESTEPS_NML",
            "Grid": "GRID_NML",
            "Rect": "RECT_NML",
            "Bound": "BOUND_NML",
            "Forcing": "FORCING_NML",
            "Track": "TRACK_NML",
            "Field": "FIELD_NML",
            "Point": "POINT_NML",
            "Restart": "RESTART_NML",
            "Update": "UPDATE_NML",
            "Depth": "DEPTH_NML",
            "Mask": "MASK_NML",
            "Obstacle": "OBST_NML",
            "Slope": "SLOPE_NML",
            "Sediment": "SED_NML",
            "InboundCount": "INBND_COUNT_NML",
            "InboundPointList": "INBND_POINT_NML",
            "ExcludedCount": "EXCL_COUNT_NML",
            "ExcludedPointList": "EXCL_POINT_NML",
            "ExcludedBodyList": "EXCL_BODY_NML",
            "OutboundCount": "OUTBND_COUNT_NML",
            "OutboundLineList": "OUTBND_LINE_NML",
            "Curv": "CURV_NML",
            "Unst": "UNST_NML",
            "Smc": "SMC_NML",
        }

        if class_name in namelist_mapping:
            return namelist_mapping[class_name]
        else:
            # Convert CamelCase to SNAKE_CASE and add _NML suffix
            snake_name = camel_to_snake(class_name)
            if snake_name.endswith("_NML"):
                return snake_name
            else:
                return f"{snake_name}_NML"

    def render(self, *args, **kwargs) -> str:
        """Render namelist as a string."""
        lines = []

        # Get the model data
        model_data = self.model_dump()

        # Get the namelist name
        namelist_name = self.get_namelist_name()
        lines.append(f"&{namelist_name}")

        # Get the namelist prefix (without _NML)
        namelist_prefix = (
            namelist_name[:-4] if namelist_name.endswith("_NML") else namelist_name
        )

        # Remove OUTPUT_ prefix. Special case in WW3 for some reason
        if namelist_prefix.startswith("OUTPUT_"):
            namelist_prefix = namelist_prefix[7:]

        # Process each field
        comma_fields = getattr(self, "_comma_fields", [])

        for key, value in model_data.items():
            nml = getattr(self, key)
            if isinstance(nml, RompyBaseModel) and value is not None:
                value = nml.get(*args, **kwargs)
                # Get the rendered output of the nested object
            # Handle nested objects that are dictionaries
            if isinstance(value, dict):
                # Handle nested objects like forcing, field, etc.
                for sub_key, sub_value in value.items():
                    if sub_value is not None:
                        sub_nml = getattr(nml, sub_key)
                        if (
                            isinstance(sub_nml, RompyBaseModel)
                            and sub_value is not None
                        ):
                            sub_value = sub_nml.get(*args, **kwargs)
                        # Format the key as NAMELIST%PARENT%CHILD for nested objects
                        formatted_key = (
                            f"{namelist_prefix}%{key.upper()}%{sub_key.upper()}"
                        )
                        processed_value = self.process_value(sub_value)

                        # Add trailing comma if needed
                        if sub_key in comma_fields:
                            line = f"  {formatted_key} = {processed_value},"
                        else:
                            line = f"  {formatted_key} = {processed_value}"

                        lines.append(line)
            else:
                # Handle simple fields with namelist prefix
                formatted_key = f"{namelist_prefix}%{key.upper()}"
                processed_value = self.process_value(value)

                # Add trailing comma if needed
                if key in comma_fields:
                    line = f"  {formatted_key} = {processed_value},"
                else:
                    line = f"  {formatted_key} = {processed_value}"

                lines.append(line)

        lines.append("/")
        return "\n".join(lines)

    def write_nml(self, destdir: Union[Path, str], *args, **kwargs) -> None:
        """Write namelist to file."""
        destdir = Path(destdir)
        destdir.mkdir(parents=True, exist_ok=True)

        # Use lowercase class name for filename
        filename = f"{self.__class__.__name__.lower()}.nml"
        filepath = destdir / filename

        with open(filepath, "w") as f:
            f.write(self.render(*args, **kwargs))

        logger.info(f"Wrote namelist to {filepath}")
