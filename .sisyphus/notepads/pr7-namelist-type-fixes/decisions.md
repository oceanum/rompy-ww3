# Decisions - PR #7 Namelist Type Fixes

This file captures architectural and design decisions made during implementation.

---

## Task 4: Type Conversion Policy (2026-02-19)

### Decision: Comprehensive Type Conversion Rules Documented

Created formal policy document defining conversion rules for WW3 namelist fields:
- **Location**: `.sisyphus/evidence/task-04-conversion-policy.md`

### Key Decisions Made

#### 1. Date/Time Conversions: `str` → `datetime`
- **Criteria**: Fields with date/time indicators (`start`, `stop`, `time`, etc.) validated with `validate_date_format()`
- **Included**: `start`, `stop`, `timestart`, `timestop`, `update_time`, `restarttime`
- **Excluded**: `timestride`, `timecount` (these are numeric counts, not dates)
- **Parsing**: Accept WW3 format (`YYYYMMDD HHMMSS`), ISO 8601, Python datetime objects
- **Rendering**: Output as `YYYYMMDD HHMMSS` (bare token, no quotes)

#### 2. Timezone Policy: NAIVE DATETIMES ONLY
- **Decision**: Reject timezone-aware datetime objects
- **Rationale**: WW3 namelists do not support timezone information; all times implicitly UTC or model-local
- **Implementation**: Add validator to reject `datetime` objects with `tzinfo` set

#### 3. Integer Conversions: `str` → `int`
- **Criteria**: Fields representing counts, strides, indices (`stride`, `count`, `nx`, `ny`, etc.)
- **Included**: `stride`, `timestride`, `count`, `timecount`, grid dimensions
- **Excluded**: File format identifiers, enum-like flags represented as numeric strings
- **Parsing**: Accept numeric strings (`'3600'`), integer values (`3600`)
- **Rendering**: Output as unquoted integer literal (`3600`)

#### 4. Boolean Conversions: `str` → `bool`
- **Criteria**: Fields accepting ONLY two values (`T`/`F`), validated with `validate_ww3_boolean()`
- **CRITICAL**: Multi-valued flags (`F/T/H/C`) are NOT booleans - see exclusion below
- **Parsing**: Accept WW3 strings (`'T'`, `'F'`), Python bool values (`True`, `False`)
- **Rendering**: Output as bare `T`/`F` tokens (already implemented via `boolean_to_string()`)

#### 5. Multi-Valued Flags: DEFERRED
- **Decision**: Keep as validated `str` - do NOT convert to `bool` or `Enum` in this PR
- **Rationale**: 
  - Not true booleans - enumerations with 3-5 possible values
  - Optimal representation unclear (Literal, Enum, validated str?)
  - Existing validation functional
  - Adds complexity without immediate benefit
- **Explicitly Deferred**: Forcing flags (`winds`, `water_levels`, etc.) with values `F/T/H/C`

#### 6. Validation Duplication: NO REFACTOR
- **Current State**: `validate_date_format()` and `validate_ww3_boolean()` exist in both `validation.py` and `basemodel.py`
- **Decision**: Keep duplication for this PR - refactor in separate, focused PR
- **Rationale**: Avoid scope creep; focus on type conversions only

#### 7. Rendering Enhancement Required
- **Change**: Add `datetime` and `int` support to `NamelistBaseModel.process_value()`
- **Implementation**:
  - `datetime` → `value.strftime('%Y%m%d %H%M%S')`
  - `int` → unquoted literal (pass through)
- **Location**: `src/rompy_ww3/namelists/basemodel.py:process_value()`

#### 8. Backward Compatibility Guarantee
- **Input**: All existing string-based inputs must continue to parse
- **Mechanism**: Pydantic `@field_validator(mode='before')` accepts both strings and typed values
- **Output**: Namelist rendering byte-for-byte identical or functionally equivalent
- **Verification**: Golden output comparison (Tasks 3, 10)

### Scope Exclusions (Never Convert)
1. **File paths and names**: Fields with `file`, `filename`, `path`, `prefix`, etc.
2. **Format identifiers**: `format`, `type` fields with textual codes
3. **Mixed-content fields**: Fields accepting keywords AND dates (e.g., `'NOW'` or date)
4. **Multi-valued flags**: Forcing selectors `F/T/H/C` (deferred)

### Implementation Pattern Examples
Documented concrete before/after code examples for:
- Date field conversion with parsing and rendering
- Integer field conversion with string parsing
- Boolean field conversion with T/F parsing
- Rendered Fortran namelist output for each type

### Rationale Summary
| Decision | Rationale |
|----------|-----------|
| Naive datetime only | WW3 namelists have no timezone support; avoid ambiguity |
| Defer enum conversions | Unclear optimal representation; existing validation works |
| Preserve duplication | Avoid scope creep; refactor in dedicated PR |
| Enhance process_value() | Single point of rendering logic; minimal changes |

### Next Steps
- Task 5: Implement datetime rendering support in `process_value()`
- Task 6+: Begin field conversions following documented patterns
- Continuously verify against golden outputs

