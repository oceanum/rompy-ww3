"""Comprehensive tests for the new clean WW3 Grid architecture with separate classes per grid type."""

import tempfile
from pathlib import Path
from rompy_ww3.grid import RectGrid, CurvGrid, UnstGrid, SmcGrid, AnyWw3Grid
from rompy_ww3.namelists.grid import Grid as GRID_NML, Rect
from rompy_ww3.namelists.curv import Curv
from rompy_ww3.namelists.unst import Unst
from rompy_ww3.namelists.smc import Smc
from rompy_ww3.namelists.depth import Depth
from rompy_ww3.namelists.mask import Mask


def test_rect_grid_creation():
    """Test creation of RectGrid with direct namelist objects."""
    # Create namelist objects directly
    grid_nml = GRID_NML(
        name="Test Rect Grid",
        nml="rect_test.nml",
        type="RECT",
        coord="SPHE",
        clos="SMPL",
        zlim=-0.2,
        dmin=3.0,
    )

    rect_nml = Rect(
        nx=100,
        ny=50,
        sx=0.1,
        sy=0.1,
        sf=1.5,
        x0=-10.0,
        y0=20.0,
        sf0=2.0,
    )

    # Create temporary files for depth and mask
    with tempfile.NamedTemporaryFile(suffix=".dat", delete=False) as depth_file:
        depth_file.write(b"depth data")
        depth_file_path = Path(depth_file.name)

    with tempfile.NamedTemporaryFile(suffix=".dat", delete=False) as mask_file:
        mask_file.write(b"mask data")
        mask_file_path = Path(mask_file.name)

    # Create RectGrid with direct namelist objects
    grid = RectGrid(
        grid_type="base",  # From BaseGrid
        model_type="ww3_rect",  # From RectGrid
        grid_nml=grid_nml,
        rect_nml=rect_nml,
        depth=Depth(filename=str(depth_file_path), sf=0.002, idf=60, idla=2),
        mask=Mask(filename=str(mask_file_path), idf=70, idla=3),
    )

    # Verify the objects are stored directly without reconstruction
    assert grid.grid_nml is grid_nml
    assert grid.rect_nml is rect_nml
    # Note: depth and mask are new objects that contain the paths
    assert grid.depth.filename == str(depth_file_path)
    assert grid.mask.filename == str(mask_file_path)

    # Verify grid-specific properties
    assert grid.model_type == "ww3_rect"

    # Clean up
    depth_file_path.unlink()
    mask_file_path.unlink()


def test_curv_grid_creation():
    """Test creation of CurvGrid with direct namelist objects."""
    # Create temporary coordinate files (required for CurvGrid)
    with tempfile.NamedTemporaryFile(suffix=".dat", delete=False) as x_coord_file:
        x_coord_file.write(b"x coordinate data")
        x_coord_file_path = Path(x_coord_file.name)

    with tempfile.NamedTemporaryFile(suffix=".dat", delete=False) as y_coord_file:
        y_coord_file.write(b"y coordinate data")
        y_coord_file_path = Path(y_coord_file.name)

    # Create temporary depth file
    with tempfile.NamedTemporaryFile(suffix=".dat", delete=False) as depth_file:
        depth_file.write(b"depth data")
        depth_file_path = Path(depth_file.name)

    # Create namelist objects directly
    grid_nml = GRID_NML(
        name="Test Curv Grid",
        nml="curv_test.nml",
        type="CURV",
        coord="SPHE",
        clos="SMPL",
        zlim=-0.3,
        dmin=4.0,
    )

    curv_nml = Curv(
        nx=80,
        ny=40,
        # Other curv parameters would be defined here
    )

    # Create CurvGrid with direct namelist objects and coordinate files
    grid = CurvGrid(
        grid_type="base",
        model_type="ww3_curv",
        grid_nml=grid_nml,
        curv_nml=curv_nml,
        depth=Depth(filename=str(depth_file_path), sf=0.003, idf=80, idla=4),
        x_coord_file=x_coord_file_path,
        y_coord_file=y_coord_file_path,
    )

    # Verify the objects are stored directly
    assert grid.grid_nml is grid_nml
    assert grid.curv_nml is curv_nml
    assert grid.x_coord_file == x_coord_file_path
    assert grid.y_coord_file == y_coord_file_path

    # Verify grid-specific properties
    assert grid.model_type == "ww3_curv"

    # Clean up
    x_coord_file_path.unlink()
    y_coord_file_path.unlink()
    depth_file_path.unlink()


def test_unst_grid_creation():
    """Test creation of UnstGrid with direct namelist objects."""
    # Create namelist objects directly
    grid_nml = GRID_NML(
        name="Test Unst Grid",
        nml="unst_test.nml",
        type="UNST",
        coord="SPHE",
        clos="SMPL",
        zlim=-0.4,
        dmin=5.0,
    )

    unst_nml = Unst(
        filename="unst_grid.dat",
        sf=-1.0,
        idla=4,
        idfm=2,
        format="(20f10.2)",
        ugobcfile="obc.dat",
    )

    # Create temporary obc file
    with tempfile.NamedTemporaryFile(suffix=".dat", delete=False) as obc_file:
        obc_file.write(b"obc data")
        obc_file_path = Path(obc_file.name)

    # Create UnstGrid with direct namelist objects
    grid = UnstGrid(
        grid_type="base",
        model_type="ww3_unst",
        grid_nml=grid_nml,
        unst_nml=unst_nml,
        unst_obc_file=obc_file_path,
    )

    # Verify the objects are stored directly
    assert grid.grid_nml is grid_nml
    assert grid.unst_nml is unst_nml
    assert grid.unst_obc_file == obc_file_path

    # Verify grid-specific properties
    assert grid.model_type == "ww3_unst"

    # Clean up
    obc_file_path.unlink()


def test_smc_grid_creation():
    """Test creation of SmcGrid with direct namelist objects."""
    # Create namelist objects directly
    grid_nml = GRID_NML(
        name="Test SMC Grid",
        nml="smc_test.nml",
        type="SMC",
        coord="SPHE",
        clos="SMPL",
        zlim=-0.1,
        dmin=2.0,
    )

    smc_nml = Smc(
        # SMC-specific parameters
    )

    # Create SmcGrid with direct namelist objects
    grid = SmcGrid(
        grid_type="base",
        model_type="ww3_smc",
        grid_nml=grid_nml,
        smc_nml=smc_nml,
    )

    # Verify the objects are stored directly
    assert grid.grid_nml is grid_nml
    assert grid.smc_nml is smc_nml

    # Verify grid-specific properties
    assert grid.model_type == "ww3_smc"


def test_direct_namelist_access():
    """Test direct access to namelist objects and their parameters."""
    # Create temporary files
    with tempfile.NamedTemporaryFile(suffix=".dat", delete=False) as depth_file:
        depth_file.write(b"depth data")
        depth_file_path = Path(depth_file.name)

    # Create namelist objects with custom parameters
    grid_nml = GRID_NML(
        name="Direct Access Grid",
        nml="direct_access.nml",
        type="RECT",
        coord="CART",
        clos="NONE",
        zlim=-0.15,
        dmin=2.5,
    )

    rect_nml = Rect(
        nx=200,
        ny=100,
        sx=0.05,
        sy=0.05,
        sf=1.2,
        x0=150.0,
        y0=-10.0,
        sf0=1.8,
    )

    depth_nml = Depth(
        filename=str(depth_file_path),
        sf=0.001,
        idf=50,
        idla=1,
    )

    # Create grid with direct namelist objects
    grid = RectGrid(
        grid_type="base",
        model_type="ww3_rect",
        grid_nml=grid_nml,
        rect_nml=rect_nml,
        depth=depth_nml,
    )

    # Test direct access to namelist parameters
    assert grid.grid_nml.name == "Direct Access Grid"
    assert grid.grid_nml.coord == "CART"
    assert grid.grid_nml.clos == "NONE"
    assert grid.grid_nml.zlim == -0.15
    assert grid.grid_nml.dmin == 2.5

    assert grid.rect_nml.nx == 200
    assert grid.rect_nml.ny == 100
    assert grid.rect_nml.sx == 0.05
    assert grid.rect_nml.sy == 0.05
    assert grid.rect_nml.sf == 1.2
    assert grid.rect_nml.x0 == 150.0
    assert grid.rect_nml.y0 == -10.0
    assert grid.rect_nml.sf0 == 1.8

    assert grid.depth.filename == str(depth_file_path)
    assert grid.depth.sf == 0.001
    assert grid.depth.idf == 50
    assert grid.depth.idla == 1

    # Clean up
    depth_file_path.unlink()


def test_namelist_rendering():
    """Test that namelist objects render correctly through direct access."""
    # Create temporary files
    with tempfile.NamedTemporaryFile(suffix=".dat", delete=False) as depth_file:
        depth_file.write(b"depth data")
        depth_file_path = Path(depth_file.name)

    grid_nml = GRID_NML(
        name="Render Test Grid",
        nml="render_test.nml",
        type="RECT",
        coord="SPHE",
        clos="SMPL",
        zlim=-0.25,
        dmin=3.2,
    )

    rect_nml = Rect(
        nx=150,
        ny=75,
        sx=0.2,
        sy=0.2,
        sf=1.6,
        x0=-5.0,
        y0=40.0,
        sf0=2.2,
    )

    depth_nml = Depth(
        filename=str(depth_file_path),
        sf=0.0025,
        idf=65,
        idla=3,
    )

    # Create grid with direct namelist objects
    grid = RectGrid(
        grid_type="base",
        model_type="ww3_rect",
        grid_nml=grid_nml,
        rect_nml=rect_nml,
        depth=depth_nml,
    )

    # Test that namelists render correctly through direct access
    grid_nml_content = grid.grid_nml.render()
    rect_nml_content = grid.rect_nml.render()
    depth_nml_content = grid.depth.render()

    # Verify content contains expected values
    assert "Render Test Grid" in grid_nml_content
    assert "SPHE" in grid_nml_content
    assert "SMPL" in grid_nml_content
    assert "zlim = -0.25" in grid_nml_content or "GRID%ZLIM" in grid_nml_content
    assert "dmin = 3.2" in grid_nml_content or "GRID%DMIN" in grid_nml_content

    assert "150" in rect_nml_content  # nx
    assert "75" in rect_nml_content  # ny
    assert "0.2" in rect_nml_content  # sx, sy
    assert "1.6" in rect_nml_content  # sf
    assert "-5.0" in rect_nml_content  # x0
    assert "40.0" in rect_nml_content  # y0
    assert "2.2" in rect_nml_content  # sf0

    assert "0.0025" in depth_nml_content  # scale factor
    assert "65" in depth_nml_content  # IDF
    assert "3" in depth_nml_content  # IDLA

    # Clean up
    depth_file_path.unlink()


def test_file_operations():
    """Test file operations for each grid type."""
    # Test RectGrid with depth file
    with tempfile.NamedTemporaryFile(suffix=".dat", delete=False) as depth_file:
        depth_file.write(b"depth data")
        depth_file_path = Path(depth_file.name)

    with tempfile.NamedTemporaryFile(suffix=".dat", delete=False) as mask_file:
        mask_file.write(b"mask data")
        mask_file_path = Path(mask_file.name)

    rect_grid = RectGrid(
        grid_type="base",
        model_type="ww3_rect",
        grid_nml=GRID_NML(
            name="File Test Grid",
            type="RECT",
            coord="SPHE",
            clos="SMPL",
            zlim=-0.2,
            dmin=3.0,
        ),
        rect_nml=Rect(
            nx=50,
            ny=25,
            sx=0.1,
            sy=0.1,
            sf=1.0,
            x0=0.0,
            y0=0.0,
            sf0=1.5,
        ),
        depth=Depth(filename=str(depth_file_path), sf=0.002, idf=60, idla=2),
        mask=Mask(filename=str(mask_file_path), idf=70, idla=3),
    )

    # Test get method
    with tempfile.TemporaryDirectory() as temp_dir:
        dest_dir = Path(temp_dir)
        result = rect_grid.get(dest_dir)

        # Check that files were copied
        assert (dest_dir / depth_file_path.name).exists()
        assert (dest_dir / mask_file_path.name).exists()

        # Check that namelist files were created
        assert (dest_dir / "ww3_grid_grid_nml.nml").exists()
        assert (dest_dir / "ww3_grid_rect_nml.nml").exists()
        assert (dest_dir / "ww3_grid_depth_nml.nml").exists()
        assert (dest_dir / "ww3_grid_mask_nml.nml").exists()

        # Check that return value contains expected keys
        assert "grid_nml" in result
        assert "rect_nml" in result
        assert "depth_nml" in result
        assert "mask_nml" in result

    # Test CurvGrid with coordinate files
    with tempfile.NamedTemporaryFile(suffix=".dat", delete=False) as x_coord_file:
        x_coord_file.write(b"x coordinates")
        x_coord_file_path = Path(x_coord_file.name)

    with tempfile.NamedTemporaryFile(suffix=".dat", delete=False) as y_coord_file:
        y_coord_file.write(b"y coordinates")
        y_coord_file_path = Path(y_coord_file.name)

    # Create temporary depth file for CurvGrid
    with tempfile.NamedTemporaryFile(suffix=".dat", delete=False) as depth_file:
        depth_file.write(b"curv depth data")
        depth_file_path = Path(depth_file.name)

    curv_grid = CurvGrid(
        grid_type="base",
        model_type="ww3_curv",
        grid_nml=GRID_NML(
            name="Curv File Test Grid",
            type="CURV",
            coord="SPHE",
            clos="SMPL",
            zlim=-0.3,
            dmin=4.0,
        ),
        curv_nml=Curv(
            nx=40,
            ny=20,
        ),
        x_coord_file=x_coord_file_path,
        y_coord_file=y_coord_file_path,
        depth=Depth(filename=str(depth_file_path), sf=0.003, idf=65, idla=2),
    )

    # Test get method for CurvGrid
    with tempfile.TemporaryDirectory() as temp_dir:
        dest_dir = Path(temp_dir)
        result = curv_grid.get(dest_dir)

        # Check that coordinate files were copied
        assert (dest_dir / x_coord_file_path.name).exists()
        assert (dest_dir / y_coord_file_path.name).exists()

        # Check that namelist files were created
        assert (dest_dir / "ww3_grid_grid_nml.nml").exists()
        assert (dest_dir / "ww3_grid_curv_nml.nml").exists()

    # Clean up files
    depth_file_path.unlink()
    mask_file_path.unlink()
    x_coord_file_path.unlink()
    y_coord_file_path.unlink()


def test_union_type():
    """Test that the AnyWw3Grid union type works properly."""
    # Create RectGrid
    rect_grid = RectGrid(
        grid_type="base",
        model_type="ww3_rect",
        grid_nml=GRID_NML(
            name="Test Rect",
            type="RECT",
            coord="SPHE",
            clos="SMPL",
            zlim=-0.2,
            dmin=3.0,
        ),
        rect_nml=Rect(
            nx=100, ny=50, sx=0.1, sy=0.1, sf=1.5, x0=-10.0, y0=20.0, sf0=2.0
        ),
    )

    # Create CurvGrid - requires coordinate files
    with tempfile.NamedTemporaryFile(suffix=".dat", delete=False) as x_coord_file:
        x_coord_file.write(b"x coordinates")
        x_coord_file_path = Path(x_coord_file.name)

    with tempfile.NamedTemporaryFile(suffix=".dat", delete=False) as y_coord_file:
        y_coord_file.write(b"y coordinates")
        y_coord_file_path = Path(y_coord_file.name)

    curv_grid = CurvGrid(
        grid_type="base",
        model_type="ww3_curv",
        grid_nml=GRID_NML(
            name="Test Curv",
            type="CURV",
            coord="SPHE",
            clos="SMPL",
            zlim=-0.2,
            dmin=3.0,
        ),
        curv_nml=Curv(nx=80, ny=40),
        x_coord_file=x_coord_file_path,
        y_coord_file=y_coord_file_path,
    )

    unst_grid = UnstGrid(
        grid_type="base",
        model_type="ww3_unst",
        grid_nml=GRID_NML(
            name="Test Unst",
            type="UNST",
            coord="SPHE",
            clos="SMPL",
            zlim=-0.2,
            dmin=3.0,
        ),
        unst_nml=Unst(
            filename="test.dat",
            sf=-1.0,
            idla=4,
            idfm=2,
            format="(20f10.2)",
            ugobcfile="obc.dat",
        ),
    )

    smc_grid = SmcGrid(
        grid_type="base",
        model_type="ww3_smc",
        grid_nml=GRID_NML(
            name="Test SMC", type="SMC", coord="SPHE", clos="SMPL", zlim=-0.2, dmin=3.0
        ),
        smc_nml=Smc(),
    )

    # Test that all grid types can be used as AnyWw3Grid
    grids: list[AnyWw3Grid] = [rect_grid, curv_grid, unst_grid, smc_grid]

    for i, grid in enumerate(grids):
        # All grids should have grid_nml attribute
        assert hasattr(grid, "grid_nml")
        assert grid.grid_nml is not None
        assert "Test" in grid.grid_nml.name

        # Verify each grid has its specific attributes
        if grid.model_type == "ww3_rect":
            assert hasattr(grid, "rect_nml")
            assert grid.rect_nml is not None
        elif grid.model_type == "ww3_curv":
            assert hasattr(grid, "curv_nml")
            assert grid.curv_nml is not None
            assert hasattr(grid, "x_coord_file")
            assert hasattr(grid, "y_coord_file")
        elif grid.model_type == "ww3_unst":
            assert hasattr(grid, "unst_nml")
            assert grid.unst_nml is not None
        elif grid.model_type == "ww3_smc":
            assert hasattr(grid, "smc_nml")
            assert grid.smc_nml is not None

    # Clean up
    x_coord_file_path.unlink()
    y_coord_file_path.unlink()


def test_polymorphic_behavior():
    """Test that all grid types provide consistent interface for Config usage."""
    # Create grids with different types but similar functionality
    rect_grid = RectGrid(
        grid_type="base",
        model_type="ww3_rect",
        grid_nml=GRID_NML(
            name="Polymorphic Rect",
            type="RECT",
            coord="SPHE",
            clos="SMPL",
            zlim=-0.2,
            dmin=3.0,
        ),
        rect_nml=Rect(
            nx=100, ny=50, sx=0.1, sy=0.1, sf=1.5, x0=-10.0, y0=20.0, sf0=2.0
        ),
    )

    # Create CurvGrid with required coordinate files
    with tempfile.NamedTemporaryFile(suffix=".dat", delete=False) as x_coord_file:
        x_coord_file.write(b"x coordinates for curv")
        x_coord_file_path = Path(x_coord_file.name)

    with tempfile.NamedTemporaryFile(suffix=".dat", delete=False) as y_coord_file:
        y_coord_file.write(b"y coordinates for curv")
        y_coord_file_path = Path(y_coord_file.name)

    curv_grid = CurvGrid(
        grid_type="base",
        model_type="ww3_curv",
        grid_nml=GRID_NML(
            name="Polymorphic Curv",
            type="CURV",
            coord="SPHE",
            clos="SMPL",
            zlim=-0.2,
            dmin=3.0,
        ),
        curv_nml=Curv(nx=80, ny=40),
        x_coord_file=x_coord_file_path,
        y_coord_file=y_coord_file_path,
    )

    # Both should have the same basic interface
    grids = [rect_grid, curv_grid]

    for grid in grids:
        # All grids should have direct namelist object access
        assert hasattr(grid, "grid_nml")
        assert grid.grid_nml is not None
        assert hasattr(grid, "get")

        # Test get method functionality
        with tempfile.TemporaryDirectory() as temp_dir:
            dest_dir = Path(temp_dir)
            result = grid.get(dest_dir)
            # Should return a dictionary with namelist content
            assert isinstance(result, dict)
            # Should contain at least grid_nml
            assert "grid_nml" in result

    # Clean up
    x_coord_file_path.unlink()
    y_coord_file_path.unlink()


if __name__ == "__main__":
    test_rect_grid_creation()
    test_curv_grid_creation()
    test_unst_grid_creation()
    test_smc_grid_creation()
    test_direct_namelist_access()
    test_namelist_rendering()
    test_file_operations()
    test_union_type()
    test_polymorphic_behavior()
    print("All new grid architecture tests passed!")
