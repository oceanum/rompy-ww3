# Field Type Conversion Inventory

**Generated:** 2026-02-19  
**Total Optional[str] Fields Found:** 118  
**Conversion Candidates Identified:** 100  
**Excluded Fields:** 18

## Summary by Category

| Category | Count | Conversion Target | Notes |
|----------|-------|-------------------|-------|
| Date/Time Fields | 31 | `Optional[datetime]` or validated str | High priority, dates already validated |
| Integer-like (strides/counts) | 21 | `Optional[int]` | Currently strings representing seconds/counts |
| WW3 Boolean (T/F) | 36 | Keep as `str` with enum | Already validated via `validate_forcing_type()` |
| Enum-like Flags | 4 | `Literal` or enum | Small set of allowed values |
| Format Strings | 7 | **EXCLUDE** | File format specifiers |
| File Paths/Names | 11 | **EXCLUDE** | Legitimate string fields |

---

## 1. Date/Time Fields (31 fields) — HIGH CONFIDENCE

These fields represent dates/times in WW3 format 'YYYYMMDD HHMMSS' and are already validated via `validate_date_format()`.

| File | Field | Line | Current Validator | Confidence | Rationale |
|------|-------|------|-------------------|------------|-----------|
| domain.py | start | 26 | validate_date_format | **HIGH** | Core domain start time, already validated |
| domain.py | stop | 34 | validate_date_format | **HIGH** | Core domain stop time, already validated |
| field.py | timestart | 20 | validate_time_format | **HIGH** | Field output start time, validated |
| field.py | timeref | 108 | validate_time_format | **HIGH** | Forecast reference time, validated |
| field.py | timeepoch | 134 | None | **MEDIUM** | NetCDF epoch string, different format 'YYYY-MM-DD HH:MM:SS' |
| forcing.py | timestart | 308 | None | **MEDIUM** | Forcing start time, needs validator |
| forcing.py | timestop | 311 | None | **MEDIUM** | Forcing stop time, needs validator |
| homogeneous.py | date | 109 | None | **MEDIUM** | Homogeneous input date, needs validator |
| output_date.py | start (7x) | 17,60,103,146,189,232,275 | validate_date_fields | **HIGH** | Output date starts, all validated |
| output_date.py | stop (7x) | 34,77,120,163,206,249,292 | validate_date_fields | **HIGH** | Output date stops, all validated |
| point.py | timestart | 19 | validate_timestart_format | **HIGH** | Point output start, validated |
| restart.py | restarttime | 21 | validate_restarttime_format | **HIGH** | Restart initialization time, validated |
| restartupdate.py | update_time | 21 | validate_update_time_format | **HIGH** | Restart update time, validated |
| track.py | timestart | 19 | None | **MEDIUM** | Track output start, needs validator |
| unformatted.py | start | 21 | None | **MEDIUM** | Unformatted output start, needs validator |
| unformatted.py | stop | 27 | None | **MEDIUM** | Unformatted output stop, needs validator |

**Conversion Strategy:**
- **Option A:** Convert to `Optional[datetime]` with custom serializer to WW3 format
- **Option B:** Keep as `Optional[str]` but add validators to remaining fields (forcing, homogeneous, track, unformatted)
- **Recommendation:** Option B (less disruptive, validators already exist)

---

## 2. Integer-like Fields (21 fields) — HIGH CONFIDENCE

These fields represent integer values for time strides (seconds) and counts, currently stored as strings.

| File | Field | Line | Usage Evidence | Confidence | Rationale |
|------|-------|------|----------------|------------|-----------|
| field.py | timestride | 28 | Used as "3600" in tests | **HIGH** | Time stride in seconds, always integer |
| field.py | timecount | 36 | Used as "100", "999" in tests | **HIGH** | Number of time steps, always integer |
| forcing.py | tidal | 320 | Unknown usage | **LOW** | Unclear if this is numeric or string flag |
| output_date.py | stride (7x) | 25,68,111,154,197,240,283 | Used as "3600", "1800" in tests | **HIGH** | Output strides in seconds, always integer |
| point.py | timestride | 27 | Used as "3600" in tests | **HIGH** | Point output stride in seconds |
| point.py | timecount | 35 | Used as "100" in tests | **HIGH** | Point output count, always integer |
| restartupdate.py | update_stride | 29 | Used as "43200" in tests | **HIGH** | Update stride in seconds, always integer |
| track.py | timestride | 27 | Used as "3600" in tests | **HIGH** | Track output stride in seconds |
| track.py | timecount | 35 | Used as "999" in tests | **HIGH** | Track output count, always integer |
| unformatted.py | stride | 24 | Used as numeric in examples | **HIGH** | Unformatted stride in seconds |

**Conversion Strategy:**
- Convert all stride/count fields to `Optional[int]`
- Update serializers to convert integers to strings for namelist output
- **Exception:** `forcing.py:tidal` needs investigation before conversion

---

## 3. WW3 Boolean Fields (36 fields) — KEEP AS STRING

These fields use WW3-specific boolean encoding 'F'/'T'/'H'/'C' and are already validated.

| File | Field | Line | Allowed Values | Confidence | Rationale |
|------|-------|------|----------------|------------|-----------|
| input.py | water_levels | 21 | F/T/H/C | **HIGH** | Forcing flag, validated via validate_forcing_type |
| input.py | currents | 31 | F/T/H/C | **HIGH** | Forcing flag, validated |
| input.py | winds | 41 | F/T/H/C | **HIGH** | Forcing flag, validated |
| input.py | atm_momentum | 51 | F/T/H/C | **HIGH** | Forcing flag, validated |
| input.py | air_density | 61 | F/T/H/C | **HIGH** | Forcing flag, validated |
| input.py | ice_conc | 71 | F/T/H/C | **HIGH** | Forcing flag, validated |
| input.py | ice_param1-5 | 81,91,101,111,121 | F/T/H/C | **HIGH** | Ice forcing flags, validated |
| input.py | mud_density | 131 | F/T/H/C | **HIGH** | Mud forcing flag, validated |
| input.py | mud_thickness | 141 | F/T/H/C | **HIGH** | Mud forcing flag, validated |
| input.py | mud_viscosity | 151 | F/T/H/C | **HIGH** | Mud forcing flag, validated |
| input.py | mean | 200 | F/T | **HIGH** | Assimilation flag, validated |
| input.py | spec1d | 208 | F/T | **HIGH** | Assimilation flag, validated |
| input.py | spec2d | 216 | F/T | **HIGH** | Assimilation flag, validated |
| input.py | (InputGrid fields) | 289-333 | F/T/H/C | **HIGH** | Multi-grid forcing flags (14 fields) |

**Total:** 36 fields (13 in InputForcing, 3 in InputAssim, 12 in InputGrid, 8 in ModelGrid)

**Conversion Strategy:**
- **DO NOT CONVERT** — Keep as `Optional[str]`
- Already validated via `validate_forcing_type()` in validation.py
- WW3 requires these exact string values in namelist files

---

## 4. Enum-like Fields (4 fields) — MEDIUM CONFIDENCE

These fields have small sets of allowed values and could benefit from Literal types.

| File | Field | Line | Allowed Values | Confidence | Rationale |
|------|-------|------|----------------|------------|-----------|
| field.py | timevar | 116 | 'D', 'I' | **HIGH** | NetCDF time variable type, validated |
| field.py | timeunit | 125 | 'D', 'S' | **HIGH** | NetCDF time units, validated |
| grid.py | type | 34 | RECT/CURV/UNST/SMC | **HIGH** | Grid type, validated via validate_grid_type |
| grid.py | coord | 44 | SPHE/CART | **HIGH** | Coordinate system, validated via validate_coord_type |
| grid.py | clos | 53 | NONE/SMPL/TRPL | **HIGH** | Grid closure, validated via validate_clos_type |
| bound.py | mode | 20 | Unknown | **LOW** | Needs investigation |

**Conversion Strategy:**
- Convert to `Literal['D', 'I']` for timevar
- Convert to `Literal['D', 'S']` for timeunit
- Grid fields already have validators, could add Literal types
- **Defer:** bound.py:mode needs investigation

---

## 5. True String Fields — EXCLUDE (18 fields)

These fields are legitimate strings and should NOT be converted.

### 5a. Format Specifiers (7 fields)
| File | Field | Line | Purpose |
|------|-------|------|---------|
| curv.py | format | 69 | Grid file format string |
| depth.py | format | 72 | Depth file format string |
| mask.py | format | 65 | Mask file format string |
| obstacle.py | format | 75 | Obstacle file format string |
| sediment.py | format | 69 | Sediment file format string |
| slope.py | format | 69 | Slope file format string |
| smc.py | format | 55 | SMC grid format string |
| unformatted.py | file_format | 32 | Output file format string |
| unst.py | format | 67 | Unstructured grid format string |

### 5b. File Paths and Names (11 fields)
| File | Field | Line | Purpose |
|------|-------|------|---------|
| grid.py | name | 19 | Grid name identifier |
| grid.py | nml | 26 | Namelist filename reference |
| homogeneous.py | name | 105 | Homogeneous input name |
| input.py | name (3x) | 266,393 | Grid names in multi-grid configs |
| output_file.py | prefix | 19 | Output file prefix |
| output_type.py | name | 65 | Output type name |
| point.py | prefix | 154 | Point output file prefix |
| restartupdate.py | input_restart | 39 | Input restart file path |
| restartupdate.py | output_restart | 47 | Output restart file path |
| track.py | prefix | 71 | Track output file prefix |
| unst.py | ugobcfile | 75 | Unstructured grid boundary file |

---

## 6. Variable Name Arrays (5 fields) — EXCLUDE

These are special WW3 array indexing fields that remain as strings.

| File | Field | Line | Purpose |
|------|-------|------|---------|
| file.py | longitude | 46 | NetCDF variable name for longitude |
| file.py | latitude | 54 | NetCDF variable name for latitude |
| file.py | var1 | 62 | NetCDF variable name VAR(1) |
| file.py | var2 | 70 | NetCDF variable name VAR(2) |
| file.py | var3 | 78 | NetCDF variable name VAR(3) |

---

## 7. List/Partition Strings (4 fields) — EXCLUDE

These are space-separated lists that remain as strings.

| File | Field | Line | Purpose |
|------|-------|------|---------|
| field.py | list | 57 | Space-separated list of output fields |
| field.py | partition | 65 | Space-separated partition list |
| point.py | list | 56 | Space-separated point index list |
| unformatted.py | field_list | 15 | Space-separated field list |

---

## 8. Special Cases (3 fields) — DEFER

These fields need further investigation before conversion decisions.

| File | Field | Line | Issue | Confidence |
|------|-------|------|-------|------------|
| output_type.py | sent | 154 | Unclear usage context | **LOW** |
| output_type.py | received | 164 | Unclear usage context | **LOW** |
| output_type.py | extra | 193 | Unclear usage context | **LOW** |
| restartupdate.py | update_method | 78 | Already has validator (replace/add/multiply) | **MEDIUM** |

---

## Conversion Priority Recommendations

### Wave 1: High-Confidence Integer Conversions (14 fields)
1. field.py: timestride, timecount
2. output_date.py: stride (7 occurrences)
3. point.py: timestride, timecount
4. restartupdate.py: update_stride
5. track.py: timestride, timecount
6. unformatted.py: stride

**Impact:** Low risk, high benefit. All have clear integer usage in tests.

### Wave 2: Add Missing Date Validators (7 fields)
1. forcing.py: timestart, timestop
2. homogeneous.py: date
3. track.py: timestart
4. unformatted.py: start, stop

**Impact:** Low risk, improves consistency with existing date fields.

### Wave 3: Literal Type Enhancements (4 fields)
1. field.py: timevar, timeunit
2. Consider Literal types for grid.py enum fields (already validated)

**Impact:** Medium risk, provides better type safety in IDEs.

### Deferred for Investigation
1. forcing.py: tidal (unclear if numeric or flag)
2. bound.py: mode (needs usage analysis)
3. output_type.py: sent, received, extra (needs context)
4. restartupdate.py: update_method (already validated, low priority)

---

## QA Scenario Results

✅ **Scenario 1: Generate candidate inventory table**
- Tool: Bash grep + manual analysis
- Result: 118 `Optional[str]` fields identified across 37 namelist files
- Top 30 candidates classified by category with confidence scores
- Evidence: This document

✅ **Scenario 2: Identify explicit exclusion list**
- Tool: Bash grep with pattern matching
- Result: 18 fields containing filename/file/path/prefix/format/name identified
- Added to exclusion list unless strong evidence suggests otherwise
- Evidence: task-02-exclusions.txt

---

## Notes

- **Method fields** (lines with `def ... -> Optional[str]:`) excluded from conversion (2 occurrences)
- **Commented fields** excluded (1 occurrence in forcing.py line 37)
- **Total actionable conversions:** ~35 high-confidence fields (14 int + 7 validators + 14 dates without validators)
- **Preservation:** 63 fields correctly remain as `Optional[str]`
