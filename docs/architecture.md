# Architecture

## Overview

rompy-ww3 follows a clean, modular architecture designed to provide direct access to WAVEWATCH III (WW3) namelist functionality while maintaining type safety and ease of use.

## Key Principles

### 1. **Direct Namelist Object Passing**
Users pass actual WW3 namelist objects directly to grid classes. This eliminates redundant interfaces and provides full access to the complete WW3 API.

### 2. **Separate Classes Per Grid Type**
Each WW3 grid type has its own dedicated class:
- `RectGrid` - Rectilinear grids
- `CurvGrid` - Curvilinear grids  
- `UnstGrid` - Unstructured grids
- `SmcGrid` - Spherical Multiple-Cell (SMC) grids

### 3. **No Redundant Validation**
Grid classes no longer validate individual parameters or reconstruct namelist objects. Users create namelist objects directly with full API access.

### 4. **Union Types for Flexibility**
The `AnyWw3Grid` union type allows Config to accept any grid type while maintaining type safety.

## Clean Architecture Benefits

### Elimination of Redundant Interfaces
Wrapper methods that just return objects are eliminated in favor of direct object access:

```python
# DIRECT ACCESS - CLEAN WAY
class RectGrid:
    grid_nml: GRID_NML  # Actual namelist object

# Usage:
grid = RectGrid(grid_nml=GRID_NML(...))
content = grid.grid_nml.render()   # Direct call to render()
```

### No Parameter Reconstruction
Namelist objects are passed directly rather than being reconstructed from individual parameters:

```python
# DIRECT NAMelist OBJECT PASSING - CLEAN WAY
class RectGrid:
    def __init__(self, grid_nml: GRID_NML, rect_nml: Rect, ...):
        # Store actual namelist objects directly
        self.grid_nml = grid_nml  # Actual GRID_NML object
        self.rect_nml = rect_nml  # Actual Rect object
        # ... other namelist objects
        
    def generate_grid_nml(self):
        # NO RECONSTRUCTION - just use the passed object!
        return self.grid_nml.render()
```

## Component Structure

### Namelists
Full WW3 namelist implementations that can be used independently or with rompy-ww3 grid classes.

### Grid Classes
Thin wrappers that store and provide access to relevant namelist objects for each grid type.

### Config Class
Main configuration class that orchestrates WW3 model setup using the clean grid architecture.

### Union Types
Type-safe way to handle multiple grid types in a single interface.

## Usage Patterns

### 1. Standalone Namelist Usage
```python
from rompy_ww3.namelists.grid import Grid as GRID_NML, Rect

# Create namelist objects directly
grid_nml = GRID_NML(
    name="Standalone Grid",
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

# Generate namelist content directly
grid_content = grid_nml.render()
rect_content = rect_nml.render()
```

### 2. Grid Class Usage
```python
from rompy_ww3.grid import RectGrid
from rompy_ww3.namelists.grid import Grid as GRID_NML, Rect

# Create namelist objects
grid_nml = GRID_NML(...)
rect_nml = Rect(...)

# Pass namelist objects directly to grid
grid = RectGrid(
    grid_type="base",
    model_type="ww3_rect",
    grid_nml=grid_nml,  # Pass actual objects directly
    rect_nml=rect_nml,  # No parameter reconstruction!
)

# Generate content directly through namelist objects
content = grid.grid_nml.render()  # Direct access
```

### 3. Config Integration
```python
from rompy_ww3.config import Config
from rompy_ww3.grid import RectGrid

# Create grid with namelist objects
grid = RectGrid(
    grid_nml=GRID_NML(...),
    rect_nml=Rect(...),
)

# Config accepts any grid type through union type
config = Config(
    grid=grid,  # AnyWw3Grid union type
)

# Generate all namelist content
namelists = config.render_namelists()
```

## Grid Classes

### RectGrid
Rectilinear grid implementation with direct namelist object access.

#### Usage
```python
from rompy_ww3.grid import RectGrid
from rompy_ww3.namelists.grid import Grid as GRID_NML, Rect
from rompy_ww3.namelists.depth import Depth

grid = RectGrid(
    grid_type="base",
    model_type="ww3_rect",
    grid_nml=GRID_NML(
        name="Rectilinear Grid",
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
    depth=Depth(
        filename="/path/to/depth.dat",
        sf=0.002,
        idf=60,
        idla=2,
    ),
)
```

### CurvGrid
Curvilinear grid implementation with direct namelist object access.

#### Usage
```python
from rompy_ww3.grid import CurvGrid
from rompy_ww3.namelists.grid import Grid as GRID_NML
from rompy_ww3.namelists.curv import Curv

grid = CurvGrid(
    grid_type="base",
    model_type="ww3_curv",
    grid_nml=GRID_NML(
        name="Curvilinear Grid",
        type="CURV",
        coord="SPHE",
        clos="SMPL",
        zlim=-0.3,
        dmin=4.0,
    ),
    curv_nml=Curv(
        nx=200,
        ny=100,
    ),
    x_coord_file=Path("/path/to/x_coords.dat"),
    y_coord_file=Path("/path/to/y_coords.dat"),
)
```

### UnstGrid
Unstructured grid implementation with direct namelist object access.

#### Usage
```python
from rompy_ww3.grid import UnstGrid
from rompy_ww3.namelists.grid import Grid as GRID_NML
from rompy_ww3.namelists.unst import Unst

grid = UnstGrid(
    grid_type="base",
    model_type="ww3_unst",
    grid_nml=GRID_NML(
        name="Unstructured Grid",
        type="UNST",
        coord="SPHE",
        clos="SMPL",
        zlim=-0.15,
        dmin=2.5,
    ),
    unst_nml=Unst(
        filename="unst_grid.dat",
        sf=-1.0,
        idla=4,
        idfm=2,
        format="(20f10.2)",
        ugobcfile="obc.dat",
    ),
    unst_obc_file=Path("/path/to/obc.dat"),
)
```

### SmcGrid
Spherical Multiple-Cell (SMC) grid implementation with direct namelist object access.

#### Usage
```python
from rompy_ww3.grid import SmcGrid
from rompy_ww3.namelists.grid import Grid as GRID_NML
from rompy_ww3.namelists.smc import Smc

grid = SmcGrid(
    grid_type="base",
    model_type="ww3_smc",
    grid_nml=GRID_NML(
        name="SMC Grid",
        type="SMC",
        coord="SPHE",
        clos="SMPL",
        zlim=-0.1,
        dmin=2.0,
    ),
    smc_nml=Smc(),
)
```

## Union Type

### AnyWw3Grid
Union type that allows Config to accept any grid type while maintaining type safety:

```python
from rompy_ww3.grid import RectGrid, CurvGrid, UnstGrid, SmcGrid, AnyWw3Grid

# All grid types can be used with the union type
grids: list[AnyWw3Grid] = [
    RectGrid(...),
    CurvGrid(...),
    UnstGrid(...),
    SmcGrid(...),
]

# Config accepts AnyWw3Grid
config = Config(grid=RectGrid(...))  # Works with any grid type
```