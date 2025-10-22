"""FILE_NML namelist implementation for WW3 preprocessing."""

from typing import Optional, Union
from pydantic import Field
from .basemodel import NamelistBaseModel
from ..core.data import WW3DataBlob


class File(NamelistBaseModel):
    """FILE_NML namelist for WW3 preprocessing.

    Defines the content of the input file for ww3_prnc.
    """

    filename: Optional[Union[str, WW3DataBlob]] = Field(
        default=None, description="Input filename for preprocessing"
    )
    var1: Optional[str] = Field(
        default=None, description="Variable name for first component"
    )
    var2: Optional[str] = Field(
        default=None, description="Variable name for second component"
    )
    var3: Optional[str] = Field(
        default=None, description="Variable name for third component"
    )

    def get_namelist_name(self) -> str:
        """Return the specific namelist name for FILE_NML."""
        return "FILE_NML"

    def render(self) -> str:
        """Render the namelist with special handling for VAR arrays."""
        lines = []
        lines.append(f"&{self.get_namelist_name()}")

        # Add standard fields
        if self.filename is not None:
            lines.append(f"  FILE%FILENAME = '{self.filename}'")
        if self.var1 is not None:
            lines.append(f"  FILE%VAR(1) = '{self.var1}'")
        if self.var2 is not None:
            lines.append(f"  FILE%VAR(2) = '{self.var2}'")
        if self.var3 is not None:
            lines.append(f"  FILE%VAR(3) = '{self.var3}'")

        lines.append("/")
        return "\n".join(lines)
