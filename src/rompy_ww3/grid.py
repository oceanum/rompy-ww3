"""Separate grid classes for each WW3 grid type."""

import logging
from abc import ABC
from pathlib import Path
from typing import List, Literal, Optional, Tuple
from typing import Union as TypingUnion
import numpy as np

from pydantic import Field
from rompy.core.grid import BaseGrid

from rompy_ww3.namelists.curv import Curv
from rompy_ww3.namelists.depth import Depth

# Import the existing WW3 namelist objects
from rompy_ww3.namelists.grid import Grid, Rect
from rompy_ww3.namelists.mask import Mask
from rompy_ww3.namelists.obstacle import Obstacle
from rompy_ww3.namelists.sediment import Sediment
from rompy_ww3.namelists.slope import Slope
from rompy_ww3.namelists.smc import Smc
from rompy_ww3.namelists.unst import Unst


logger = logging.getLogger(__name__)

HERE = Path(__file__).parent


class BaseWW3Grid(BaseGrid, ABC):
    """Base class for WW3 grid classes."""

    grid: Grid = Field(..., description="GRID_NML namelist object for WW3")


class RectGrid(BaseWW3Grid):
    """Rectilinear WW3 grid class."""

    model_type: Literal["ww3_rect"] = Field(
        default="ww3_rect",
        description="Model type discriminator for rectilinear grid",
    )

    # Grid namelist objects - REQUIRED for RECT grids
    rect: Rect = Field(
        ...,
        description="RECT_NML namelist object for rectilinear grid",
    )

    # File-based namelist objects - OPTIONAL for RECT grids
    depth: Optional[Depth] = Field(
        default=None,
        description="Depth namelist object for rectilinear grid",
    )
    mask: Optional[Mask] = Field(
        default=None,
        description="Mask namelist object for rectilinear grid",
    )
    obst: Optional[Obstacle] = Field(
        default=None,
        description="Obstruction namelist object for rectilinear grid",
    )
    slope: Optional[Slope] = Field(
        default=None,
        description="Slope namelist object for rectilinear grid",
    )
    sed: Optional[Sediment] = Field(
        default=None,
        description="Sediment namelist object for rectilinear grid",
    )

    @property
    def x(self) -> np.ndarray:
        return np.linspace(
            self.rect.x0, self.rect.x0 + self.rect.sx * (self.rect.nx - 1), self.rect.nx
        )

    @property
    def y(self) -> np.ndarray:
        return np.linspace(
            self.rect.y0, self.rect.y0 + self.rect.sy * (self.rect.ny - 1), self.rect.ny
        )

    @property
    def grid_specific_nml(self) -> Rect:
        return self.rect_nml

    @property
    def grid_specific_name(self) -> str:
        return "rect_nml"

    @property
    def namelist_file_attrs(self) -> List[Tuple[str, str]]:
        """Return list of (attribute_name, filename_attribute) for optional namelist files."""
        return [
            ("depth", "filename"),
            ("mask", "filename"),
            ("obst", "filename"),
            ("slope", "filename"),
            ("sed", "filename"),
        ]

    def _add_optional_namelists(self, namelist_objects: dict) -> None:
        """Add optional namelist objects to the dictionary."""
        if self.depth:
            namelist_objects["depth_nml"] = self.depth
        if self.mask:
            namelist_objects["mask_nml"] = self.mask
        if self.obst:
            namelist_objects["obst_nml"] = self.obst
        if self.slope:
            namelist_objects["slope_nml"] = self.slope
        if self.sed:
            namelist_objects["sed_nml"] = self.sed


class CurvGrid(BaseWW3Grid):
    """Curvilinear WW3 grid class."""

    model_type: Literal["ww3_curv"] = Field(
        default="ww3_curv",
        description="Model type discriminator for curvilinear grid",
    )

    # Grid namelist objects - REQUIRED for CURV grids
    curv_nml: Curv = Field(
        description="CURV_NML namelist object for curvilinear grid",
    )

    # Coordinate files - REQUIRED for CURV grids
    x_coord_file: Path = Field(
        description="Path to x-coordinate file for curvilinear grid",
    )
    y_coord_file: Path = Field(
        description="Path to y-coordinate file for curvilinear grid",
    )

    # File-based namelist objects - OPTIONAL for CURV grids
    depth: Optional[Depth] = Field(
        default=None,
        description="Depth namelist object for curvilinear grid",
    )
    mask: Optional[Mask] = Field(
        default=None,
        description="Mask namelist object for curvilinear grid",
    )
    obst: Optional[Obstacle] = Field(
        default=None,
        description="Obstruction namelist object for curvilinear grid",
    )
    slope: Optional[Slope] = Field(
        default=None,
        description="Slope namelist object for curvilinear grid",
    )
    sed: Optional[Sediment] = Field(
        default=None,
        description="Sediment namelist object for curvilinear grid",
    )

    @property
    def grid_specific_nml(self) -> Curv:
        return self.curv_nml

    @property
    def grid_specific_name(self) -> str:
        return "curv_nml"

    @property
    def additional_file_attrs(self) -> List[str]:
        return ["x_coord_file", "y_coord_file"]

    @property
    def namelist_file_attrs(self) -> List[Tuple[str, str]]:
        """Return list of (attribute_name, filename_attribute) for optional namelist files."""
        return [
            ("depth", "filename"),
            ("mask", "filename"),
            ("obst", "filename"),
            ("slope", "filename"),
            ("sed", "filename"),
        ]

    def _add_optional_namelists(self, namelist_objects: dict) -> None:
        """Add optional namelist objects to the dictionary."""
        if self.depth:
            namelist_objects["depth_nml"] = self.depth
        if self.mask:
            namelist_objects["mask_nml"] = self.mask
        if self.obst:
            namelist_objects["obst_nml"] = self.obst
        if self.slope:
            namelist_objects["slope_nml"] = self.slope
        if self.sed:
            namelist_objects["sed_nml"] = self.sed


class UnstGrid(BaseWW3Grid):
    """Unstructured WW3 grid class."""

    model_type: Literal["ww3_unst"] = Field(
        default="ww3_unst",
        description="Model type discriminator for unstructured grid",
    )

    # Grid namelist objects - REQUIRED for UNST grids
    unst_nml: Unst = Field(
        description="UNST_NML namelist object for unstructured grid",
    )

    # Optional boundary file
    unst_obc_file: Optional[Path] = Field(
        default=None,
        description="Path to additional boundary list file for unstructured grid",
    )

    @property
    def grid_specific_nml(self) -> Unst:
        return self.unst_nml

    @property
    def grid_specific_name(self) -> str:
        return "unst_nml"

    @property
    def additional_file_attrs(self) -> List[str]:
        return ["unst_obc_file"] if self.unst_obc_file else []

    @property
    def namelist_file_attrs(self) -> List[Tuple[str, str]]:
        """Return empty list as UNST grids don't typically use optional namelist files."""
        return []

    def _add_optional_namelists(self, namelist_objects: dict) -> None:
        """Add optional namelist objects to the dictionary. UNST has none."""
        pass


class SmcGrid(BaseWW3Grid):
    """SMC (Spherical Multiple-Cell) WW3 grid class."""

    model_type: Literal["ww3_smc"] = Field(
        default="ww3_smc",
        description="Model type discriminator for SMC grid",
    )

    # Grid namelist objects - REQUIRED for SMC grids
    smc_nml: Smc = Field(
        description="SMC_NML namelist object for SMC grid",
    )

    @property
    def grid_specific_nml(self) -> Smc:
        return self.smc_nml

    @property
    def grid_specific_name(self) -> str:
        return "smc_nml"

    @property
    def additional_file_attrs(self) -> List[str]:
        """Return list of additional file attributes specific to the grid type."""
        return []

    @property
    def namelist_file_attrs(self) -> List[Tuple[str, str]]:
        """Return empty list as SMC grids don't typically use optional namelist files."""
        return []

    def _add_optional_namelists(self, namelist_objects: dict) -> None:
        """Add optional namelist objects to the dictionary. SMC has none."""
        pass


# Convenience union type for any WW3 grid
AnyWw3Grid = TypingUnion[RectGrid, CurvGrid, UnstGrid, SmcGrid]
