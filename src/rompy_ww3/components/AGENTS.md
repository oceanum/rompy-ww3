# COMPONENTS KNOWLEDGE BASE

**Generated:** 2026-01-13 01:12:15
**Commit:** Unknown
**Branch:** main

## OVERVIEW
WW3 processing components providing Fortran namelist generation, file rendering, and shell execution integration for all WW3 executables.

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Component base | `basemodel.py` | WW3ComponentBaseModel with render/write_nml methods |
| Shell configuration | `shel.py` | Main WW3 shell component (ww3_shel.nml) |
| Grid preprocessing | `grid.py` | Grid preprocessing component (ww3_grid.nml) |
| Multi-grid setup | `multi.py` | Multi-grid configuration (ww3_multi.nml) |
| Field preprocessing | `prnc.py` | Field data preprocessing (ww3_prnc.nml) |
| Field output | `ounf.py` | NetCDF field output (ww3_ounf.nml) |
| Point output | `ounp.py` | Point location output (ww3_ounp.nml) |
| Boundary processing | `bound.py` | Boundary preprocessing (ww3_bound.nml) |
| Boundary updates | `bounc.py` | Multi-grid boundary updates (ww3_bounc.nml) |
| Track output | `trnc.py` | Track point output (ww3_trnc.nml) |

## CONVENTIONS

**Component-specific patterns:**

- **Rendering Pipeline**: All components inherit from WW3ComponentBaseModel with standardized render() and write_nml() methods
- **Namelist Generation**: Components wrap multiple Pydantic namelist objects into single executable configurations
- **Automatic Naming**: nml_filename property generates standard WW3 filenames (e.g., ww3_shel.nml)
- **Command Integration**: run_cmd property constructs executable commands with proper WW3_DIR handling
- **Symbolic Links**: Prnc component creates symbolic links for variable-specific namelists (ww3_prnc.{var} -> ww3_prnc.nml)
- **Multi-Grid Rendering**: Multi component uses custom render() method with proper index formatting for MODEL(1)% fields
- **File Generation**: write_nml() creates directories and renders content with proper newline handling
- **Validation Integration**: Components include cross-namelist validation (e.g., Grid closure validation)
- **Boolean Conversion**: process_value() converts Python bool to Fortran 'T'/'F' format

## ANTI-PATTERNS (COMPONENTS)

**Critical prohibitions for WW3 components:**

- **Missing Final Newline**: Empty content would break prnc - fixed by always appending final newline in render()
- **Incorrect Grid Closure**: 360-degree longitude grids MUST use clos='SMPL' - auto-enforced by Grid component
- **Prnc Filename Mismatch**: Variable-specific namelists require symbolic links to standard name
- **Multi-Grid Field Names**: MODEL% fields must be converted to MODEL(1)% indexed format
- **Inconsistent Run Commands**: Components MUST use lowercase class names in run_cmd construction
- **Missing Prepend Commands**: Prnc component requires symbolic link setup before execution
- **File Extension Mismatches**: Component filenames must match WW3 executable naming exactly