# Project Context for Qwen Code

This document provides essential context for Qwen Code to assist with tasks in the `/home/tdurrant/source/rompy/rompy-ww3` directory.

## Project Overview

This is a **Python code project**. The project is a plugin for the **rompy** framework, specifically designed to integrate with the **WAVEWATCH III (WW3)** ocean wave model.

The main goal of rompy is to streamline the setup, configuration, execution, and analysis of coastal ocean models. This plugin (`rompy-ww3`) provides the necessary components to configure and run WW3 models using rompy's architecture.

**⚠️ IMPORTANT**: This is an **unreleased project** under active development. There is **no requirement to maintain backward compatibility** - changes should strongly favor clean interfaces and architectural improvements over maintaining legacy compatibility.

Key characteristics:

- **Language**: Python
- **Framework**: Built on the `rompy` core library.
- **Purpose**: Provides configuration, data handling, grids, and source definitions specific to the WAVEWATCH III (WW3) model within the rompy ecosystem.
- **Modularity**: Uses a plugin architecture where this package registers its components (like `Config`) with the main rompy framework.
- **Templating**: Uses a namelist render method from a base class (similar to rompy-schism) for generating model configuration files.

## Project Status

✅ **ACTIVE DEVELOPMENT - UNRELEASED**

This project is currently under active development and has not yet been released. All development decisions should prioritize:

1. **Clean Architecture** - Favor simplicity and clarity over backward compatibility
2. **Direct API Access** - Provide complete access to WW3 namelist functionality
3. **No Redundant Interfaces** - Eliminate wrapper methods that just return objects
4. **Type Safety** - Use union types and proper typing for flexibility
5. **Modern Python** - Leverage Pydantic V2 and modern Python features

**Backward compatibility is NOT a concern** - feel free to make breaking changes to improve the architecture.

## Current Clean Architecture

The project has been refactored to use a **clean, direct namelist object passing** architecture:

### 1. **Separate Grid Classes Per Grid Type**

Instead of a single generic Grid class, there are now specific classes for each WW3 grid type:

- `RectGrid` - Rectilinear grids
- `CurvGrid` - Curvilinear grids
- `UnstGrid` - Unstructured grids
- `SmcGrid` - Spherical Multiple-Cell (SMC) grids

### 2. **Direct Namelist Object Passing**

Users pass actual WW3 namelist objects directly instead of individual parameters:

```python
# CLEAN WAY - Direct namelist objects
from rompy_ww3.grid import RectGrid
from rompy_ww3.namelists.grid import Grid as GRID_NML, Rect

grid = RectGrid(
    grid=GRID_NML(      # Actual GRID_NML object
        name="Clean Grid",
        type="RECT",
        coord="SPHE",
        # ... all GRID_NML parameters
    ),
    rect=Rect(          # Actual Rect object
        nx=300,
        ny=150,
        sx=0.1,
        # ... all Rect parameters
    ),
    # NO REDUNDANT INDIVIDUAL PARAMETERS!
)
```

### 3. **No Redundant Validation or Reconstruction**

Grid classes no longer validate individual parameters or reconstruct namelist objects. Users create namelist objects directly with full API access.

### 4. **Direct Object Access**

Grid classes store and provide direct access to namelist objects:

```python
# DIRECT ACCESS - No wrapper methods!
content = grid.grid.render()   # Direct call to render()
content = grid.rect.render()    # Direct call to render()
```

### 5. **Union Types for Flexibility**

The `AnyWw3Grid` union type allows Config to accept any grid type:

```python
from rompy_ww3.config import NMLConfig
from rompy_ww3.grid import RectGrid, CurvGrid, UnstGrid, SmcGrid, AnyWw3Grid

# Config accepts AnyWw3Grid union type
config = NMLConfig(ww3_grid=RectGrid(...))   # Works with any grid type
config = NMLConfig(ww3_grid=CurvGrid(...))   # Works with any grid type
```

## Project Structure

- `src/rompy_ww3/`: Main source code directory.
  - `__init__.py`: Package initialization, defines version.
  - `cli.py`: Command-line interface using `typer`.
  - `config.py`: WW3-specific configuration class (`NMLConfig`), inherits from `rompy.core.config.BaseConfig`.
  - `grid.py`: WW3-specific grid classes (`RectGrid`, `CurvGrid`, `UnstGrid`, `SmcGrid`, `AnyWw3Grid`).
  - `data.py`: WW3-specific data handling class (`Data`), inherits from `rompy.core.data.DataGrid`.
  - `source.py`: WW3-specific data source definition (`Ww3Source`), inherits from `rompy.core.source.SourceBase`.
  - `namelists/`: Directory containing WW3 namelist configuration classes.
  - `templates/`: Directory containing templates for generating WW3 model input files.
- `tests/`: Comprehensive test suite covering the new clean architecture.
- `docs/`: Documentation reflecting the current clean architecture.
- `pyproject.toml`: Project metadata, dependencies, build system configuration, and entry points.
- `README.md`: Project introduction, features, and basic usage information.
- `Makefile`: Defines common development tasks (linting, testing, building, documentation).
- `requirements_dev.txt`: Development dependencies.

## Actual Implementation Details

### Config Architecture
- Main config class is `NMLConfig` which creates an alias `Config = NMLConfig` for backward compatibility
- Contains multiple component fields for different WW3 namelist files:
  - `ww3_shel`: Shell component (ww3_shel.nml)
  - `ww3_grid`: Grid component (ww3_grid.nml)
  - `multi_component`: Multi-grid component (ww3_multi.nml)
  - `ww3_bounc`: Boundary component (ww3_bounc.nml)
  - `ww3_prnc`: Field preprocessor component (ww3_prnc.nml)
  - `ww3_track`: Track component (ww3_trnc.nml)
  - `ww3_ounf`: Field output component (ww3_ounf.nml)
  - `ww3_ounp`: Point output component (ww3_ounp.nml)
  - `ww3_upstr`: Restart update component (ww3_uprstr.nml)
  - `namelists`: Namelists component (namelists.nml)
- Implements template context generation and namelist rendering
- Includes automatic synchronization between component parameters (e.g., forcing parameters between shell and preprocessor)

### Namelist System
- Extensive collection of WW3 namelist implementations in `src/rompy_ww3/namelists/`
- Each namelist class inherits from `NamelistBaseModel`
- Proper Fortran-style namelist formatting
- Nested object support for complex WW3 configurations

### Grid System
- Specific grid classes for each WW3 grid type (RectGrid, CurvGrid, UnstGrid, SmcGrid)
- Each grid class stores required and optional namelist objects
- Direct access to namelist rendering methods
- Grid-specific file handling (coordinate files, depth files, etc.)

## Building, Running, and Development

### Key Commands (from `Makefile` and `README.md`)

- **Install**: `pip install -e .` (for development) or `pip install .`. Development dependencies are in `requirements_dev.txt`.
- **Linting**: `make lint` or `ruff check .` (uses `ruff`). Pre-commit hooks are configured for formatting (`black`) and linting.
- **Testing**: `make test` or `pytest`. Tests are run in the virtualenv located in `.venv` at the root of the directory.
- **Documentation**: `make docs` (uses Sphinx).
- **Build Package**: `make dist` (creates source and wheel distributions).
- **Release**: `make release` (uploads to PyPI using `twine`). Versioning is managed by `tbump`.

### Code Formatting and Pre-commit Hooks

This project enforces code formatting using `black` via pre-commit hooks.

1. Install pre-commit: `pip install pre-commit`
2. Install hooks: `pre-commit install`
3. Manual run: `pre-commit run --all-files`

### Versioning and Release

Versioning is managed by `tbump`.

- Command: `tbump <new_version>`
- Configuration: `tbump.toml` and `src/rompy_ww3/__init__.py`.

## Development Conventions

- **Clean Architecture First** - Always favor clean interfaces over backward compatibility
- **No Legacy Constraints** - Feel free to make breaking changes to improve the design
- **Follows standard Python packaging conventions** (`src` layout).
- **Uses `pydantic`** for configuration validation.
- **Uses `typer`** for CLI.
- **Uses `ruff`** for linting and `black` for formatting.
- **Uses `pytest`** for testing in the `.venv` virtual environment.
- **Uses `mkdocs`** for documentation.
- **Uses a namelist render method** from a base class for generating model configuration files.
- **Uses `Makefile`** for common development tasks.

## Related Projects

- **rompy**: The core framework. Source code is at <https://github.com/rom-py/rompy>. Can be accessed with the "rompy Docs" mcp tool"
- **rompy-swan**: Plugin for the SWAN wave model. Source code is at <https://github.com/rom-py/rompy-swan>. Can be accessed with the "rompy-swan Docs" mcp tool.
- **rompy-schism**: Plugin for the SCHISM ocean model. Source code is at <https://github.com/rom-py/rompy-schism"
- WW3 model. Source code of the WAVEWATCH III model is at <https://github.com/NOAA-EMC/WW3/tree/develop>.  Can be accessed with the "WW3 Docs" mcp tool.

## Development Philosophy

### Clean Architecture Principles

1. **Direct Namelist Object Passing** - Users pass actual WW3 namelist objects directly
2. **No Redundant Interfaces** - Eliminate wrapper methods that just return objects
3. **Full API Access** - Complete access to all WW3 namelist parameters through namelist objects
4. **Type Safety** - Union types for flexible grid handling
5. **Simple Validation** - No complex validation logic

### Backward Compatibility Policy

**NONE REQUIRED** - This is an unreleased project under active development. Feel free to make breaking changes to improve the architecture.

### Clean Interface Priority

All changes should strongly favor clean interfaces over maintaining backward compatibility:

✅ **DO**:

- Simplify complex APIs
- Remove redundant methods
- Improve type safety
- Enhance direct access to functionality
- Make breaking changes to improve design

❌ **DON'T**:

- Maintain legacy interfaces just for compatibility
- Add complexity to support old patterns
- Compromise clean design for backward compatibility

## Current Implementation Status

### ✅ **Completed Components**

1. **Namelist System**:
   - Comprehensive set of WW3 namelist configuration classes
   - Direct object passing instead of parameter reconstruction
   - Full WW3 namelist API access
   - Proper Fortran-style namelist formatting
   - Nested object handling for WW3 namelists like `FORCING%FIELD%WINDS`

2. **Grid Architecture**:
   - Separate classes for each grid type (`RectGrid`, `CurvGrid`, `UnstGrid`, `SmcGrid`)
   - Direct namelist object passing (no individual parameters)
   - No redundant validation or reconstruction logic
   - Direct object access through namelist objects
   - Union type support (`AnyWw3Grid`)

3. **Configuration System**:
   - Integration with new clean grid architecture
   - Direct namelist object access through config
   - No redundant wrapper methods
   - Full API access to all namelist parameters

4. **Testing**:
   - Comprehensive test suite (78 tests passing)
   - Tests for new clean grid architecture
   - Tests for Config integration with new grid types
   - No obsolete tests for old architecture

5. **Documentation**:
   - Clean documentation reflecting current architecture
   - No references to old way or before/after comparisons
   - Focus on current clean approach only
   - Examples showing direct namelist object passing

### 🚀 **Ready for Continued Development**

The foundation is now in place for continued development with a clean, modern architecture that:

- Provides direct access to full WW3 namelist API
- Eliminates redundant interfaces and validation
- Uses union types for flexible grid handling
- Maintains type safety
- Follows clean architecture principles
- Has no backward compatibility constraints

Continue development with confidence that the architecture is clean and ready for enhancement!