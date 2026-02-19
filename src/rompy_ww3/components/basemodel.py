"""Base model for WW3 components."""

from typing import Any, Union
from pathlib import Path
import logging
from ..namelists.basemodel import NamelistBaseModel
from rompy.core.types import RompyBaseModel

from ..settings import WW3_DIR


logger = logging.getLogger(__name__)


class WW3ComponentBaseModel(RompyBaseModel):
    """Base class for WW3 components with common rendering functionality.

    This base class provides the foundation for all WW3 component classes. It handles
    the common functionality needed for rendering namelist content, writing files,
    and processing values in the WW3-required format.

    The base class ensures consistency across all WW3 components by providing:
    - Standardized rendering methods for namelist content
    - Consistent file writing functionality
    - Proper value processing for Fortran-style formatting
    - Integration with rompy core functionality

    All WW3 component classes should inherit from this base class to ensure
    consistent behavior and proper integration with the rompy-ww3 framework.

    Key Features:
    - **Rendering**: Standardized namelist rendering with proper formatting
    - **File Operations**: Consistent file writing with automatic directory creation
    - **Value Processing**: Proper conversion of Python values to Fortran format
    - **Command Generation**: Standardized run command generation for WW3 executables
    """

    def render(self, *args, **kwargs) -> str:
        """Render namelist as a string.

        This method generates the namelist content by iterating through all
        namelist objects contained in this component and rendering them.

        The rendering process:
        1. Gets the model data using model_dump()
        2. Iterates through each field in the model
        3. Renders namelist objects while skipping non-namelist fields
        4. Combines all rendered content with proper formatting

        Args:
            *args: Variable positional arguments to pass to render methods
            **kwargs: Variable keyword arguments to pass to render methods

        Returns:
            str: The rendered namelist content as a string with proper formatting

        Note:
            Empty namelists return None, which is handled appropriately by callers.
        """
        content = []
        # Get the model data
        model_data = self.model_dump()
        for key, value in model_data.items():
            if value is None:
                continue
            else:
                nml = getattr(self, key)
                if isinstance(value, list):
                    # Check if this is a list of homogeneous inputs (needs special handling)
                    if key == "homog_input" and nml:
                        # Import here to avoid circular imports
                        from ..namelists.homogeneous import HomogInput

                        if isinstance(nml[0], HomogInput):
                            # Collect all homog_input entries into a single namelist block
                            homog_lines = ["&HOMOG_INPUT_NML"]
                            for idx, item in enumerate(nml, 1):
                                if isinstance(item, HomogInput):
                                    homog_lines.append(item.render_entry(idx))
                            homog_lines.append("/")
                            content.append("\n".join(homog_lines))
                            continue

                    # Handle other lists of namelist objects
                    for idx, item in enumerate(nml, 1):
                        if isinstance(item, NamelistBaseModel):
                            content.append(item.render(index=idx, *args, **kwargs))
                elif isinstance(nml, NamelistBaseModel):
                    content.append(nml.render(*args, **kwargs))
        content.append(
            ""
        )  # Add final newline (fixes bug in prnc that requires final newline)
        return "\n".join(content)

    @property
    def nml_filename(self) -> str:
        """Get the default filename for this component.

        Returns the standard WW3 namelist filename based on the component class name.
        For example, a Shel component would return 'ww3_shel.nml'.

        Returns:
            str: The default namelist filename for this component type
        """
        return f"ww3_{self.__class__.__name__.lower()}.nml"

    @property
    def prepend_cmd(self) -> str:
        """Get the string to prepend to the namelist file.

        This property provides any command that should be executed before
        running the WW3 executable for this component. This is typically
        used for setting up symbolic links or other pre-execution setup.

        Returns:
            str: The command to prepend, or None if no prepending is needed
        """
        return None

    @property
    def run_cmd(self) -> str:
        """Get the default run command for this component.

        Constructs the command needed to run the WW3 executable associated
        with this component. The command includes the full path if WW3_DIR
        is set, otherwise assumes the binary is in the system PATH.

        Returns:
            str: The command to run the WW3 executable for this component
        """
        name = self.__class__.__name__.lower()
        # Construct the command to run and print logs to stdout as well as save to file
        cmdlist = []
        if self.prepend_cmd:
            cmdlist.append(self.prepend_cmd)
        cmd = f"ww3_{name}"
        if WW3_DIR:
            cmdlist.append(f"{WW3_DIR}/{cmd}")
        else:
            # assume binary is in PATH
            cmdlist.append(cmd)
        return "\n".join(cmdlist)

    def write_nml(self, destdir: Union[Path, str], *args, **kwargs) -> None:
        """Write the rendered component to a namelist file.

        Renders the component content and writes it to the appropriate namelist file
        in the specified destination directory. Creates the directory if it doesn't exist.

        Args:
            destdir: Directory path where the namelist file should be written.
                    Can be a string or Path object.
            *args: Variable positional arguments to pass to the render method
            **kwargs: Variable keyword arguments to pass to the render method

        Returns:
            Path: The path to the written namelist file

        Raises:
            IOError: If there are issues writing to the file
            OSError: If there are issues creating directories
        """
        destdir = Path(destdir)
        destdir.mkdir(parents=True, exist_ok=True)

        # Use lowercase class name for filename
        filepath = destdir / self.nml_filename
        rendered = self.render(destdir=destdir, *args, **kwargs)

        if rendered is not None:
            with open(filepath, "w") as f:
                f.write(rendered)

        logger.info(f"Wrote component to {filepath}")
        return filepath

    def model_dump(self, *args, **kwargs) -> dict:
        """Return the component as a dictionary.

        This method is needed to maintain compatibility with NamelistBaseModel interface.
        It returns the component data as a dictionary using the parent class implementation.

        Args:
            *args: Variable positional arguments to pass to the parent method
            **kwargs: Variable keyword arguments to pass to the parent method

        Returns:
            dict: The component data as a dictionary representation
        """
        return super().model_dump(*args, **kwargs)

    def model_dump_json(self, *args, **kwargs) -> str:
        """Return the component as a JSON string.

        This method is needed to maintain compatibility with NamelistBaseModel interface.
        It returns the component data as a JSON-formatted string using the parent class implementation.

        Args:
            *args: Variable positional arguments to pass to the parent method
            **kwargs: Variable keyword arguments to pass to the parent method

        Returns:
            str: The component data as a JSON-formatted string
        """
        return super().model_dump_json(*args, **kwargs)

    def process_value(self, value: Any) -> Any:
        """Process value for namelist formatting (from NamelistBaseModel).

        Converts Python values to the appropriate Fortran-style formatting for WW3 namelists.
        This includes handling booleans, strings, and lists with proper formatting.

        Args:
            value: The value to process for namelist formatting

        Returns:
            Any: The processed value in appropriate Fortran-style format
        """
        if isinstance(value, bool):
            return self.boolean_to_string(value)
        elif isinstance(value, str):
            # Don't quote Fortran booleans
            if value in ["T", "F"]:
                return value
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

    def boolean_to_string(self, value: bool) -> str:
        """Convert boolean to Fortran-style string.

        Converts Python boolean values to Fortran-style 'T' or 'F' strings
        as required by WW3 namelists.

        Args:
            value: Boolean value to convert

        Returns:
            str: 'T' for True, 'F' for False
        """
        return "T" if value else "F"

    def get_namelist_name(self) -> str:
        """Get the namelist name for this model.

        This method should be overridden by subclasses to provide the appropriate namelist name.

        Returns:
            str: The namelist name for this component
        """
        # Default implementation - should be overridden by subclasses
        class_name = self.__class__.__name__
        return f"{class_name.upper()}_NML"

    @property
    def component_name(self) -> str:
        """Get the component name for this model.

        Returns the standardized component name based on the class name.

        Returns:
            str: The standardized component name
        """
        class_name = self.__class__.__name__
        return f"{class_name.upper()}_NML"
