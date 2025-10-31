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
- **Component-Based Architecture**: Dedicated component models for each WW3 control file
- **Enhanced Validation**: Comprehensive validation for all WW3 namelist parameters
- **Detailed Documentation**: Complete documentation for every WW3 parameter with usage examples

## Installation

```bash
pip install rompy-ww3
```

## Quick Start

### Grid Configuration
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

# Create grid with direct namelist objects
grid = RectGrid(
    grid_type="base",
    model_type="ww3_rect",
    grid_nml=grid_nml,  # Pass actual GRID_NML object directly
    rect_nml=rect_nml,  # Pass actual Rect object directly
)

# Create config with grid architecture
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

### Component-Based Architecture
```python
from rompy_ww3.config import Config
from rompy_ww3.components import Shel, Grid
from rompy_ww3.namelists import Domain, Input, Spectrum, Run, Timesteps

# Create components with namelist objects
shell = Shel(
    domain=Domain(start="20230101 000000", stop="20230107 000000"),
    input_nml=Input(forcing={"winds": "T", "water_levels": "T"})
)

grid = Grid(
    spectrum=Spectrum(xfr=1.1, freq1=0.04, nk=25, nth=24),
    run=Run(fldry=False, flcx=True, flcy=True),
    timesteps=Timesteps(dtmax=1800.0, dtxy=600.0, dtmin=10.0)
)

# Create config with components
config = Config(
    ww3_shel=shell,  # Dedicated component for ww3_shel.nml
    ww3_grid=grid,   # Dedicated component for ww3_grid.nml
)

# Generate all namelist files directly
result = config(runtime=your_runtime_object)

# Generate template context for use in templates
context = config.get_template_context()
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
# Direct namelist objects:
grid = RectGrid(
    grid_nml=GRID_NML(  # Actual GRID_NML object
        name="Grid",
        type="RECT",
        coord="SPHE",
        # All GRID_NML parameters in one object
    ),
    rect_nml=Rect(  # Actual Rect object
        nx=300,  # Part of Rect object
        ny=150,  # Part of Rect object
        # All Rect parameters in one object
    ),
    # No redundant individual parameters!
)
```

### 3. **No Redundant Interfaces**
Eliminates wrapper methods that just return objects:

```python
# Direct object access:
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

### 5. **Component-Based Architecture**
Dedicated component models for each WW3 control file:

- `Shel` → `ww3_shel.nml` (Main model configuration)
- `Grid` → `ww3_grid.nml` (Grid preprocessing configuration)
- `Multi` → `ww3_multi.nml` (Multi-grid model configuration)
- `Bound` → `ww3_bound.nml` (Boundary preprocessing configuration)
- `Bounc` → `ww3_bounc.nml` (Boundary update configuration)
- `Prnc` → `ww3_prnc.nml` (Field preprocessing configuration)
- `Trnc` → `ww3_trnc.nml` (Track output configuration)
- `Ounf` → `ww3_ounf.nml` (Field output configuration)
- `Ounp` → `ww3_ounp.nml` (Point output configuration)
- `Uptstr` → `ww3_upstr.nml` (Restart update configuration)
- `Namelists` → `namelists.nml` (Model parameters configuration)

See [Component Architecture Documentation](architecture.md) for detailed information.

## Documentation

- [Installation](installation.md)
- [Architecture](architecture.md)
- [Namelist Documentation](namelists.md)
- [Validation Features](validation.md)
- [API Reference](reference/grid.md)
- [API Reference - Components](reference/components.md)
- [Contributing](contributing.md)