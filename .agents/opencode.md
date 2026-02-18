# Project Context for OpenCode

This document provides essential context for OpenCode to assist with tasks in the `/home/tdurrant/source/rompy/rompy-meta/repos/rompy-ww3` directory.

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
# Old way (avoid):
config = Config(
    domain_start="20230101 000000",
    domain_stop="20230107 000000",
    domain_iostyp=1
)

# New way (preferred):
config = Config(
    domain=Domain(
        start="20230101 000000",
        stop="20230107 000000",
        iostyp=1
    )
)
```

### 3. **Complete Namelist Coverage**

The plugin includes implementations for all major WW3 namelist components:

- **DOMAIN_NML**: Domain definition and model timing
- **INPUT_NML**: Input data configuration for single-grid models
- **INPUT_GRID_NML**: Input grid specification for multi-grid models
- **MODEL_GRID_NML**: Model grid specification for multi-grid models
- **OUTPUT_TYPE_NML**: Output field specifications
- **OUTPUT_DATE_NML**: Output timing configuration
- And many more...

## Code Style and Standards

- **Formatter**: Use `black` for code formatting
- **Pre-commit**: All code must pass pre-commit hooks
- **Type Hints**: Use proper type annotations throughout
- **Pydantic V2**: All configuration classes use Pydantic V2 models
- **Documentation**: Use docstrings for all public APIs

## Development Guidelines

1. **Prefer Explicit over Implicit**: Make configuration and APIs explicit rather than magical
2. **No Legacy Support**: Don't maintain compatibility with old patterns during active development
3. **Direct Access**: Provide direct access to WW3 namelist parameters without wrapper abstractions
4. **Type Safety**: Use union types and proper Pydantic models for flexible but safe APIs
5. **Modular Design**: Keep components focused and composable

## File Structure

```
src/
├── rompy_ww3/
│   ├── __init__.py
│   ├── config.py          # Main configuration classes
│   ├── grid.py           # Grid implementations
│   ├── data.py           # Data handling classes
│   ├── source.py         # Data source implementations
│   └── namelists/        # Namelist Pydantic models
│       ├── __init__.py
│       ├── domain.py
│       ├── input.py
│       └── ... (other namelist files)
examples/
├── basic_ww3_run.py      # Basic usage examples
└── multi_grid_example.py # Multi-grid configuration examples
```

## Key APIs

### Main Config Class
```python
from rompy_ww3.config import Config

config = Config(
    domain=Domain(...),
    input_nml=Input(...),
    # ... other namelist objects
)
```

### Grid Classes
```python
from rompy_ww3.grid import RectGrid, CurvGrid, UnstGrid, SmcGrid

grid = RectGrid(
    nx=100,
    ny=50,
    dx=0.1,
    dy=0.1,
    # ... other grid parameters
)
```

### Template Context Generation
```python
# Generate context for template rendering
context = config.get_template_context()
```

## Testing and Validation

- All namelist objects should validate against WW3 specifications
- Use Pydantic validators for complex constraints
- Integration tests should cover common configuration scenarios
- Examples should be kept up-to-date with API changes

## Working with OpenCode

When working on this project:

1. **Always read existing code patterns** before implementing new features
2. **Follow the direct namelist passing architecture** - don't add wrapper methods
3. **Use proper type annotations** for all public APIs
4. **Run `black`** on any code changes before committing
5. **Test configurations** with actual WW3 namelist validation
6. **Update examples** when making API changes
7. **Prioritize clean code** over backward compatibility

Remember: This is active development - architectural improvements are encouraged even if they require breaking changes!