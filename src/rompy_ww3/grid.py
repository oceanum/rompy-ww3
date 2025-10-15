"""WW3 Rompy grid."""

import logging
from pathlib import Path
from typing import Literal, Optional, Union, Dict, Any
from pydantic import Field, model_validator
import shutil

from rompy.core.grid import RegularGrid

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


class Grid(RegularGrid):
    """Ww3 grid class with WW3-specific parameters.

    This class extends the RegularGrid with WW3-specific grid parameters
    needed for wave model configuration.
    """

    model_type: Literal["ww3"] = Field(
        default="ww3",
        description="Model type discriminator",
    )

    # WW3 grid parameters
    name: Optional[str] = Field(
        default=None, description="Grid name for identification"
    )
    grid_type: Optional[str] = Field(
        default="RECT",
        description="Grid type: 'RECT' (rectilinear), 'CURV' (curvilinear), 'UNST' (unstructured), 'SMC' (spherical multiple-cell)",
    )
    coordinate_system: Optional[str] = Field(
        default="SPHE",
        description="Coordinate system: 'SPHE' (spherical), 'CART' (cartesian)",
    )
    grid_closure: Optional[str] = Field(
        default="NONE",
        description="Grid closure: 'NONE', 'SMPL' (simple), 'TRPL' (tripole)",
    )
    zlim: Optional[float] = Field(
        default=-0.10, description="Minimum depth limit (meters)"
    )
    dmin: Optional[float] = Field(
        default=2.5, description="Minimum depth for wave propagation (meters)"
    )

    # Rectilinear grid parameters
    nx: Optional[int] = Field(
        default=None, description="Number of points along x-axis (for RECT grids)"
    )
    ny: Optional[int] = Field(
        default=None, description="Number of points along y-axis (for RECT grids)"
    )
    sx: Optional[float] = Field(
        default=None, description="Grid increment along x-axis (for RECT grids)"
    )
    sy: Optional[float] = Field(
        default=None, description="Grid increment along y-axis (for RECT grids)"
    )
    sf: Optional[float] = Field(
        default=None, description="Scaling factor for grid increments (for RECT grids)"
    )
    sf0: Optional[float] = Field(
        default=None,
        description="Scaling factor for x0, y0 coordinates (for RECT grids)",
    )

    # Grid boundaries
    x0: Optional[float] = Field(
        default=None, description="Western boundary of the grid"
    )
    y0: Optional[float] = Field(
        default=None, description="Southern boundary of the grid"
    )
    x1: Optional[float] = Field(
        default=None, description="Eastern boundary of the grid"
    )
    y1: Optional[float] = Field(
        default=None, description="Northern boundary of the grid"
    )

    # Grid file definitions
    # For RECT and CURV grids
    depth: Optional[Depth] = Field(
        default=None,
        description="Depth namelist object for RECT/CURV grids",
    )
    mask: Optional[Mask] = Field(
        default=None,
        description="Mask namelist object for RECT/CURV grids",
    )
    obst: Optional[Obstacle] = Field(
        default=None,
        description="Obstruction namelist object for RECT/CURV grids",
    )
    slope: Optional[Slope] = Field(
        default=None,
        description="Slope namelist object for RECT/CURV grids",
    )
    sed: Optional[Sediment] = Field(
        default=None,
        description="Sediment namelist object for RECT/CURV grids",
    )

    # For CURV grids - coordinate files (these are just file paths that get copied)
    x_coord_file: Optional[Path] = Field(
        default=None,
        description="Path to x-coordinate file for CURV grids, will be copied to staging directory",
    )
    y_coord_file: Optional[Path] = Field(
        default=None,
        description="Path to y-coordinate file for CURV grids, will be copied to staging directory",
    )

    # For UNST grids
    unst: Optional[Unst] = Field(
        default=None,
        description="Unstructured grid namelist object for UNST grids",
    )
    unst_obc_file: Optional[Path] = Field(
        default=None,
        description="Path to additional boundary list file for UNST grids, will be copied to staging directory",
    )

    # For SMC grids
    smc: Optional[Smc] = Field(
        default=None,
        description="SMC grid namelist object for SMC grids",
    )

    @model_validator(mode="after")
    def validate_grid_parameters(self) -> "Grid":
        """Validate grid parameters."""
        # Validate grid type
        if self.grid_type and self.grid_type not in ["RECT", "CURV", "UNST", "SMC"]:
            raise ValueError(
                "grid_type must be one of 'RECT', 'CURV', 'UNST', or 'SMC'"
            )

        # Validate coordinate system
        if self.coordinate_system and self.coordinate_system not in ["SPHE", "CART"]:
            raise ValueError("coordinate_system must be one of 'SPHE' or 'CART'")

        # Validate grid closure
        if self.grid_closure and self.grid_closure not in ["NONE", "SMPL", "TRPL"]:
            raise ValueError("grid_closure must be one of 'NONE', 'SMPL', or 'TRPL'")

        # Validate rectilinear grid parameters
        if self.grid_type == "RECT":
            if self.nx is not None and self.nx <= 0:
                raise ValueError("nx must be positive for RECT grids")
            if self.ny is not None and self.ny <= 0:
                raise ValueError("ny must be positive for RECT grids")
            if self.sx is not None and self.sx <= 0:
                raise ValueError("sx must be positive for RECT grids")
            if self.sy is not None and self.sy <= 0:
                raise ValueError("sy must be positive for RECT grids")

        # Validate boundaries
        if self.x0 is not None and self.x1 is not None and self.x0 >= self.x1:
            raise ValueError("x0 must be less than x1")
        if self.y0 is not None and self.y1 is not None and self.y0 >= self.y1:
            raise ValueError("y0 must be less than y1")

        # Validate that required files exist if specified
        file_attrs = [
            "x_coord_file",
            "y_coord_file",
            "unst_obc_file",
        ]

        for attr_name in file_attrs:
            file_path = getattr(self, attr_name, None)
            if file_path and not Path(file_path).exists():
                raise ValueError(f"File does not exist: {file_path}")

        # Also check files referenced in namelist objects
        namelist_attrs = ["depth", "mask", "obst", "slope", "sed", "unst", "smc"]
        for attr_name in namelist_attrs:
            nml_obj = getattr(self, attr_name, None)
            if nml_obj and hasattr(nml_obj, "filename") and nml_obj.filename:
                file_path = Path(nml_obj.filename)
                if not file_path.exists():
                    raise ValueError(
                        f"File referenced in {attr_name} does not exist: {file_path}"
                    )

        return self

    @property
    def grid_dimensions(self) -> tuple[Optional[int], Optional[int]]:
        """Get grid dimensions (nx, ny)."""
        return (self.nx, self.ny)

    @property
    def grid_spacing(self) -> tuple[Optional[float], Optional[float]]:
        """Get grid spacing (sx, sy)."""
        return (self.sx, self.sy)

    @property
    def grid_boundaries(
        self,
    ) -> tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
        """Get grid boundaries (x0, y0, x1, y1)."""
        return (self.x0, self.y0, self.x1, self.y1)

    def calculate_grid_size(self) -> Optional[float]:
        """Calculate approximate grid area in square degrees or square meters.

        Returns:
            Approximate grid area or None if boundaries cannot be determined.
        """
        # Try to use explicit boundaries if available
        x0 = self.x0
        y0 = self.y0
        x1 = self.x1
        y1 = self.y1

        # If explicit boundaries are not fully defined, try to compute from dx/dy/nx/ny
        if x0 is not None and y0 is not None:
            if (
                x1 is None
                and hasattr(self, "dx")
                and hasattr(self, "nx")
                and self.dx is not None
                and self.nx is not None
            ):
                x1 = x0 + (self.nx - 1) * self.dx
            if (
                y1 is None
                and hasattr(self, "dy")
                and hasattr(self, "ny")
                and self.dy is not None
                and self.ny is not None
            ):
                y1 = y0 + (self.ny - 1) * self.dy

        # Now check if we have all boundaries
        if x0 is None or x1 is None or y0 is None or y1 is None:
            return None

        if self.coordinate_system == "SPHE":
            # Approximate area calculation for spherical coordinates (in square degrees)
            return (x1 - x0) * (y1 - y0)
        else:
            # Cartesian coordinates (in square meters or whatever units are used)
            return (x1 - x0) * (y1 - y0)

    def generate_grid_nml(self) -> str:
        """Generate GRID_NML namelist content as string."""
        nml_obj = GRID_NML(
            name=self.name or "UNSET",
            nml="namelists.nml",
            type=self.grid_type,
            coord=self.coordinate_system,
            clos=self.grid_closure,
            zlim=self.zlim,
            dmin=self.dmin,
        )
        return nml_obj.render() if nml_obj else ""

    def generate_rect_nml(self) -> str:
        """Generate RECT_NML namelist content as string."""
        nml_obj = Rect(
            nx=self.nx or getattr(self, "xsize", 0),
            ny=self.ny or getattr(self, "ysize", 0),
            sx=self.sx or self.dx if hasattr(self, "dx") else None,
            sy=self.sy or self.dy if hasattr(self, "dy") else None,
            sf=self.sf,
            x0=self.x0,
            y0=self.y0,
            sf0=self.sf0,
        )
        return nml_obj.render() if nml_obj else ""

    def generate_curv_nml(self) -> str:
        """Generate CURV_NML namelist content as string."""
        from rompy_ww3.namelists.curv import CoordData

        # Define coordinate objects if files are provided
        xcoord = None
        ycoord = None
        if self.x_coord_file:
            xcoord = CoordData(
                filename=self.x_coord_file.name, sf=0.25, off=-0.5, idla=3
            )
        if self.y_coord_file:
            ycoord = CoordData(
                filename=self.y_coord_file.name, sf=0.25, off=0.5, idla=3
            )

        nml_obj = Curv(
            nx=self.nx or getattr(self, "xsize", 0),
            ny=self.ny or getattr(self, "ysize", 0),
            xcoord=xcoord,
            ycoord=ycoord,
        )
        return nml_obj.render() if nml_obj else ""

    def generate_unst_nml(self) -> str:
        """Generate UNST_NML namelist content as string."""
        nml_obj = self.unst
        return nml_obj.render() if nml_obj else ""

    def generate_smc_nml(self) -> str:
        """Generate SMC_NML namelist content as string."""
        nml_obj = self.smc
        return nml_obj.render() if nml_obj else ""

    def generate_depth_nml(self) -> str:
        """Generate DEPTH_NML namelist content as string."""
        nml_obj = self.depth
        return nml_obj.render() if nml_obj else ""

    def generate_mask_nml(self) -> str:
        """Generate MASK_NML namelist content as string."""
        nml_obj = self.mask
        return nml_obj.render() if nml_obj else ""

    def generate_obst_nml(self) -> str:
        """Generate OBST_NML namelist content as string."""
        nml_obj = self.obst
        return nml_obj.render() if nml_obj else ""

    def generate_slope_nml(self) -> str:
        """Generate SLOPE_NML namelist content as string."""
        nml_obj = self.slope
        return nml_obj.render() if nml_obj else ""

    def generate_sed_nml(self) -> str:
        """Generate SED_NML namelist content as string."""
        nml_obj = self.sed
        return nml_obj.render() if nml_obj else ""

    def get(self, destdir: Union[str, Path], *args, **kwargs) -> Dict[str, Any]:
        """Copy grid files to the destination directory and return namelist paths.

        This method copies all specified grid files to the staging directory
        and returns a dictionary with paths to the namelist files that need
        to be generated for the ww3_grid preprocessor.

        Args:
            destdir: Destination directory to copy the files
            *args: Additional arguments
            **kwargs: Additional keyword arguments

        Returns:
            Dictionary containing paths to generated namelist content
        """
        destdir = Path(destdir)
        destdir.mkdir(parents=True, exist_ok=True)

        # List of file attributes to copy
        file_attrs = [
            # Direct file paths (coordinate files, etc.)
            ("x_coord_file", "x_coord_file"),
            ("y_coord_file", "y_coord_file"),
            ("unst_obc_file", "unst_obc_file"),
        ]

        # Copy each file to destination if it exists
        for attr_name, _ in file_attrs:
            src_file = getattr(self, attr_name, None)
            if src_file:
                src_path = Path(src_file)
                dst_path = destdir / src_path.name
                if src_path.exists():
                    shutil.copy2(src_path, dst_path)
                    logger.info(f"Copied {src_path.name} to {destdir}")
                else:
                    raise FileNotFoundError(f"Source file does not exist: {src_path}")

        # Also copy files referenced in namelist objects
        namelist_file_attrs = [
            ("depth", "filename"),
            ("mask", "filename"),
            ("obst", "filename"),
            ("slope", "filename"),
            ("sed", "filename"),
            ("x_coord_file", None),  # Already handled above
            ("y_coord_file", None),  # Already handled above
        ]

        for attr_name, filename_attr in namelist_file_attrs:
            if attr_name in ["x_coord_file", "y_coord_file"]:
                continue  # Skip these as they're already handled

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

        # Get the namelist objects based on grid type and provided files
        namelist_objects = {
            "grid_nml": GRID_NML(
                name=self.name or "UNSET",
                nml="namelists.nml",
                type=self.grid_type,
                coord=self.coordinate_system,
                clos=self.grid_closure,
                zlim=self.zlim,
                dmin=self.dmin,
            ),
        }

        # Add grid type specific namelists
        if self.grid_type == "RECT":
            namelist_objects["rect_nml"] = Rect(
                nx=self.nx or getattr(self, "xsize", 0),
                ny=self.ny or getattr(self, "ysize", 0),
                sx=self.sx or self.dx if hasattr(self, "dx") else None,
                sy=self.sy or self.dy if hasattr(self, "dy") else None,
                sf=self.sf,
                x0=self.x0,
                y0=self.y0,
                sf0=self.sf0,
            )
        elif self.grid_type == "CURV":
            from rompy_ww3.namelists.curv import CoordData

            # Define coordinate objects if files are provided
            xcoord = None
            ycoord = None
            if self.x_coord_file:
                xcoord = CoordData(
                    filename=self.x_coord_file.name, sf=0.25, off=-0.5, idla=3
                )
            if self.y_coord_file:
                ycoord = CoordData(
                    filename=self.y_coord_file.name, sf=0.25, off=0.5, idla=3
                )

            namelist_objects["curv_nml"] = Curv(
                nx=self.nx or getattr(self, "xsize", 0),
                ny=self.ny or getattr(self, "ysize", 0),
                xcoord=xcoord,
                ycoord=ycoord,
            )
        elif self.grid_type == "UNST":
            namelist_objects["unst_nml"] = self.unst
        elif self.grid_type == "SMC":
            namelist_objects["smc_nml"] = self.smc

        # Add optional file-based namelists if objects are provided
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

        # Generate and write the namelist files to the destination
        namelist_content = {}
        for nml_name, nml_obj in namelist_objects.items():
            if nml_obj:
                # Use the render method of the namelist object
                nml_content = nml_obj.render()
                namelist_content[nml_name] = nml_content
                # Use the default naming scheme: ww3_grid_{nml_name}.nml
                filename = f"ww3_grid_{nml_name}.nml"

                with open(destdir / filename, "w") as f:
                    f.write(nml_content)

        logger.info(f"Copied all grid files to {destdir}")
        return namelist_content

    def write_grid_files(self, workdir: Path) -> None:
        """Write grid namelist files."""
        # Use the get method to handle file copying and namelist generation
        # This maintains consistency with the original design
        self.get(workdir)

    def get_template_context(self) -> dict:
        """Generate template context for Jinja2 templates.

        Returns:
            Dictionary containing grid parameters for templates.
        """
        return {
            "name": self.name,
            "grid_type": self.grid_type,
            "coordinate_system": self.coordinate_system,
            "grid_closure": self.grid_closure,
            "zlim": self.zlim,
            "dmin": self.dmin,
            "nx": self.nx,
            "ny": self.ny,
            "sx": self.sx,
            "sy": self.sy,
            "sf": self.sf,
            "x0": self.x0,
            "y0": self.y0,
            "x1": self.x1,
            "y1": self.y1,
            "grid_dimensions": self.grid_dimensions,
            "grid_spacing": self.grid_spacing,
            "grid_boundaries": self.grid_boundaries,
            "grid_area": self.calculate_grid_size(),
            # Include file paths for templates
            "depth_file": (
                self.depth.filename if self.depth and self.depth.filename else None
            ),
            "mask_file": (
                self.mask.filename if self.mask and self.mask.filename else None
            ),
            "obst_file": (
                self.obst.filename if self.obst and self.obst.filename else None
            ),
            "slope_file": (
                self.slope.filename if self.slope and self.slope.filename else None
            ),
            "sed_file": self.sed.filename if self.sed and self.sed.filename else None,
            "x_coord_file": self.x_coord_file.name if self.x_coord_file else None,
            "y_coord_file": self.y_coord_file.name if self.y_coord_file else None,
            "unst_obc_file": self.unst_obc_file.name if self.unst_obc_file else None,
        }
