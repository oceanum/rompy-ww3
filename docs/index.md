# rompy-ww3

[![PyPI](https://img.shields.io/pypi/v/rompy-ww3.svg)](https://pypi.org/project/rompy-ww3/)
[![License](https://img.shields.io/github/license/rom-py/rompy-ww3)](https://github.com/rom-py/rompy-ww3/blob/main/LICENSE)

WAVEWATCH III (WW3) plugin for the rompy framework.

rompy-ww3 provides a clean, Pythonic interface for configuring and running WAVEWATCH III ocean wave models within the rompy ecosystem. It offers comprehensive support for WW3 namelists, grid configuration, data handling, and source definitions.

## Features

- **Clean Architecture**: Separate classes for each WW3 grid type (RectGrid, CurvGrid, UnstGrid, SmcGrid)
- **Namelist Objects**: Full WW3 namelist support with direct object passing (no redundant parameters)
- **Direct API Access**: Complete access to all WW3 namelist parameters through namelist objects
- **No Redundant Interfaces**: Eliminates wrapper methods that just return objects
- **Type Safety**: Union types for flexible grid handling
- **Modern Python**: Built with Pydantic V2 for validation and type hints

## Installation

```bash
pip install rompy-ww3
```

## Quick Start

```python
from rompy_ww3.config import Config
from rompy_ww3.grid import RectGrid
from rompy_ww3.namelists.grid import Grid as GRID_NML, Rect
from rompy_ww3.namelists.timesteps import Timesteps

# Create namelist objects with full API access
grid_nml = GRID_NML(
    name="My WW3 Grid",
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

# Create grid with direct namelist objects - CLEAN ARCHITECTURE!
grid = RectGrid(
    grid_type="base",
    model_type="ww3_rect",
    grid_nml=grid_nml,  # Pass actual GRID_NML object directly
    rect_nml=rect_nml,  # Pass actual Rect object directly
)

# Create config with the new grid architecture
config = Config(
    grid=grid,  # Accepts AnyWw3Grid union type (RectGrid, CurvGrid, etc.)
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

# Generate namelist content directly through namelist objects
grid_nml_content = config.grid.grid_nml.render()  # Direct call to render()
rect_nml_content = config.grid.rect_nml.render()   # Direct call to render()
```

## Key Features

### 1. **Separate Grid Classes**
Each WW3 grid type now has its own dedicated class:
- `RectGrid` for rectilinear grids
- `CurvGrid` for curvilinear grids
- `UnstGrid` for unstructured grids
- `SmcGrid` for SMC grids

### 2. **Direct Namelist Object Passing**
Users pass actual WW3 namelist objects directly instead of individual parameters:

```python
# CLEAN WAY (direct namelist objects):
grid = RectGrid(
    grid_nml=GRID_NML(  # Actual GRID_NML object
        name="Clean Grid",
        type="RECT",
        coord="SPHE",
        # All GRID_NML parameters in one object
    ),
    rect_nml=Rect(  # Actual Rect object
        nx=300,  # Part of Rect object
        ny=150,  # Part of Rect object
        # All Rect parameters in one object
    ),
    # NO REDUNDANT INDIVIDUAL PARAMETERS!
)
```

### 3. **No Redundant Interfaces**
Eliminates wrapper methods that just return objects:

```python
# CLEAN WAY (direct object access):
grid = RectGrid(...)
nml_content = grid.grid_nml.render()   # Direct call to render()
```

### 4. **Full API Access**
Complete access to all WW3 namelist parameters through namelist objects:

```python
# Access all namelist parameters directly:
print(grid.grid_nml.name)
print(grid.grid_nml.type)
print(grid.grid_nml.coord)
print(grid.rect_nml.nx)
print(grid.rect_nml.ny)
print(grid.depth.filename)
print(grid.depth.sf)
# ... and all other parameters directly through objects
```

## Documentation

- [Installation](installation.md)
- [API Reference](reference/grid.md)
- [Contributing](contributing.md)