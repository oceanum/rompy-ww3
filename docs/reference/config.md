# Config API Reference

::: rompy_ww3.config.NMLConfig
    handler: python
    options:
      show_root_heading: true
      show_root_full_path: false
      show_object_full_path: false
      show_category_heading: true
      show_if_no_docstring: true
      show_signature_annotations: true
      signature_crossrefs: true
      separate_signature: true
      docstring_section_style: table
      members_order: source
      group_by_category: true
      show_submodules: false
      filters:
        - "!^_"  # Hide private members by default

## Usage

The Config class is the main entry point for configuring WW3 models in rompy-ww3. It accepts namelist objects directly and supports the new clean grid architecture.

### Basic Usage

```python
from rompy_ww3.config import Config
from rompy_ww3.grid import RectGrid
from rompy_ww3.namelists.grid import Grid as GRID_NML, Rect
from rompy_ww3.namelists.timesteps import Timesteps

# Create grid with direct namelist objects
grid = RectGrid(
    grid_type="base",
    model_type="ww3_rect",
    grid_nml=GRID_NML(
        name="Clean Grid",
        type="RECT",
        coord="SPHE",
        clos="SMPL",
        zlim=-0.2,
        dmin=3.0,
    ),
    rect_nml=Rect(
        nx=300,
        ny=150,
        sx=0.1,
        sy=0.1,
        sf=1.5,
        x0=180.0,
        y0=20.0,
        sf0=2.0,
    ),
)

# Create config with the clean grid architecture
config = Config(
    grid=grid,  # Accepts AnyWw3Grid union type
    timesteps=Timesteps(
        dt=1800.0,
        dtfield=3600.0,
        dtpoint=3600.0,
        dtmax=180.0,
        dtxy=60.0,
        dtkth=30.0,
        dtmin=10.0,
    ),
)
```

### Multi-Grid Support

```python
from rompy_ww3.config import Config
from rompy_ww3.grid import RectGrid, CurvGrid

# Create multiple grids of different types
rect_grid = RectGrid(
    grid_type="base",
    model_type="ww3_rect",
    grid_nml=GRID_NML(...),
    rect_nml=Rect(...),
)

curv_grid = CurvGrid(
    grid_type="base", 
    model_type="ww3_curv",
    grid_nml=GRID_NML(...),
    curv_nml=Curv(...),
    x_coord_file=Path("x_coords.dat"),
    y_coord_file=Path("y_coords.dat"),
)

# Config supports both single and multi-grid configurations
single_grid_config = Config(grid=rect_grid)
multi_grid_config = Config(grid=rect_grid, grids=[rect_grid, curv_grid])
```

### Direct Namelist Access

```python
# Access namelist objects directly through config
grid_nml_content = config.grid.grid_nml.render()
rect_nml_content = config.grid.rect_nml.render()

# Generate all namelists at once
all_namelists = config.render_namelists()
```