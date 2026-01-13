# PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-13 01:12:15
**Commit:** Unknown
**Branch:** main

## OVERVIEW
Pydantic models for WAVEWATCH III namelist components with 145+ validation constraints and Fortran-style rendering.

## STRUCTURE
```
src/rompy_ww3/namelists/
├── basemodel.py         # NamelistBaseModel with render/serialize utilities
├── namelist.py          # Central imports for 30+ namelist classes
├── validation.py        # WW3-specific validation functions and constants
├── domain.py           # DOMAIN_NML with timing and multi-grid parameters
├── timesteps.py        # TIMESTEPS_NML with critical CFL validation
├── input.py            # INPUT_NML forcing configuration (F/T/H/C flags)
└── [33 additional component files]
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Core base class | `basemodel.py` | NamelistBaseModel with Fortran rendering |
| Validation patterns | `validation.py` | 17 validation functions, WW3 constants |
| Critical constraints | `timesteps.py` | dtmax ≈ 3×dtxy, dtkth between dtmax/10-2 |
| Forcing configuration | `input.py` | F/T/H/C flag system for all forcings |
| Field validation | All files | 145 ValueError instances with specific constraints |

## CONVENTIONS

**WW3-specific patterns:**

- **Fortran Boolean Format**: Booleans converted to 'T'/'F' strings via `boolean_to_string()`
- **Namelist Mapping**: Class names mapped to _NML suffixes via `get_namelist_name()`
- **Date Validation**: All dates converted to 'YYYYMMDD HHMMSS' format
- **Field Processing**: Special handling for VAR(1), VAR(2), VAR(3) array indexing
- **Recursive Rendering**: Nested objects processed with path-based prefixes

## ANTI-PATTERNS

**WW3 modeling prohibitions:**

- **Timestep Relationships**: dtmax must be ≈ 3×dtxy (±10%), dtkth must be between dtmax/10 and dtmax/2
- **Grid Minimums**: Grid dimensions must be ≥3×3, smaller sizes prohibited
- **Depth Constraints**: zlim must be ≤0 (below sea level), dmin must be positive
- **Boolean Values**: WW3 requires 'T'/'F', not Python True/False
- **Forcing Flags**: Only F/T/H/C values allowed for forcing configuration
- **File Validation**: Scale factors cannot be zero, unit numbers must be positive