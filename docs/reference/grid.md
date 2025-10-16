# Grid API Reference

The rompy-ww3 plugin provides separate grid classes for each WW3 grid type, following a clean architecture where users pass actual namelist objects directly instead of individual parameters.

## New Grid Architecture

Instead of a single generic `Grid` class, rompy-ww3 now provides specific classes for each grid type:

- `RectGrid` - Rectilinear grids
- `CurvGrid` - Curvilinear grids  
- `UnstGrid` - Unstructured grids
- `SmcGrid` - Spherical Multiple-Cell (SMC) grids

Each grid type accepts only the namelist objects relevant to that specific grid type, eliminating redundant parameters and validation complexity.

## Grid Classes

### RectGrid

::: rompy_ww3.grid.RectGrid
    handler: python
    options:
      show_root_heading: false
      show_root_toc_entry: false
      show_bases: true
      show_source: false

### CurvGrid

::: rompy_ww3.grid.CurvGrid
    handler: python
    options:
      show_root_heading: false
      show_root_toc_entry: false
      show_bases: true
      show_source: false

### UnstGrid

::: rompy_ww3.grid.UnstGrid
    handler: python
    options:
      show_root_heading: false
      show_root_toc_entry: false
      show_bases: true
      show_source: false

### SmcGrid

::: rompy_ww3.grid.SmcGrid
    handler: python
    options:
      show_root_heading: false
      show_root_toc_entry: false
      show_bases: true
      show_source: false

## Union Type

::: rompy_ww3.grid.AnyWw3Grid
    handler: python
    options:
      show_root_heading: false
      show_root_toc_entry: false
      show_bases: false
      show_source: false

## Usage Pattern

The new clean architecture eliminates redundant interfaces and provides direct access to full WW3 namelist objects:

```python
from rompy_ww3.grid import RectGrid
from rompy_ww3.namelists.grid import Grid as GRID_NML, Rect
from rompy_ww3.namelists.depth import Depth

# Create namelist objects with full API access
grid_nml = GRID_NML(
    name="Clean Implementation",
    nml="clean.nml",
    type="RECT",
    coord="SPHE",
    clos="SMPL",
    zlim=-0.2,
    dmin=3.0,
)

rect_nml = Rect(
    nx=300,
    ny=150,
    sx=0.1,
    sy=0.1,
    sf=1.5,
    x0=180.0,
    y0=20.0,
    sf0=2.0,
)

depth_nml = Depth(
    filename="/path/to/depth.dat",
    sf=0.002,
    idf=60,
    idla=2,
)

# Pass actual namelist objects directly - NO REDUNDANT PARAMETERS!
grid = RectGrid(
    grid_type="base",
    model_type="ww3_rect",
    grid_nml=grid_nml,    # Actual GRID_NML object
    rect_nml=rect_nml,    # Actual Rect object
    depth=depth_nml,     # Actual Depth object
)

# Generate namelist content directly
nml_content = grid.grid_nml.render()  # Direct call to render()
```