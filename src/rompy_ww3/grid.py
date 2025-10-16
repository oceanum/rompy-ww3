"""Separate grid classes for each WW3 grid type."""

import logging
from pathlib import Path
from typing import Literal, Optional, Union, Dict, Any
from pydantic import Field, model_validator
import shutil

from rompy.core.grid import BaseGrid

# Import the existing WW3 namelist objects
from rompy_ww3.namelists.grid import Grid as GRID_NML, Rect
from rompy_ww3.namelists.curv import Curv
from rompy_ww3.namelists.unst import Unst
from rompy_ww3.namelists.smc import Smc
from rompy_ww3.namelists.depth import Depth
from rompy_ww3.namelists.mask import Mask
from rompy_ww3.namelists.obstacle import Obstacle
from rompy_ww3.namelists.slope import Slope
from rompy_ww3.namelists.sediment import Sediment


logger = logging.getLogger(__name__)

HERE = Path(__file__).parent


class RectGrid(BaseGrid):
    """Rectilinear WW3 grid class."""

    model_type: Literal["ww3_rect"] = Field(
        default="ww3_rect",
        description="Model type discriminator for rectilinear grid",
    )

    # Grid namelist objects - REQUIRED for RECT grids
    grid_nml: GRID_NML = Field(
        description="GRID_NML namelist object for rectilinear grid",
    )
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

    @model_validator(mode="after")
    def validate_rect_grid_parameters(self) -> "RectGrid":
        """Validate rectilinear grid parameters."""
        # Validate that required files exist if specified
        namelist_attrs = ["depth", "mask", "obst", "slope", "sed"]
        for attr_name in namelist_attrs:
            nml_obj = getattr(self, attr_name, None)
            if nml_obj and hasattr(nml_obj, "filename") and nml_obj.filename:
                file_path = Path(nml_obj.filename)
                if not file_path.exists():
                    raise ValueError(
                        f"File referenced in {attr_name} does not exist: {file_path}"
                    )

        return self

    def get(self, destdir: Union[str, Path], *args, **kwargs) -> Dict[str, Any]:
        """Copy rectilinear grid files and return namelist paths."""
        destdir = Path(destdir)
        destdir.mkdir(parents=True, exist_ok=True)

        # Copy files referenced in namelist objects
        namelist_file_attrs = [
            ("depth", "filename"),
            ("mask", "filename"),
            ("obst", "filename"),
            ("slope", "filename"),
            ("sed", "filename"),
        ]

        for attr_name, filename_attr in namelist_file_attrs:
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
            "rect_nml": self.rect_nml,
        }

        # Add optional namelists if provided
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

        # Generate and write the namelist files
        namelist_content = {}
        for nml_name, nml_obj in namelist_objects.items():
            if nml_obj:
                nml_content = nml_obj.render()
                namelist_content[nml_name] = nml_content
                filename = f"ww3_grid_{nml_name}.nml"

                with open(destdir / filename, "w") as f:
                    f.write(nml_content)

        logger.info(f"Copied all rectilinear grid files to {destdir}")
        return namelist_content


class CurvGrid(BaseGrid):
    """Curvilinear WW3 grid class."""

    model_type: Literal["ww3_curv"] = Field(
        default="ww3_curv",
        description="Model type discriminator for curvilinear grid",
    )

    # Grid namelist objects - REQUIRED for CURV grids
    grid_nml: GRID_NML = Field(
        description="GRID_NML namelist object for curvilinear grid",
    )
    curv_nml: Curv = Field(
        description="CURV_NML namelist object for curvilinear grid",
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

    # Coordinate files - REQUIRED for CURV grids
    x_coord_file: Path = Field(
        description="Path to x-coordinate file for curvilinear grid",
    )
    y_coord_file: Path = Field(
        description="Path to y-coordinate file for curvilinear grid",
    )

    @model_validator(mode="after")
    def validate_curv_grid_parameters(self) -> "CurvGrid":
        """Validate curvilinear grid parameters."""
        # Validate coordinate files
        file_attrs = ["x_coord_file", "y_coord_file"]
        for attr_name in file_attrs:
            file_path = getattr(self, attr_name, None)
            if file_path and not Path(file_path).exists():
                raise ValueError(f"File does not exist: {file_path}")

        # Validate namelist object files
        namelist_attrs = ["depth", "mask", "obst", "slope", "sed"]
        for attr_name in namelist_attrs:
            nml_obj = getattr(self, attr_name, None)
            if nml_obj and hasattr(nml_obj, "filename") and nml_obj.filename:
                file_path = Path(nml_obj.filename)
                if not file_path.exists():
                    raise ValueError(
                        f"File referenced in {attr_name} does not exist: {file_path}"
                    )

        return self

    def get(self, destdir: Union[str, Path], *args, **kwargs) -> Dict[str, Any]:
        """Copy curvilinear grid files and return namelist paths."""
        destdir = Path(destdir)
        destdir.mkdir(parents=True, exist_ok=True)

        # Copy coordinate files
        file_attrs = ["x_coord_file", "y_coord_file"]
        for attr_name in file_attrs:
            src_file = getattr(self, attr_name, None)
            if src_file:
                src_path = Path(src_file)
                dst_path = destdir / src_path.name
                if src_path.exists():
                    shutil.copy2(src_path, dst_path)
                    logger.info(f"Copied {src_path.name} to {destdir}")
                else:
                    raise FileNotFoundError(f"Source file does not exist: {src_path}")

        # Copy files referenced in namelist objects
        namelist_file_attrs = [
            ("depth", "filename"),
            ("mask", "filename"),
            ("obst", "filename"),
            ("slope", "filename"),
            ("sed", "filename"),
        ]

        for attr_name, filename_attr in namelist_file_attrs:
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
            "curv_nml": self.curv_nml,
        }

        # Add optional namelists if provided
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

        # Generate and write the namelist files
        namelist_content = {}
        for nml_name, nml_obj in namelist_objects.items():
            if nml_obj:
                nml_content = nml_obj.render()
                namelist_content[nml_name] = nml_content
                filename = f"ww3_grid_{nml_name}.nml"

                with open(destdir / filename, "w") as f:
                    f.write(nml_content)

        logger.info(f"Copied all curvilinear grid files to {destdir}")
        return namelist_content


class UnstGrid(BaseGrid):
    """Unstructured WW3 grid class."""

    model_type: Literal["ww3_unst"] = Field(
        default="ww3_unst",
        description="Model type discriminator for unstructured grid",
    )

    # Grid namelist objects - REQUIRED for UNST grids
    grid_nml: GRID_NML = Field(
        description="GRID_NML namelist object for unstructured grid",
    )
    unst_nml: Unst = Field(
        description="UNST_NML namelist object for unstructured grid",
    )

    # Optional boundary file
    unst_obc_file: Optional[Path] = Field(
        default=None,
        description="Path to additional boundary list file for unstructured grid",
    )

    @model_validator(mode="after")
    def validate_unst_grid_parameters(self) -> "UnstGrid":
        """Validate unstructured grid parameters."""
        # Validate boundary file if specified
        if self.unst_obc_file and not Path(self.unst_obc_file).exists():
            raise ValueError(f"File does not exist: {self.unst_obc_file}")

        return self

    def get(self, destdir: Union[str, Path], *args, **kwargs) -> Dict[str, Any]:
        """Copy unstructured grid files and return namelist paths."""
        destdir = Path(destdir)
        destdir.mkdir(parents=True, exist_ok=True)

        # Copy boundary file if specified
        if self.unst_obc_file:
            src_path = Path(self.unst_obc_file)
            dst_path = destdir / src_path.name
            if src_path.exists():
                shutil.copy2(src_path, dst_path)
                logger.info(f"Copied {src_path.name} to {destdir}")
            else:
                raise FileNotFoundError(f"Source file does not exist: {src_path}")

        # Generate and write the namelist files
        namelist_objects = {
            "grid_nml": self.grid_nml,
            "unst_nml": self.unst_nml,
        }

        # Generate and write the namelist files
        namelist_content = {}
        for nml_name, nml_obj in namelist_objects.items():
            if nml_obj:
                nml_content = nml_obj.render()
                namelist_content[nml_name] = nml_content
                filename = f"ww3_grid_{nml_name}.nml"

                with open(destdir / filename, "w") as f:
                    f.write(nml_content)

        logger.info(f"Copied all unstructured grid files to {destdir}")
        return namelist_content


class SmcGrid(BaseGrid):
    """SMC (Spherical Multiple-Cell) WW3 grid class."""

    model_type: Literal["ww3_smc"] = Field(
        default="ww3_smc",
        description="Model type discriminator for SMC grid",
    )

    # Grid namelist objects - REQUIRED for SMC grids
    grid_nml: GRID_NML = Field(
        description="GRID_NML namelist object for SMC grid",
    )
    smc_nml: Smc = Field(
        description="SMC_NML namelist object for SMC grid",
    )

    @model_validator(mode="after")
    def validate_smc_grid_parameters(self) -> "SmcGrid":
        """Validate SMC grid parameters."""
        # No specific validation needed for SMC grids
        return self

    def get(self, destdir: Union[str, Path], *args, **kwargs) -> Dict[str, Any]:
        """Copy SMC grid files and return namelist paths."""
        destdir = Path(destdir)
        destdir.mkdir(parents=True, exist_ok=True)

        # Generate and write the namelist files
        namelist_objects = {
            "grid_nml": self.grid_nml,
            "smc_nml": self.smc_nml,
        }

        # Generate and write the namelist files
        namelist_content = {}
        for nml_name, nml_obj in namelist_objects.items():
            if nml_obj:
                nml_content = nml_obj.render()
                namelist_content[nml_name] = nml_content
                filename = f"ww3_grid_{nml_name}.nml"

                with open(destdir / filename, "w") as f:
                    f.write(nml_content)

        logger.info(f"Copied all SMC grid files to {destdir}")
        return namelist_content


# Convenience union type for any WW3 grid
from typing import Union as TypingUnion

AnyWw3Grid = TypingUnion[RectGrid, CurvGrid, UnstGrid, SmcGrid]
