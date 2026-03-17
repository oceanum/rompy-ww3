# PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-13 01:12:15
**Commit:** Unknown
**Branch:** main

## OVERVIEW

rompy-ww3 is a Python plugin for the rompy framework that provides WAVEWATCH III (WW3) ocean wave model configuration and execution capabilities. This is an unreleased, actively developed scientific modeling package.

## STRUCTURE

```
./
├── src/rompy_ww3/          # Main package with components, namelists, core modules
├── tests/                    # Comprehensive test suite with 15 test files
├── examples/                  # Usage examples including multi-grid configurations
├── docs/                      # MkDocs documentation with Material theme
├── regtests/                   # Regression test configurations and backends
├── docker/                     # WW3 model compilation and execution environment
└── .agents/                     # Agent configuration files
```

## WHERE TO LOOK

| Task                 | Location                     | Notes                                        |
| -------------------- | ---------------------------- | -------------------------------------------- |
| Core configuration   | `src/rompy_ww3/config.py`    | Main Config (ShelConfig) class               |
| WW3 namelists        | `src/rompy_ww3/namelists/`   | 47+ Pydantic models for all WW3 components   |
| Component processors | `src/rompy_ww3/components/`  | Shel, Grid, Multi, Ounf, etc.                |
| Data handling        | `src/rompy_ww3/core/data.py` | WW3DataBlob, WW3DataGrid, WW3Boundary        |
| Test infrastructure  | `tests/conftest.py`          | Auto data download, Docker detection         |
| CLI interface        | `src/rompy_ww3/cli.py`       | typer-based commands: init, run, create_grid |

## CODE MAP

| Symbol                | Type  | Location                | Refs       | Role                               |
| --------------------- | ----- | ----------------------- | ---------- | ---------------------------------- |
| ShelConfig            | Class | config.py               | Primary    | Main configuration interface       |
| Config                | Class | config.py               | Primary    | Alias for ShelConfig               |
| Domain                | Class | namelists/domain.py     | Core       | WW3 domain/timing configuration    |
| Input                 | Class | namelists/input.py      | Core       | WW3 input data configuration       |
| Shel                  | Class | components/shel.py      | Core       | WW3 shell model component          |
| Grid                  | Class | components/grid.py      | Core       | WW3 grid preprocessing component   |
| Multi                 | Class | components/multi.py     | Core       | Multi-grid configuration component |
| WW3ComponentBaseModel | Class | components/basemodel.py | Foundation | Base for all components            |
| Timesteps             | Class | namelists/timesteps.py  | Core       | Critical timestep validation       |

## CONVENTIONS

**Only deviations from standard Python patterns:**

- **Plugin Architecture**: Entry points defined in pyproject.toml (`rompy.config.ww3nml`)
- **WW3-Specific Validation**: 153+ ValueError instances enforcing timestep relationships, depth limits, and WW3 format constraints
- **Dual CI Systems**: Both GitHub Actions (modern) and Travis CI (legacy) maintained simultaneously
- **Test Data Auto-Download**: Tests automatically fetch data from GitHub releases
- **Docker-Aware Testing**: Conditional Docker execution based on CI environment
- **Namelist-Based Configuration**: Fortran-style namelist generation rather than typical Python config

## ANTI-PATTERNS (THIS PROJECT)

**Critical prohibitions for WW3 modeling:**

- **Backward Compatibility**: "Backward compatibility is NOT guaranteed" during development
- **Depth Constraints**: Points with depth > ZLIM "will never be wet points"
- **Timestep Relationships**: Must follow dtmax ≈ 3×dtxy, dtkth between dtmax/10 and dtmax/2
- **Mutually Exclusive Features**: "If a mask is defined, EXCL cannot be used"
- **Compiler Fixes**: "do not invoke a link step" in WW3 Docker compilation
- **Code Quality**: "must pass black formatting before commit or merge"
- **Boolean Format**: WW3 booleans must be 'T'/'F', not Python True/False

## UNIQUE STYLES

**Project-specific patterns:**

- **Component-Based Architecture**: Separate classes for each WW3 executable (ww3_shel, ww3_grid, ww3_multi)
- **Pydantic V2 Validation**: Extensive field validation with custom error messages
- **Template Generation**: Jinja2 templates with runtime variable substitution
- **Scientific Model Integration**: Direct integration with compiled WW3 Fortran model
- **Multi-Backend Execution**: Support for both local and Docker execution backends
- **Version Management**: tbump-based semantic versioning with automated git tagging
- **Comprehensive Testing**: 15 test files covering all components, minimal mocking usage

## COMMANDS

```bash
# Development Workflow
make test              # Run full test suite with pytest
make lint              # Code quality checks with ruff
make coverage          # Generate coverage report (HTML in htmlcov/)
make docs              # Build MkDocs documentation
make clean             # Clean build artifacts

# Testing - Single Tests/Modules
pytest tests/test_config.py                           # Single test file
pytest tests/test_config.py::test_grid_from_yaml      # Single test function
pytest tests/test_config.py::TestNMLConfig            # Single test class
pytest -k "grid"                                       # All tests matching "grid"
pytest -v                                              # Verbose output
pytest --pdb                                           # Drop into debugger on failure
pytest --lf                                            # Run last failed tests only
pytest --capture=no                                    # Show print() statements

# Code Quality
ruff check .                                           # Lint all files
ruff check --fix .                                     # Auto-fix issues
ruff format .                                          # Format code (black-compatible)
mypy src/rompy_ww3                                     # Type checking
pre-commit run --all-files                             # Run all pre-commit hooks

# CLI Commands
rompy_ww3 init         # Initialize new WW3 configuration
rompy_ww3 run          # Execute WW3 model run
rompy_ww3 create_grid  # Generate grid configuration
```

## CODE STYLE GUIDELINES

### Import Order
```python
# 1. Standard library
import os
from pathlib import Path
from typing import Optional, List, Dict, Literal

# 2. Third-party packages
import numpy as np
import xarray as xr
from pydantic import Field, field_validator, model_validator

# 3. Rompy framework
from rompy.core import RompyBaseModel

# 4. Local package
from rompy_ww3.namelists.basemodel import NamelistBaseModel
from rompy_ww3.core.types import TimeType
```

### Type Annotations
- **Always use type hints** for function parameters and return values
- Use `Optional[T]` for nullable types
- Use `Literal["value1", "value2"]` for restricted string choices
- Use `List[T]`, `Dict[K, V]` from typing (Python 3.9+ generics also acceptable)
- Pydantic models use `Field()` for metadata and validation

```python
def process_grid(
    depth: np.ndarray,
    mask: Optional[np.ndarray] = None,
    zlim: float = 0.5,
) -> Dict[str, np.ndarray]:
    """Process grid with optional mask."""
    ...
```

### Naming Conventions
- **Classes**: PascalCase (e.g., `ShelConfig`, `WW3DataGrid`)
- **Functions/methods**: snake_case (e.g., `create_grid`, `validate_timesteps`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_ZLIM`, `WW3_BOOLEAN_TRUE`)
- **Private attributes**: Leading underscore (e.g., `_template_env`)
- **Pydantic fields**: snake_case matching WW3 namelist parameters

### Error Handling
- **Raise ValueError** for validation errors with detailed messages explaining WW3 constraints
- Include parameter names, expected values, and actual values in error messages
- Use model validators (`@field_validator`, `@model_validator`) for Pydantic validation

```python
@field_validator("dtkth")
@classmethod
def validate_dtkth(cls, v: float, info) -> float:
    """Validate dtkth is between dtmax/10 and dtmax/2."""
    dtmax = info.data.get("dtmax")
    if dtmax is not None:
        if not (dtmax / 10 <= v <= dtmax / 2):
            raise ValueError(
                f"dtkth ({v}) must be between dtmax/10 ({dtmax/10}) "
                f"and dtmax/2 ({dtmax/2})"
            )
    return v
```

### Documentation
- **Docstrings**: Use Google-style docstrings for all public functions/classes
- **Type hints**: Required for all function signatures
- **Field descriptions**: Use `Field(description="...")` for Pydantic fields
- **Inline comments**: Explain WW3-specific constraints and non-obvious logic

```python
class Timesteps(NamelistBaseModel):
    """WW3 timestep configuration.
    
    Timesteps must follow critical relationships:
    - dtmax ≈ 3 × dtxy (CFL condition)
    - dtkth between dtmax/10 and dtmax/2
    """
    
    dtmax: float = Field(..., description="Maximum global time step (seconds)")
    dtxy: float = Field(..., description="Spatial propagation time step (seconds)")
```

### Testing Conventions
- **Test files**: `test_*.py` in `tests/` directory
- **Test functions**: `test_<functionality>` naming
- **Fixtures**: Define in `conftest.py` for reusability
- **Parametrize**: Use `@pytest.mark.parametrize` for multiple test cases
- **Assertions**: Prefer specific assertions (`assert x == y`) over generic ones

```python
@pytest.mark.parametrize(
    "dtmax,dtxy,valid",
    [
        (300, 100, True),   # dtmax = 3 × dtxy (valid)
        (300, 200, False),  # dtmax < 3 × dtxy (invalid)
    ],
)
def test_timestep_validation(dtmax, dtxy, valid):
    """Test timestep relationship validation."""
    if valid:
        Timesteps(dtmax=dtmax, dtxy=dtxy)
    else:
        with pytest.raises(ValueError):
            Timesteps(dtmax=dtmax, dtxy=dtxy)
```

### WW3-Specific Patterns
- **Booleans**: Use `'T'`/`'F'` strings, not Python `True`/`False`
- **Namelists**: Generate via Jinja2 templates in `templates/` directory
- **Component inheritance**: All components inherit from `WW3ComponentBaseModel`
- **Validation**: Extensive validation prevents WW3 model runtime failures
- **Entry points**: Register new config types in `pyproject.toml` under `rompy.config`

## NOTES

**Critical development considerations:**

1. **Unreleased Status**: API instability expected - prioritize clean interfaces over compatibility
2. **WW3 Model Dependencies**: Requires compiled WW3 6.07.1 binaries in PATH or WW3_DIR
3. **Scientific Validation**: Extensive parameter validation prevents model blow-up and stability issues
4. **Docker Environment**: Custom WW3 compilation with Gnu Fortran and MPI support
5. **Test Data**: Automatically downloaded from rompy-test-data GitHub releases
6. **Entry Points**: Plugin integrates with broader rompy framework via setuptools entry points

## RELATED PROJECTS

**Main Rompy Framework**: <https://github.com/rom-py/rompy>

- Core framework providing plugin architecture, data handling, and model execution backends
- Entry point system allowing plugins like rompy-ww3 to register configurations
- Comprehensive documentation and examples for ocean modeling workflows

**WW3 Source Code**: <https://github.com/NOAA-EMC/WW3/tree/develop/model>

- Official WAVEWATCH III Fortran model source code
- Reference implementation for namelist formats and parameter validation
- Development branch containing latest model features and improvements

**Integration Notes**:

- rompy-ww3 serves as Python interface to WW3 model capabilities
- Validation rules ensure compatibility with WW3 Fortran requirements
- Component architecture mirrors WW3 executable structure (ww3_shel, ww3_grid, etc.)
