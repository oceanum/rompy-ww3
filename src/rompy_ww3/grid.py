"""Separate grid classes for each WW3 grid type."""

import logging
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Union
from typing import Union as TypingUnion

from pydantic import Field, model_validator
from rompy.core.grid import BaseGrid

from rompy_ww3.namelists.curv import Curv
from rompy_ww3.namelists.depth import Depth

# Import the existing WW3 namelist objects
from rompy_ww3.namelists.grid import Grid as GRID_NML
from rompy_ww3.namelists.grid import Rect
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

    grid_nml: GRID_NML = Field(
        description="GRID_NML namelist object for WW3 grid",
    )

    @property
    @abstractmethod
    def grid_specific_nml(self) -> Any:
        """Return the grid-specific namelist (e.g., rect_nml, curv_nml, etc.)"""
        pass

    @property
    @abstractmethod
    def grid_specific_name(self) -> str:
        """Return the name of the grid-specific namelist (e.g., 'rect_nml', 'curv_nml', etc.)"""
        pass

    @property
    @abstractmethod
    def namelist_file_attrs(self) -> List[Tuple[str, str]]:
        """Return list of (attribute_name, filename_attribute) for optional namelist files."""
        pass

    @property
    def additional_file_attrs(self) -> List[str]:
        """Return list of additional file attributes specific to the grid type."""
        return []

    def _validate_file_exists(
        self, file_path: Union[str, Path], attr_name: str
    ) -> None:
        """Validate that a file exists at the given path."""
        path = Path(file_path)
        if not path.exists():
            raise ValueError(f"File does not exist: {path}")

    def _validate_namelist_files(self) -> None:
        """Validate that required files exist for optional namelist objects."""
        for attr_name, _ in self.namelist_file_attrs:
            nml_obj = getattr(self, attr_name, None)
            if nml_obj and hasattr(nml_obj, "filename") and nml_obj.filename:
                self._validate_file_exists(nml_obj.filename, attr_name)

    def _copy_additional_files(self, destdir: Path) -> None:
        """Copy additional files specific to this grid type."""
        for attr_name in self.additional_file_attrs:
            src_file = getattr(self, attr_name, None)
            if src_file:
                src_path = Path(src_file)
                dst_path = destdir / src_path.name
                if src_path.exists():
                    shutil.copy2(src_path, dst_path)
                    logger.info(f"Copied {src_path.name} to {destdir}")
                else:
                    raise FileNotFoundError(f"Source file does not exist: {src_path}")

    @model_validator(mode="after")
    def validate_grid_parameters(self) -> "BaseWW3Grid":
        """Validate grid parameters including file existence."""
        # Validate optional namelist files
        self._validate_namelist_files()

        # Validate any additional files
        for attr_name in self.additional_file_attrs:
            file_path = getattr(self, attr_name, None)
            if file_path:
                self._validate_file_exists(file_path, attr_name)

        return self

    def get(self, destdir: Union[str, Path], *args, **kwargs) -> Dict[str, Any]:
        """Copy grid files and return namelist paths."""
        destdir = Path(destdir)
        destdir.mkdir(parents=True, exist_ok=True)

        # Copy additional files specific to this grid type
        self._copy_additional_files(destdir)

        # Copy files referenced in namelist objects
        for attr_name, filename_attr in self.namelist_file_attrs:
            nml_obj = getattr(self, attr_name, None)
            if nml_obj and hasattr(nml_obj, "filename") and nml_obj.filename:
                src_path = Path(nml_obj.filename)
                dst_path = destdir / src_path.name
                if src_path.exists() and not dst_path.exists():
                    shutil.copy2(src_path, dst_path)
                    logger.info(f"Copied {src_path.name} to {destdir}")
                elif src_path.exists() and dst_path.exists():
                    # File already copied, skip
                    pass
                else:
                    raise FileNotFoundError(f"Source file does not exist: {src_path}")

        # Generate and write the namelist files
        namelist_objects = {
            "grid_nml": self.grid_nml,
            self.grid_specific_name: self.grid_specific_nml,
        }

        # Add optional namelists if provided - this will be implemented by subclasses
        self._add_optional_namelists(namelist_objects)

        # Generate and write the namelist files
        namelist_content = {}
        for nml_name, nml_obj in namelist_objects.items():
            if nml_obj:
                nml_content = nml_obj.render()
                namelist_content[nml_name] = nml_content
                filename = f"ww3_grid_{nml_name}.nml"

                with open(destdir / filename, "w") as f:
                    f.write(nml_content)

        logger.info(f"Copied all grid files to {destdir}")
        return namelist_content

    def _add_optional_namelists(self, namelist_objects: dict) -> None:
        """Add optional namelist objects to the dictionary. Implemented by subclasses."""
        # This method will be overridden by subclasses that have optional files
        pass


class RectGrid(BaseWW3Grid):
    """Rectilinear WW3 grid class."""

    model_type: Literal["ww3_rect"] = Field(
        default="ww3_rect",
        description="Model type discriminator for rectilinear grid",
    )

    # Grid namelist objects - REQUIRED for RECT grids
    rect_nml: Rect = Field(
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
