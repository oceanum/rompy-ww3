"""Base model for WW3 namelists."""

import logging
import re
from pathlib import Path
from typing import Any, Dict, Union
from pydantic import model_serializer, model_validator
from rompy.core.types import RompyBaseModel


logger = logging.getLogger(__name__)


def boolean_to_string(value: bool) -> str:
    """Convert boolean to Fortran-style string."""
    return "T" if value else "F"


def camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case."""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.upper()


class NamelistBaseModel(RompyBaseModel):
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

    def process_key(self, key: str) -> str:
        if key == "var1":
            return "VAR(1)"
        elif key == "var2":
            return "VAR(2)"
        elif key == "var3":
            return "VAR(3)"
        else:
            return key.upper()

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
            processed_items = []
            for item in value:
                if isinstance(item, dict) or hasattr(item, "model_dump"):
                    # For complex objects in lists, convert to string representation
                    if hasattr(item, "model_dump"):
                        item_dict = item.model_dump()
                        processed_items.append(str(item_dict))
                    else:
                        processed_items.append(str(item))
                else:
                    processed_items.append(str(self.process_value(item)))
            return ", ".join(processed_items)
        elif hasattr(value, "model_dump"):
            # Convert BaseModel instances to dictionary and then to string
            return str(value.model_dump())

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

        # Process each field recursively
        self._render_recursive(
            model_data, lines, namelist_prefix, self, *args, **kwargs
        )

        lines.append("/")
        return "\n".join(lines)

    def _render_recursive(
        self, data, lines, prefix, parent_obj, path="", *args, **kwargs
    ):
        """Recursively render nested objects with proper formatting."""
        comma_fields = getattr(parent_obj, "_comma_fields", [])

        for key, value in data.items():
            current_obj = getattr(parent_obj, key, None)

            # Check if it's a nested RompyBaseModel instance
            # Using string-based check to avoid circular imports during model loading
            if hasattr(current_obj, "model_dump") and value is not None:
                # Check if the object has a get() method
                if hasattr(current_obj, "get") and callable(
                    getattr(current_obj, "get")
                ):
                    logger.info(
                        f"Calling get() method on object: {type(current_obj).__name__}"
                    )
                    value = current_obj.get(
                        *args, **kwargs
                    )  # Get the value by calling get() method
                else:
                    value = current_obj.model_dump()  # Get the nested model's data

            # Build the current path for the namelist key
            current_path = (
                f"{path}%{self.process_key(key)}"
                if path
                else f"{prefix}%{self.process_key(key)}"
            )

            if isinstance(value, dict):
                # Recursively process nested dictionaries
                self._render_recursive(
                    value, lines, prefix, current_obj, current_path, *args, **kwargs
                )
            elif isinstance(value, list):
                # Handle lists
                processed_value = self.process_value(value)
                line = f"  {current_path} = {processed_value}"
                lines.append(line)
            else:
                if hasattr(value, "get") and callable(getattr(value, "get")):
                    logger.info(
                        f"Calling get() method on value: {type(value).__name__}"
                    )
                    value = value.get()
                # Handle simple values
                processed_value = self.process_value(value)

                # Add trailing comma if needed
                if key in comma_fields:
                    line = f"  {current_path} = {processed_value},"
                else:
                    line = f"  {current_path} = {processed_value}"

                lines.append(line)

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

    def set_default_dates(self, period) -> None:
        """
        Set default start and end dates for date fields in this namelist if they are None.

        Args:
            period: The time period to use for default dates
        """
        # Get attributes of Pydantic models
        if hasattr(self, "model_fields"):
            for field_name in self.model_fields:
                # Check if this field is a date field
                if self._is_date_field(field_name):
                    current_value = getattr(self, field_name)
                    if current_value is None:
                        # Set default date value
                        if (
                            "start" in field_name.lower()
                            or "timestart" in field_name.lower()
                        ):
                            setattr(
                                self, field_name, period.start.strftime("%Y%m%d %H%M%S")
                            )
                        elif (
                            "stop" in field_name.lower()
                            or "timestop" in field_name.lower()
                        ):
                            setattr(
                                self, field_name, period.end.strftime("%Y%m%d %H%M%S")
                            )
                else:
                    # If not a date field, check if it's a nested object that might have date fields
                    field_value = getattr(self, field_name)
                    if hasattr(field_value, "__dict__") or hasattr(
                        field_value, "__pydantic_fields__"
                    ):
                        if field_value is not None and not isinstance(
                            field_value, (str, int, float, bool, list, dict)
                        ):
                            # If the nested object also has a set_default_dates method, call it
                            if hasattr(field_value, "set_default_dates"):
                                field_value.set_default_dates(period)
                            # Otherwise, recursively process its fields
                            else:
                                self._set_nested_object_dates_recursive(
                                    field_value, period
                                )

    def _set_nested_object_dates_recursive(self, obj, period):
        """
        Recursively find and set date fields in a nested object.

        Args:
            obj: The nested object to process
            period: The time period to use for default dates
        """
        # Get attributes of Pydantic models
        if hasattr(obj, "model_fields"):
            for field_name in obj.model_fields:
                # Check if this field is a date field
                if self._is_date_field(field_name):
                    current_value = getattr(obj, field_name)
                    if current_value is None:
                        # Set default date value
                        if (
                            "start" in field_name.lower()
                            or "timestart" in field_name.lower()
                        ):
                            setattr(
                                obj, field_name, period.start.strftime("%Y%m%d %H%M%S")
                            )
                        elif (
                            "stop" in field_name.lower()
                            or "timestop" in field_name.lower()
                        ):
                            setattr(
                                obj, field_name, period.end.strftime("%Y%m%d %H%M%S")
                            )
                else:
                    # If not a date field, check if it's a nested object that might have date fields
                    field_value = getattr(obj, field_name)
                    if hasattr(field_value, "__dict__") or hasattr(
                        field_value, "__pydantic_fields__"
                    ):
                        if field_value is not None and not isinstance(
                            field_value, (str, int, float, bool, list, dict)
                        ):
                            # Recursively process nested objects
                            self._set_nested_object_dates_recursive(field_value, period)

    def _is_date_field(self, field_name: str) -> bool:
        """
        Check if a field name indicates it's a date/time field.

        Args:
            field_name: Name of the field to check

        Returns:
            True if the field is likely a date field, False otherwise
        """
        field_name_lower = field_name.lower()

        # Explicitly allow known date fields - these are the actual date/time values
        if field_name_lower in [
            "start",
            "stop",
            "timestart",
            "timestop",
            "time_start",
            "time_stop",
            "update_time",
        ]:
            return True

        # Explicitly exclude known non-date fields that contain date-like substrings
        # These are object containers that contain date fields, not date fields themselves
        if field_name_lower in [
            "timestride",
            "timecount",
            "timesplit",
            "stride",
            "count",
            "restart",
            "boundary",
            "track",
            "point",
            "partition",
            "coupling",
            "output_date",
            "date",
        ]:
            return False

        # For all other cases, if it contains obvious date indicators and was not excluded
        # This is a conservative approach: only identify actual date value fields, not containers
        date_indicators = [
            "start",
            "stop",
            "timestart",
            "timestop",
            "time_start",
            "time_stop",
        ]
        for indicator in date_indicators:
            if field_name_lower == indicator:  # Only exact matches, not partial
                return True

        return False
