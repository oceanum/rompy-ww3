"""Comprehensive tests for Config class integration with new grid architecture."""

import tempfile
from pathlib import Path
from rompy_ww3.config import Config
from rompy_ww3.grid import RectGrid
from rompy_ww3.namelists.grid import Grid as GRID_NML, Rect
from rompy_ww3.namelists.timesteps import Timesteps
from rompy_ww3.namelists.depth import Depth


def test_config_with_new_grid():
    """Test Config class with the new grid architecture."""
    # Create required timesteps object
    timesteps = Timesteps(
        dt=1800.0,
        dtfield=3600.0,
        dtpoint=3600.0,
        dtmax=180.0,
        dtxy=60.0,
        dtkth=30.0,
        dtmin=10.0,
    )

    # Create grid with direct namelist objects
    grid = RectGrid(
        grid_type="base",
        model_type="ww3_rect",
        grid_nml=GRID_NML(
            name="Config Integration Grid",
            nml="config_integration.nml",
            type="RECT",
            coord="SPHE",
            clos="SMPL",
            zlim=-0.2,
            dmin=3.0,
        ),
        rect_nml=Rect(
            nx=100,
            ny=50,
            sx=0.1,
            sy=0.1,
            sf=1.5,
            x0=-10.0,
            y0=20.0,
            sf0=2.0,
        ),
    )

    # Create config with new grid architecture
    config = Config(
        grid=grid,
        timesteps=timesteps,
    )

    # Verify that config can access grid namelist objects directly
    assert config.grid is not None
    assert config.grid.grid_nml is not None
    assert config.grid.rect_nml is not None
    assert config.grid.grid_nml.name == "Config Integration Grid"
    assert config.grid.rect_nml.nx == 100
    assert config.grid.rect_nml.ny == 50


def test_config_render_namelists_with_new_grid():
    """Test Config.render_namelists() with the new grid architecture."""
    # Create required timesteps object
    timesteps = Timesteps(
        dt=1800.0,
        dtfield=3600.0,
        dtpoint=3600.0,
        dtmax=180.0,
        dtxy=60.0,
        dtkth=30.0,
        dtmin=10.0,
    )

    # Create grid with direct namelist objects
    with tempfile.NamedTemporaryFile(suffix=".dat", delete=False) as depth_file:
        depth_file.write(b"depth data")
        depth_file_path = Path(depth_file.name)

    grid = RectGrid(
        grid_type="base",
        model_type="ww3_rect",
        grid_nml=GRID_NML(
            name="Render Namelists Grid",
            nml="render_namelists.nml",
            type="RECT",
            coord="SPHE",
            clos="SMPL",
            zlim=-0.25,
            dmin=2.8,
        ),
        rect_nml=Rect(
            nx=200,
            ny=100,
            sx=0.05,
            sy=0.05,
            sf=1.2,
            x0=150.0,
            y0=-10.0,
            sf0=1.8,
        ),
        depth=Depth(
            filename=str(depth_file_path),
            sf=0.0015,
            idf=55,
            idla=1,
        ),
    )

    # Create config
    config = Config(
        grid=grid,
        timesteps=timesteps,
    )

    # Test render_namelists method
    namelists = config.render_namelists()

    # Check that expected namelist files are generated
    assert "timesteps.nml" in namelists
    assert "grid.nml" in namelists
    assert "rect.nml" in namelists

    # Verify content contains expected values from the direct namelist objects
    assert "Render Namelists Grid" in namelists["grid.nml"]
    assert "SPHE" in namelists["grid.nml"]
    assert "SMPL" in namelists["grid.nml"]
    assert (
        "zlim = -0.25" in namelists["grid.nml"] or "GRID%ZLIM" in namelists["grid.nml"]
    )
    assert "dmin = 2.8" in namelists["grid.nml"] or "GRID%DMIN" in namelists["grid.nml"]

    assert "200" in namelists["rect.nml"]  # nx
    assert "100" in namelists["rect.nml"]  # ny
    assert "0.05" in namelists["rect.nml"]  # sx, sy
    assert "1.2" in namelists["rect.nml"]  # sf
    assert "150.0" in namelists["rect.nml"]  # x0
    assert "-10.0" in namelists["rect.nml"]  # y0
    assert "1.8" in namelists["rect.nml"]  # sf0

    assert "180.0" in namelists["timesteps.nml"]  # dtmax

    # Clean up
    if depth_file_path.exists():
        depth_file_path.unlink()


def test_config_integration_with_file_generation():
    """Test Config integration with new grid architecture for file generation."""
    # Create required timesteps object
    timesteps = Timesteps(
        dt=1800.0,
        dtfield=3600.0,
        dtpoint=3600.0,
        dtmax=180.0,
        dtxy=60.0,
        dtkth=30.0,
        dtmin=10.0,
    )

    # Create grid with direct namelist objects
    grid = RectGrid(
        grid_type="base",
        model_type="ww3_rect",
        grid_nml=GRID_NML(
            name="Integration Test Grid",
            nml="integration_test.nml",
            type="RECT",
            coord="SPHE",
            clos="SMPL",
            zlim=-0.3,
            dmin=3.5,
        ),
        rect_nml=Rect(
            nx=150,
            ny=75,
            sx=0.1,
            sy=0.1,
            sf=1.5,
            x0=0.0,
            y0=0.0,
            sf0=2.0,
        ),
    )

    # Create config
    config = Config(
        grid=grid,
        timesteps=timesteps,
    )

    # Test the __call__ method which generates WW3 control files
    with tempfile.TemporaryDirectory() as temp_dir:
        runtime_mock = type("Runtime", (), {"staging_dir": temp_dir})()
        result = config(runtime_mock)

        # Check that the expected directories were created
        assert Path(result["staging_dir"]).exists()
        assert Path(result["namelists_dir"]).exists()

        # Verify that WW3 control files were created
        namelists_dir = Path(result["namelists_dir"])
        shel_file = namelists_dir / "ww3_shel.nml"
        grid_file = namelists_dir / "ww3_grid.nml"
        bound_file = namelists_dir / "ww3_bound.nml"

        assert shel_file.exists()
        assert grid_file.exists()
        assert bound_file.exists()

        # Check content of grid file contains grid-specific namelists from the grid object
        with open(grid_file, "r") as f:
            grid_content = f.read()
            assert "GRID_NML" in grid_content
            assert "RECT_NML" in grid_content
            assert "Integration Test Grid" in grid_content
            assert "SPHE" in grid_content
            assert "SMPL" in grid_content
            assert "150" in grid_content  # nx from grid object
            assert "75" in grid_content  # ny from grid object


def test_config_with_multiple_grid_types():
    """Test that Config can work with different grid types through the union type."""
    from rompy_ww3.grid import CurvGrid, UnstGrid, SmcGrid
    from rompy_ww3.namelists.curv import Curv
    from rompy_ww3.namelists.unst import Unst
    from rompy_ww3.namelists.smc import Smc

    # Create required timesteps object
    timesteps = Timesteps(
        dt=1800.0,
        dtfield=3600.0,
        dtpoint=3600.0,
        dtmax=180.0,
        dtxy=60.0,
        dtkth=30.0,
        dtmin=10.0,
    )

    # Test with RectGrid
    rect_grid = RectGrid(
        grid_type="base",
        model_type="ww3_rect",
        grid_nml=GRID_NML(
            name="Rect Config Test",
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

    rect_config = Config(
        grid=rect_grid,
        timesteps=timesteps,
    )

    assert rect_config.grid.model_type == "ww3_rect"
    assert rect_config.grid.grid_nml.name == "Rect Config Test"

    # Test with CurvGrid - requires coordinate files
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
            name="Curv Config Test",
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

    curv_config = Config(
        grid=curv_grid,
        timesteps=timesteps,
    )

    assert curv_config.grid.model_type == "ww3_curv"
    assert curv_config.grid.grid_nml.name == "Curv Config Test"

    # Test with UnstGrid
    unst_grid = UnstGrid(
        grid_type="base",
        model_type="ww3_unst",
        grid_nml=GRID_NML(
            name="Unst Config Test",
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

    unst_config = Config(
        grid=unst_grid,
        timesteps=timesteps,
    )

    assert unst_config.grid.model_type == "ww3_unst"
    assert unst_config.grid.grid_nml.name == "Unst Config Test"

    # Clean up coordinate files
    x_coord_file_path.unlink()
    y_coord_file_path.unlink()


def test_config_direct_access_to_grid_objects():
    """Test that Config provides direct access to grid namelist objects."""
    # Create required timesteps object
    timesteps = Timesteps(
        dt=1800.0,
        dtfield=3600.0,
        dtpoint=3600.0,
        dtmax=180.0,
        dtxy=60.0,
        dtkth=30.0,
        dtmin=10.0,
    )

    # Create grid with direct namelist objects
    grid_nml = GRID_NML(
        name="Direct Access Config Grid",
        nml="direct_access_config.nml",
        type="RECT",
        coord="CART",
        clos="NONE",
        zlim=-0.15,
        dmin=2.5,
    )

    rect_nml = Rect(
        nx=250,
        ny=125,
        sx=0.02,
        sy=0.02,
        sf=1.1,
        x0=175.0,
        y0=25.0,
        sf0=1.6,
    )

    grid = RectGrid(
        grid_type="base",
        model_type="ww3_rect",
        grid_nml=grid_nml,
        rect_nml=rect_nml,
    )

    # Create config
    config = Config(
        grid=grid,
        timesteps=timesteps,
    )

    # Test direct access to grid namelist objects through config
    assert config.grid.grid_nml is grid_nml
    assert config.grid.rect_nml is rect_nml

    # Verify that we can access all parameters directly
    assert config.grid.grid_nml.name == "Direct Access Config Grid"
    assert config.grid.grid_nml.coord == "CART"
    assert config.grid.grid_nml.clos == "NONE"
    assert config.grid.grid_nml.zlim == -0.15
    assert config.grid.grid_nml.dmin == 2.5

    assert config.grid.rect_nml.nx == 250
    assert config.grid.rect_nml.ny == 125
    assert config.grid.rect_nml.sx == 0.02
    assert config.grid.rect_nml.sy == 0.02
    assert config.grid.rect_nml.sf == 1.1
    assert config.grid.rect_nml.x0 == 175.0
    assert config.grid.rect_nml.y0 == 25.0
    assert config.grid.rect_nml.sf0 == 1.6


if __name__ == "__main__":
    test_config_with_new_grid()
    test_config_render_namelists_with_new_grid()
    test_config_integration_with_file_generation()
    test_config_with_multiple_grid_types()
    test_config_direct_access_to_grid_objects()
    print("All Config integration tests passed!")
