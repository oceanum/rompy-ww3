"""WW3 Rompy grid."""

import logging
from pathlib import Path
from typing import Literal, Optional, Union, Dict, Any
from pydantic import Field, model_validator
import shutil

from rompy.core.grid import RegularGrid


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

    # Grid file definitions - optional, to be copied to staging directory
    # For RECT and CURV grids
    depth_file: Optional[Path] = Field(
        default=None,
        description="Path to depth file for RECT/CURV grids, will be copied to staging directory",
    )
    mask_file: Optional[Path] = Field(
        default=None,
        description="Path to mask file for RECT/CURV grids, will be copied to staging directory",
    )
    obst_file: Optional[Path] = Field(
        default=None,
        description="Path to obstruction file for RECT/CURV grids, will be copied to staging directory",
    )
    slope_file: Optional[Path] = Field(
        default=None,
        description="Path to slope file for RECT/CURV grids, will be copied to staging directory",
    )
    sed_file: Optional[Path] = Field(
        default=None,
        description="Path to sediment file for RECT/CURV grids, will be copied to staging directory",
    )

    # For CURV grids - coordinate files
    x_coord_file: Optional[Path] = Field(
        default=None,
        description="Path to x-coordinate file for CURV grids, will be copied to staging directory",
    )
    y_coord_file: Optional[Path] = Field(
        default=None,
        description="Path to y-coordinate file for CURV grids, will be copied to staging directory",
    )

    # For UNST grids
    unst_file: Optional[Path] = Field(
        default=None,
        description="Path to unstructured grid file for UNST grids, will be copied to staging directory",
    )
    unst_obc_file: Optional[Path] = Field(
        default=None,
        description="Path to additional boundary list file for UNST grids, will be copied to staging directory",
    )

    # For SMC grids
    mcels_file: Optional[Path] = Field(
        default=None,
        description="Path to MCels file for SMC grids, will be copied to staging directory",
    )
    iside_file: Optional[Path] = Field(
        default=None,
        description="Path to ISide file for SMC grids, will be copied to staging directory",
    )
    jside_file: Optional[Path] = Field(
        default=None,
        description="Path to JSide file for SMC grids, will be copied to staging directory",
    )
    subtr_file: Optional[Path] = Field(
        default=None,
        description="Path to Subtr file for SMC grids, will be copied to staging directory",
    )
    bundy_file: Optional[Path] = Field(
        default=None,
        description="Path to Bundy file for SMC grids, will be copied to staging directory",
    )
    mbarc_file: Optional[Path] = Field(
        default=None,
        description="Path to MBArc file for SMC grids, will be copied to staging directory",
    )
    aisid_file: Optional[Path] = Field(
        default=None,
        description="Path to AISid file for SMC grids, will be copied to staging directory",
    )
    ajsid_file: Optional[Path] = Field(
        default=None,
        description="Path to AJSid file for SMC grids, will be copied to staging directory",
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
            "depth_file",
            "mask_file",
            "obst_file",
            "slope_file",
            "sed_file",
            "x_coord_file",
            "y_coord_file",
            "unst_file",
            "unst_obc_file",
            "mcels_file",
            "iside_file",
            "jside_file",
            "subtr_file",
            "bundy_file",
            "mbarc_file",
            "aisid_file",
            "ajsid_file",
        ]

        for attr_name in file_attrs:
            file_path = getattr(self, attr_name, None)
            if file_path and not Path(file_path).exists():
                raise ValueError(f"File does not exist: {file_path}")

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
            Approximate grid area or None if boundaries are not defined.
        """
        if self.x0 is None or self.x1 is None or self.y0 is None or self.y1 is None:
            return None

        if self.coordinate_system == "SPHE":
            # Approximate area calculation for spherical coordinates (in square degrees)
            return (self.x1 - self.x0) * (self.y1 - self.y0)
        else:
            # Cartesian coordinates (in square meters or whatever units are used)
            return (self.x1 - self.x0) * (self.y1 - self.y0)

    def generate_grid_nml(self) -> str:
        """Generate GRID_NML namelist content."""
        lines = []
        lines.append("! Generated by rompy-ww3")
        lines.append("&GRID_NML")

        if self.name:
            lines.append(f"  GRID%NAME              =  '{self.name}'")
        lines.append(f"  GRID%NML               =  'namelists.nml'")
        if self.grid_type:
            lines.append(f"  GRID%TYPE              =  '{self.grid_type}'")
        if self.coordinate_system:
            lines.append(f"  GRID%COORD             =  '{self.coordinate_system}'")
        if self.grid_closure:
            lines.append(f"  GRID%CLOS              =  '{self.grid_closure}'")
        if self.zlim is not None:
            lines.append(f"  GRID%ZLIM              =  {self.zlim}")
        if self.dmin is not None:
            lines.append(f"  GRID%DMIN              =  {self.dmin}")

        lines.append("/")
        return "\n".join(lines)

    def generate_rect_nml(self) -> str:
        """Generate RECT_NML namelist content."""
        lines = []
        lines.append("! Generated by rompy-ww3")
        lines.append("&RECT_NML")

        if self.nx is not None:
            lines.append(f"  RECT%NX                =  {self.nx}")
        if self.ny is not None:
            lines.append(f"  RECT%NY                =  {self.ny}")
        if self.sx is not None:
            lines.append(f"  RECT%SX                =  {self.sx}")
        elif self.dx is not None:  # Using dx from parent class as sx
            lines.append(f"  RECT%SX                =  {self.dx}")
        if self.sy is not None:
            lines.append(f"  RECT%SY                =  {self.sy}")
        elif self.dy is not None:  # Using dy from parent class as sy
            lines.append(f"  RECT%SY                =  {self.dy}")
        if self.sf is not None:
            lines.append(f"  RECT%SF                =  {self.sf}")
        if self.x0 is not None:
            lines.append(f"  RECT%X0                =  {self.x0}")
        if self.y0 is not None:
            lines.append(f"  RECT%Y0                =  {self.y0}")
        if hasattr(self, "sf0") and self.sf0 is not None:
            lines.append(f"  RECT%SF0               =  {self.sf0}")

        lines.append("/")
        return "\n".join(lines)

    def generate_curv_nml(self) -> str:
        """Generate CURV_NML namelist content."""
        lines = []
        lines.append("! Generated by rompy-ww3")
        lines.append("&CURV_NML")

        if self.nx is not None:
            lines.append(f"  CURV%NX               =  {self.nx}")
        if self.ny is not None:
            lines.append(f"  CURV%NY               =  {self.ny}")

        # Add coordinate file configurations if they exist
        if self.x_coord_file:
            lines.append(f"  CURV%XCOORD%FILENAME   = '{self.x_coord_file.name}'")
            lines.append(f"  CURV%XCOORD%SF         = 0.25")
            lines.append(f"  CURV%XCOORD%OFF        = -0.5")
            lines.append(f"  CURV%XCOORD%IDLA       = 3")
        if self.y_coord_file:
            lines.append(f"  CURV%YCOORD%FILENAME   = '{self.y_coord_file.name}'")
            lines.append(f"  CURV%YCOORD%SF         = 0.25")
            lines.append(f"  CURV%YCOORD%OFF        = 0.5")
            lines.append(f"  CURV%YCOORD%IDLA       = 3")

        lines.append("/")
        return "\n".join(lines)

    def generate_unst_nml(self) -> str:
        """Generate UNST_NML namelist content."""
        lines = []
        lines.append("! Generated by rompy-ww3")
        lines.append("&UNST_NML")

        if self.unst_file:
            lines.append(f"  UNST%FILENAME       = '{self.unst_file.name}'")
        if self.unst_obc_file:
            lines.append(f"  UNST%UGOBCFILE      = '{self.unst_obc_file.name}'")

        # Set default parameters for unstructured grid
        lines.append(f"  UNST%SF             = -1.")
        lines.append(f"  UNST%IDLA           = 4")
        lines.append(f"  UNST%IDFM           = 2")
        lines.append(f"  UNST%FORMAT         = '(20f10.2)'")

        lines.append("/")
        return "\n".join(lines)

    def generate_smc_nml(self) -> str:
        """Generate SMC_NML namelist content."""
        lines = []
        lines.append("! Generated by rompy-ww3")
        lines.append("&SMC_NML")

        if self.mcels_file:
            lines.append(f"  SMC%MCELS%FILENAME       = '{self.mcels_file.name}'")
        if self.iside_file:
            lines.append(f"  SMC%ISIDE%FILENAME       = '{self.iside_file.name}'")
        if self.jside_file:
            lines.append(f"  SMC%JSIDE%FILENAME       = '{self.jside_file.name}'")
        if self.subtr_file:
            lines.append(f"  SMC%SUBTR%FILENAME       = '{self.subtr_file.name}'")
        if self.bundy_file:
            lines.append(f"  SMC%BUNDY%FILENAME       = '{self.bundy_file.name}'")
        if self.mbarc_file:
            lines.append(f"  SMC%MBARC%FILENAME       = '{self.mbarc_file.name}'")
        if self.aisid_file:
            lines.append(f"  SMC%AISID%FILENAME       = '{self.aisid_file.name}'")
        if self.ajsid_file:
            lines.append(f"  SMC%AJSID%FILENAME       = '{self.ajsid_file.name}'")

        lines.append("/")
        return "\n".join(lines)

    def generate_depth_nml(self) -> str:
        """Generate DEPTH_NML namelist content."""
        if not self.depth_file:
            return ""

        lines = []
        lines.append("! Generated by rompy-ww3")
        lines.append("&DEPTH_NML")

        lines.append(f"  DEPTH%SF             = 0.001")
        lines.append(f"  DEPTH%FILENAME       = '{self.depth_file.name}'")
        lines.append(f"  DEPTH%IDF            = 50")
        lines.append(f"  DEPTH%IDLA           = 1")

        lines.append("/")
        return "\n".join(lines)

    def generate_mask_nml(self) -> str:
        """Generate MASK_NML namelist content."""
        if not self.mask_file:
            return ""

        lines = []
        lines.append("! Generated by rompy-ww3")
        lines.append("&MASK_NML")

        lines.append(f"  MASK%FILENAME         = '{self.mask_file.name}'")
        lines.append(f"  MASK%IDF              = 60")
        lines.append(f"  MASK%IDLA             = 1")

        lines.append("/")
        return "\n".join(lines)

    def generate_obst_nml(self) -> str:
        """Generate OBST_NML namelist content."""
        if not self.obst_file:
            return ""

        lines = []
        lines.append("! Generated by rompy-ww3")
        lines.append("&OBST_NML")

        lines.append(f"  OBST%SF              = 0.0001")
        lines.append(f"  OBST%FILENAME        = '{self.obst_file.name}'")
        lines.append(f"  OBST%IDF             = 70")
        lines.append(f"  OBST%IDLA            = 1")

        lines.append("/")
        return "\n".join(lines)

    def generate_slope_nml(self) -> str:
        """Generate SLOPE_NML namelist content."""
        if not self.slope_file:
            return ""

        lines = []
        lines.append("! Generated by rompy-ww3")
        lines.append("&SLOPE_NML")

        lines.append(f"  SLOPE%SF             = 0.0001")
        lines.append(f"  SLOPE%FILENAME       = '{self.slope_file.name}'")
        lines.append(f"  SLOPE%IDF            = 80")
        lines.append(f"  SLOPE%IDLA           = 1")

        lines.append("/")
        return "\n".join(lines)

    def generate_sed_nml(self) -> str:
        """Generate SED_NML namelist content."""
        if not self.sed_file:
            return ""

        lines = []
        lines.append("! Generated by rompy-ww3")
        lines.append("&SED_NML")

        lines.append(f"  SED%FILENAME         = '{self.sed_file.name}'")
        lines.append(f"  SED%IDFM             = 2")
        lines.append(f"  SED%FORMAT           = '(f10.6)'")

        lines.append("/")
        return "\n".join(lines)

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
            ("depth_file", "depth_file"),
            ("mask_file", "mask_file"),
            ("obst_file", "obst_file"),
            ("slope_file", "slope_file"),
            ("sed_file", "sed_file"),
            ("x_coord_file", "x_coord_file"),
            ("y_coord_file", "y_coord_file"),
            ("unst_file", "unst_file"),
            ("unst_obc_file", "unst_obc_file"),
            ("mcels_file", "mcels_file"),
            ("iside_file", "iside_file"),
            ("jside_file", "jside_file"),
            ("subtr_file", "subtr_file"),
            ("bundy_file", "bundy_file"),
            ("mbarc_file", "mbarc_file"),
            ("aisid_file", "aisid_file"),
            ("ajsid_file", "ajsid_file"),
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
                    logger.warning(f"Source file does not exist: {src_path}")

        # Return a dictionary of namelist content
        namelist_content = {
            "grid_nml": self.generate_grid_nml(),
            "rect_nml": self.generate_rect_nml() if self.grid_type == "RECT" else "",
            "curv_nml": self.generate_curv_nml() if self.grid_type == "CURV" else "",
            "unst_nml": self.generate_unst_nml() if self.grid_type == "UNST" else "",
            "smc_nml": self.generate_smc_nml() if self.grid_type == "SMC" else "",
            "depth_nml": self.generate_depth_nml(),
            "mask_nml": self.generate_mask_nml(),
            "obst_nml": self.generate_obst_nml(),
            "slope_nml": self.generate_slope_nml(),
            "sed_nml": self.generate_sed_nml(),
        }

        # Write the grid namelist files to the destination
        for nml_name, nml_content in namelist_content.items():
            if nml_content:  # Only write if there's content
                with open(destdir / f"ww3_grid_{nml_name}", "w") as f:
                    f.write(nml_content)

        logger.info(f"Copied all grid files to {destdir}")
        return namelist_content

    def write_grid_files(self, workdir: Path) -> None:
        """Write grid namelist files."""
        self.get(
            workdir
        )  # Use the get method to handle file copying and namelist generation

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
            "depth_file": self.depth_file.name if self.depth_file else None,
            "mask_file": self.mask_file.name if self.mask_file else None,
            "obst_file": self.obst_file.name if self.obst_file else None,
            "x_coord_file": self.x_coord_file.name if self.x_coord_file else None,
            "y_coord_file": self.y_coord_file.name if self.y_coord_file else None,
            "unst_file": self.unst_file.name if self.unst_file else None,
            "mcels_file": self.mcels_file.name if self.mcels_file else None,
        }
