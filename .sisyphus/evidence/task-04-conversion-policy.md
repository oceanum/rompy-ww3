# WW3 Namelist Type Conversion Policy

**Document Version:** 1.0  
**Date:** 2026-02-19  
**PR:** #7 - Fix mis-typed WW3 namelist fields

---

## Purpose

This document defines the rules and policies for converting WW3 namelist Pydantic model fields from `str` to strongly typed Python types (`datetime`, `int`, `bool`), while preserving WW3 Fortran-style namelist rendering and maintaining backward-compatible parsing.

---

## Core Principles

1. **Preserve WW3 Namelist Format**: All conversions must maintain byte-for-byte (or functionally equivalent) WW3 Fortran namelist output
2. **Backward Compatibility**: Existing configurations using string inputs must continue to load
3. **Explicit Conversion Only**: Only convert fields with high confidence and clear semantic types
4. **No Scope Creep**: Do not convert fields that are genuinely textual (file paths, names, prefixes, format identifiers)

---

## Conversion Rules by Type

### 1. Date/Time Fields: `str` → `datetime`

#### Criteria for Conversion
A `str` field is a candidate for `datetime` conversion if **ALL** of the following are true:
- Field represents an absolute date and time (not a relative time or duration)
- Field name contains date/time indicators: `start`, `stop`, `time`, `date`, `restart`, `update`
- Field is currently validated with `validate_date_format()` OR conforms to WW3 date format in usage
- Field accepts WW3 format: `YYYYMMDD HHMMSS`

#### Explicitly Included Fields
- `start`, `stop` (model domain timing)
- `timestart`, `timestop` (output timing)
- `time_start`, `time_stop` (alternative naming)
- `update_time` (restart/update timing)
- `restarttime` (restart initialization)

#### Explicitly Excluded Fields
- `timestride`, `timecount` - these are **numeric counts/strides**, not dates
- `timesplit` - configuration parameter, not a date
- Fields containing `time` but representing durations or intervals

#### Input Parsing Requirements
Must accept (via Pydantic `@field_validator(mode='before')`):

1. **WW3 format string** (preserved): `'20230101 000000'` → `datetime(2023, 1, 1, 0, 0, 0)`
2. **ISO 8601 format**: `'2023-01-01 00:00:00'` → `datetime(2023, 1, 1, 0, 0, 0)`
3. **Python datetime objects** (direct): `datetime(2023, 1, 1, 0, 0, 0)` → no conversion needed
4. **Alternative formats** (from `validate_date_format()` patterns):
   - `'YYYY/MM/DD HH:MM:SS'`
   - `'YYYY-MM-DD HH:MM'`
   - `'YYYY/MM/DD HH:MM'`
   - `'YYYY-MM-DD'` (time defaults to 00:00:00)

#### Output Rendering Requirements
Must render (via `NamelistBaseModel.process_value()`):

- **Output format**: `YYYYMMDD HHMMSS` (WW3 Fortran format)
- **No quotes**: Dates render as bare tokens, not quoted strings
- **Example**: `datetime(2023, 1, 1, 0, 0, 0)` → `20230101 000000`

#### Timezone Policy
**TIMEZONE POLICY: NAIVE DATETIMES ONLY**

- **Accept**: Naive `datetime` objects (no timezone information)
- **Reject**: Timezone-aware `datetime` objects with `tzinfo` set
- **Rationale**: WW3 namelists do not support timezone information; all times are implicitly UTC or model-local
- **Validation**: Add validator to reject aware datetimes: `if value.tzinfo is not None: raise ValueError(...)`

#### Example Conversion Pattern
```python
from datetime import datetime
from pydantic import field_validator

class Domain(NamelistBaseModel):
    start: Optional[datetime] = Field(None, description="Start date")
    
    @field_validator('start', mode='before')
    @classmethod
    def parse_start_date(cls, v):
        if v is None or isinstance(v, datetime):
            return v
        if isinstance(v, str):
            return cls._parse_ww3_date(v)  # Use existing validate_date_format logic
        raise ValueError(f"Invalid date format: {v}")
    
    @field_validator('start')
    @classmethod
    def reject_aware_datetime(cls, v):
        if v is not None and v.tzinfo is not None:
            raise ValueError("Timezone-aware datetimes not supported. Use naive datetime (no tzinfo).")
        return v
```

---

### 2. Integer Fields: `str` → `int`

#### Criteria for Conversion
A `str` field is a candidate for `int` conversion if **ALL** of the following are true:
- Field represents a count, stride, index, or integer dimension
- Field name contains indicators: `stride`, `count`, `num`, `index`, `nx`, `ny`, `npts`
- Field is **not** a formatted identifier (e.g., file format codes, enum-like flags)
- Current usage shows numeric strings: `'3600'`, `'100'`, etc.

#### Explicitly Included Fields
- `stride`, `timestride` (output strides in time steps or seconds)
- `count`, `timecount` (counts of items or time steps)
- Grid dimensions: `nx`, `ny`, `nz`, `nspec`, `nfreq`, `nth` (if currently strings)
- Indexing fields: `index`, `unit_number` (if numeric)

#### Explicitly Excluded Fields
- File format identifiers even if numeric (e.g., `iostyp` if already typed)
- Enum-like flag fields represented as numeric strings (defer to flag section)

#### Input Parsing Requirements
Must accept:

1. **Numeric strings**: `'3600'` → `3600`
2. **Integer values**: `3600` → `3600` (direct)
3. **Float strings with zero decimals**: `'3600.0'` → `3600` (if practical)

#### Output Rendering Requirements
- **Output format**: Unquoted integer literal
- **Example**: `3600` → `3600` (not `'3600'`)

#### Example Conversion Pattern
```python
from pydantic import field_validator

class Track(NamelistBaseModel):
    timestride: Optional[int] = Field(None, description="Time stride in seconds")
    
    @field_validator('timestride', mode='before')
    @classmethod
    def parse_timestride(cls, v):
        if v is None or isinstance(v, int):
            return v
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                raise ValueError(f"Invalid integer: {v}")
        raise ValueError(f"Invalid integer format: {v}")
```

---

### 3. Boolean Fields: `str` → `bool`

#### Criteria for Conversion
A `str` field is a candidate for `bool` conversion if **ALL** of the following are true:
- Field accepts **only** two values: `'T'` or `'F'` (WW3 Fortran boolean)
- Field is **not** a multi-valued flag (see Exclusions below)
- Field is currently validated with `validate_ww3_boolean()` OR constrained to `{'T', 'F'}`
- Field represents a true binary on/off, yes/no, enabled/disabled state

#### Explicitly Included Fields
Boolean flags validated with `validate_ww3_boolean()` or constrained to `T/F` values (examples TBD after inventory)

#### Explicitly Excluded Fields
**CRITICAL: Multi-valued flags are NOT booleans**
- Forcing flags: `F/T/H/C` (no forcing, external file, homogeneous, coupled) - see Multi-Valued Flags section
- Any field accepting >2 values even if includes `T/F`

#### Input Parsing Requirements
Must accept:

1. **WW3 string format**: `'T'` → `True`, `'F'` → `False` (case-insensitive)
2. **Python bool values**: `True` → `True`, `False` → `False` (direct)
3. **Alternative representations** (optional): `'true'`, `'false'`, `'yes'`, `'no'`, `1`, `0` (if deemed safe)

#### Output Rendering Requirements
- **Output format**: Bare `T` or `F` tokens (no quotes)
- **Example**: `True` → `T`, `False` → `F`
- **Implementation**: Already exists in `NamelistBaseModel.process_value()` via `boolean_to_string()`

#### Example Conversion Pattern
```python
from pydantic import field_validator

class Input(NamelistBaseModel):
    some_flag: Optional[bool] = Field(None, description="Some boolean flag")
    
    @field_validator('some_flag', mode='before')
    @classmethod
    def parse_ww3_boolean(cls, v):
        if v is None or isinstance(v, bool):
            return v
        if isinstance(v, str):
            upper = v.upper()
            if upper == 'T':
                return True
            elif upper == 'F':
                return False
            else:
                raise ValueError(f"Invalid WW3 boolean: {v}. Must be 'T' or 'F'.")
        raise ValueError(f"Invalid boolean format: {v}")
```

---

### 4. Multi-Valued Flags: **DEFERRED**

#### Scope Decision
**Multi-valued flags (e.g., F/T/H/C forcing selectors) are DEFERRED to later work.**

#### Rationale
1. These are not true booleans—they are enumerations with 3-5 possible values
2. Optimal representation is unclear: `Literal['F', 'T', 'H', 'C']`, `Enum`, or validated `str`?
3. Conversion adds complexity without immediate user benefit
4. Existing string-based validation with `validate_forcing_type()` is functional

#### Current Approach
- **Keep as validated `str`** with validation functions (e.g., `validate_forcing_type()`)
- **Do NOT convert** to `bool` or `Enum` in this PR

#### Explicitly Deferred Fields
- Forcing configuration flags: `winds`, `water_levels`, `currents`, `ice`, etc. (values: `F/T/H/C`)
- Any field accepting >2 discrete string values

#### Future Work
If enum conversions are pursued later:
- Consider `Literal` types for small fixed sets
- Consider `Enum` classes for fields with semantic meaning beyond values
- Ensure backward compatibility with string inputs

---

## Validation Strategy

### Validation Duplication
**CURRENT STATE: Validation helpers are duplicated**
- `validate_date_format()` exists in both `validation.py` and `basemodel.py`
- `validate_ww3_boolean()` exists in both `validation.py` and `basemodel.py`

**POLICY FOR THIS PR: Do NOT refactor duplication**
- Keep both copies to avoid scope creep
- Use `validation.py` versions as canonical for imports
- Refactor duplication in a separate, focused PR after type conversions are complete

### Validator Placement
- Use Pydantic `@field_validator(mode='before')` for input parsing (string → typed)
- Use Pydantic `@field_validator(mode='after')` for constraint validation (e.g., reject aware datetimes)
- Reuse existing validation functions where possible

---

## Rendering Strategy

### Current Rendering Infrastructure
**File**: `src/rompy_ww3/namelists/basemodel.py`

**Method**: `NamelistBaseModel.process_value(value: Any) -> Any`

Current support:
- `bool` → `'T'/'F'` via `boolean_to_string()`
- `str` → `'<quoted string>'`
- Lists, nested objects, primitives

**REQUIRED ENHANCEMENT: Add `datetime` support**

```python
def process_value(self, value: Any) -> Any:
    """Process value for namelist formatting."""
    if isinstance(value, bool):
        return boolean_to_string(value)
    elif isinstance(value, datetime):
        # NEW: Handle datetime → WW3 format
        return value.strftime('%Y%m%d %H%M%S')
    elif isinstance(value, str):
        # Don't quote WW3 format artifacts (handled by bool/datetime cases)
        return f"'{value}'"
    elif isinstance(value, int):
        # NEW: Ensure integers render unquoted
        return value
    # ... existing list/dict handling
```

**Verification**: Rendering changes must be tested to ensure golden output equivalence (Task 5)

---

## Backward Compatibility Policy

### Input Compatibility
**GUARANTEE: All existing string-based inputs must continue to parse**

Users with existing configs like:
```python
Domain(start='20230101 000000', stop='20230107 000000')
```

Must **still work** after conversion to `datetime` fields.

**Mechanism**: Pydantic `@field_validator(mode='before')` accepts both strings and typed values

### Output Compatibility
**GOAL: Namelist output should be byte-for-byte identical (or functionally equivalent)**

Changes to rendered output are acceptable **only if**:
- Semantically equivalent (e.g., `3600` vs `'3600'` are equivalent for WW3 integers)
- Removal of unnecessary quotes (e.g., `3600` vs `'3600'` - unquoted is preferred)
- No changes to date formats, boolean representations, or field names/structure

**Verification**: Golden output comparison (Task 3, Task 10)

---

## Scope Exclusions

### Never Convert These Field Types

1. **File Paths and Names**
   - Fields containing: `file`, `filename`, `path`, `dir`, `prefix`, `suffix`
   - Example: `filepath`, `out_prefix`, `grid_name`
   - **Rationale**: Genuinely textual, no semantic type

2. **Format Identifiers and Codes**
   - Fields like: `format`, `type` (when textual codes)
   - Example: `fileformat='unformatted'`, `coord_type='SPHE'`
   - **Rationale**: Discrete string identifiers, not dates/numbers/booleans

3. **Mixed-Content Fields**
   - Fields accepting both keywords AND dates (e.g., `'NOW'` or `'20230101 000000'`)
   - **Keep as**: `Union[Literal['NOW'], datetime]` or validated `str`
   - **Rationale**: Union types add complexity; defer unless critical

4. **Multi-Valued Flags** (see dedicated section)
   - Forcing selectors: `F/T/H/C`
   - **Rationale**: Deferred to later work

---

## Example Conversions

### Date Field Example
**Before:**
```python
class Domain(NamelistBaseModel):
    start: Optional[str] = Field(None, description="Start date YYYYMMDD HHMMSS")
    
    @field_validator('start')
    @classmethod
    def validate_start(cls, v):
        if v is not None:
            return validate_date_format(v)
        return v
```

**After:**
```python
from datetime import datetime

class Domain(NamelistBaseModel):
    start: Optional[datetime] = Field(None, description="Start date")
    
    @field_validator('start', mode='before')
    @classmethod
    def parse_start(cls, v):
        if v is None or isinstance(v, datetime):
            return v
        if isinstance(v, str):
            # Reuse existing parsing logic
            date_str = validate_date_format(v)  # Returns 'YYYYMMDD HHMMSS'
            return datetime.strptime(date_str, '%Y%m%d %H%M%S')
        raise ValueError(f"Invalid date: {v}")
    
    @field_validator('start')
    @classmethod
    def reject_aware(cls, v):
        if v is not None and v.tzinfo is not None:
            raise ValueError("Timezone-aware datetimes not supported")
        return v
```

**Rendered Output:**
```fortran
&DOMAIN_NML
  DOMAIN%START = 20230101 000000
/
```

---

### Integer Field Example
**Before:**
```python
class Track(NamelistBaseModel):
    timestride: Optional[str] = Field(None, description="Time stride")
```

**After:**
```python
class Track(NamelistBaseModel):
    timestride: Optional[int] = Field(None, description="Time stride in seconds")
    
    @field_validator('timestride', mode='before')
    @classmethod
    def parse_timestride(cls, v):
        if v is None or isinstance(v, int):
            return v
        if isinstance(v, str):
            return int(v)
        raise ValueError(f"Invalid integer: {v}")
```

**Rendered Output:**
```fortran
&TRACK_NML
  TRACK%TIMESTRIDE = 3600
/
```

---

### Boolean Field Example
**Before:**
```python
class SomeNML(NamelistBaseModel):
    some_flag: Optional[str] = Field(None, description="Some flag T/F")
    
    @field_validator('some_flag')
    @classmethod
    def validate_flag(cls, v):
        if v is not None:
            return validate_ww3_boolean(v)
        return v
```

**After:**
```python
class SomeNML(NamelistBaseModel):
    some_flag: Optional[bool] = Field(None, description="Some flag")
    
    @field_validator('some_flag', mode='before')
    @classmethod
    def parse_flag(cls, v):
        if v is None or isinstance(v, bool):
            return v
        if isinstance(v, str):
            upper = v.upper()
            if upper == 'T':
                return True
            elif upper == 'F':
                return False
        raise ValueError(f"Invalid boolean: {v}")
```

**Rendered Output:**
```fortran
&SOME_NML
  SOME%SOME_FLAG = T
/
```

---

## Implementation Checklist

For each field conversion:

- [ ] Verify field meets criteria for conversion (see type-specific sections)
- [ ] Add `@field_validator(mode='before')` for parsing strings + typed values
- [ ] Add constraint validators (e.g., reject aware datetimes) if needed
- [ ] Update field type annotation: `str` → `datetime`/`int`/`bool`
- [ ] Update field description to reflect typed nature
- [ ] Test backward compatibility: existing string inputs still parse
- [ ] Test rendering output: matches WW3 format expectations
- [ ] Run full test suite: `make test`
- [ ] Generate golden output: compare to baseline

---

## Rationale Summary

| Decision | Rationale |
|----------|-----------|
| Naive datetime only | WW3 namelists have no timezone support; avoid ambiguity |
| Defer enum conversions | Unclear optimal representation; existing validation works |
| Preserve duplication | Avoid scope creep; refactor in dedicated PR |
| Enhance `process_value()` | Single point of rendering logic; minimal changes |
| Backward compatible parsing | Protect existing user configs; low migration friction |
| Golden output comparison | Regression protection for WW3 namelist format |

---

## Success Criteria

This policy is successfully applied when:

1. **All date fields** meeting criteria are converted to `datetime` with naive-only validation
2. **All integer fields** meeting criteria are converted to `int` with string parsing
3. **All boolean fields** meeting criteria are converted to `bool` with `T/F` parsing
4. **Multi-valued flags** remain as validated `str` (explicitly deferred)
5. **All existing tests pass** after conversions
6. **Golden namelist outputs** are unchanged or justifiably different
7. **Backward compatibility** is preserved for string inputs

---

**Document Status:** COMPLETE  
**Review Status:** Ready for implementation  
**Next Steps:** Begin Task 5 (datetime rendering support) and Task 6+ (field conversions)
