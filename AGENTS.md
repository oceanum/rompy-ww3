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
| Core configuration   | `src/rompy_ww3/config.py`    | Main Config and NMLConfig classes            |
| WW3 namelists        | `src/rompy_ww3/namelists/`   | 47+ Pydantic models for all WW3 components   |
| Component processors | `src/rompy_ww3/components/`  | Shel, Grid, Multi, Ounf, etc.                |
| Data handling        | `src/rompy_ww3/core/data.py` | WW3DataBlob, WW3DataGrid, WW3Boundary        |
| Test infrastructure  | `tests/conftest.py`          | Auto data download, Docker detection         |
| CLI interface        | `src/rompy_ww3/cli.py`       | typer-based commands: init, run, create_grid |

## CODE MAP

| Symbol                | Type  | Location                | Refs       | Role                               |
| --------------------- | ----- | ----------------------- | ---------- | ---------------------------------- |
| NMLConfig             | Class | config.py               | Primary    | Main configuration interface       |
| Config                | Class | config.py               | Primary    | Alias for NMLConfig                |
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
# Development
make test              # Run test suite
make lint              # Code quality checks with ruff
make coverage          # Generate coverage report
make docs              # Build MkDocs documentation
make clean              # Clean build artifacts

# CLI
rompy_ww3 init         # Initialize new WW3 configuration
rompy_ww3 run          # Execute WW3 model run
rompy_ww3 create_grid  # Generate grid configuration
```

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
