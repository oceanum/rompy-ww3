# Enum Type Safety for Fixed-Vocabulary WW3 Namelist Fields

## TL;DR
Convert **all fixed-vocabulary** WW3 namelist fields (currently represented as `str`/`int` + set-based validators) into **typed Enums** to make the API type-safe across **Python + YAML/JSON/CLI** entry points. Inputs may use **Enum.name or Enum.value** (validated + normalized; unknowns hard-fail). Exports/dumps emit **canonical WW3 tokens/codes** (`Enum.value`). Booleans remain **strict `bool`** and render to `'T'/'F'`.

**Estimated Effort**: Large
**Parallel Execution**: YES (4 waves + final verification)
**Critical Path**: Baseline capture → Enum infra + serializer/render handling → module conversions → CLI/YAML/JSON roundtrip verification → final diffs/tests

---

## Context

### Original Request
“Tackle the enum piece” by converting small fixed-vocab fields into Enums.

### Key Decisions (Interview)
- Scope: **ALL fixed-vocabulary fields** across namelists.
- Entry points: **Python + YAML/JSON + CLI** must be type-safe.
- Input format: accept **Enum.name** and **Enum.value** as simple scalars; normalize; **hard fail** on unknown.
- Parsing strictness: trim whitespace; accept **case-insensitive Enum.value** and **case-insensitive Enum.name**.
- Precedence rule (accepted): exact value match → case-insensitive value match → case-insensitive name match; if multiple matches remain, hard fail listing candidates.
- Output format: dumps/exports emit **canonical** `Enum.value`.
- Booleans: **do not** use enum; keep **strict `bool`** + existing WW3 rendering.

### Key Codebase Findings (Evidence)
- Canonical vocab sets live in `src/rompy_ww3/namelists/validation.py`:
  - `IOSTYP_VALUES = {0,1,2,3}`
  - `GRID_TYPE_VALUES = {"RECT","CURV","UNST","SMC"}`
  - `COORD_TYPE_VALUES = {"SPHE","CART"}`
  - `CLOS_TYPE_VALUES = {"NONE","SMPL","TRPL"}`
  - `FORCING_VALUES = {"F","T","H","C"}`
- Roundtrip surfaces:
  - CLI uses `Config.model_dump_json()` and `Config.model_validate_json()` (`src/rompy_ww3/cli.py`).
  - Regtests YAML uses `yaml.safe_load` (`regtests/runner/core/test.py`).
- Rendering/serialization hooks:
  - Namelist models use a custom `@model_serializer` and `process_value()` (`src/rompy_ww3/namelists/basemodel.py`).
  - Enum members must be converted to primitives (`.value`) before JSON dump / WW3 render.

### Metis Review (gaps addressed in this plan)
- Add explicit guardrails for **rendering invariance** and **error message quality**.
- Ensure Enum→primitive conversion happens in shared serializer/render hooks, not ad-hoc.
- Define “fixed vocabulary” criteria and prevent scope creep.

---

## Work Objectives

### Core Objective
Replace finite-vocabulary `str`/`int` fields in WW3 namelist models with Enum types, while preserving identical WW3 namelist output and ensuring YAML/JSON/CLI roundtrips remain usable and strictly validated.

### Definition of Done
- [ ] All enum-candidate fields are typed as Enums (centralized), with validators accepting Enum.name/value scalars.
- [ ] All existing tests pass.
- [ ] CLI `init` → JSON written → `validate/run` can read it back.
- [ ] YAML regtests configs still parse and run config generation.
- [ ] Namelist rendering outputs are **byte-identical** for representative example/regtest configurations (baseline diff = empty).
- [ ] Invalid enum inputs hard-fail with an error listing allowed canonical values.

### Must NOT Have (Guardrails)
- Do **not** convert boolean fields into enums.
- Do **not** silently accept unknown/ambiguous inputs.
- Do **not** implement “friendly” normalization beyond trim + case-fold (e.g., no hyphen/underscore equivalence) unless explicitly added as a separate decision.
- Do **not** change WW3 token rendering (quotes, casing, spacing) beyond what is required to emit the same canonical values.
- Avoid global `use_enum_values=True` unless proven necessary (prefer explicit serialization).
- Do **not** add new third-party dependencies for enum parsing/serialization.
- Do **not** leave the codebase in a partially-converted state (inventory completeness is part of verification).

---

## Verification Strategy (MANDATORY)

### Test Decision
- **Infrastructure exists**: YES (pytest)
- **Automated tests**: YES (**tests-after**, plus targeted new unit tests)

### QA Policy
Every task includes agent-executed QA scenarios. Evidence saved to `.sisyphus/evidence/`.

Global verification commands (used repeatedly):
- `pytest tests/ -q`
- CLI smoke: `rompy_ww3 --help`, `rompy_ww3 init ...`, `rompy_ww3 validate ...` (exact flags in tasks)

---

## Execution Strategy

### Parallel Execution Waves (overview)

**Wave 1 (foundation + invariants)**
- Baseline capture for rendering invariance
- Enum infrastructure + normalization rules
- Serializer/render hook updates (Enum → primitive)
- “Fixed vocab” inventory tooling (search + list)

**Wave 2 (core namelist conversions)**
- Convert high-impact modules using `validation.py` sets (grid, domain, input)

**Wave 3 (remaining fixed-vocab conversions)**
- Convert other namelist modules with finite sets (bound/field/point/output_file + repeated idla/idfm patterns)

**Wave 4 (roundtrip + docs + regression)**
- Ensure CLI JSON + YAML regtests roundtrip behavior
- Update docs/examples if they reference friendly names or outdated allowed-value descriptions

---

## TODOs

- [ ] 1. Capture baseline WW3 rendering outputs for diffing

  **What to do**:
  - Select representative generation inputs:
    - 1–2 configs under `examples/`
    - 2–3 configs under `regtests/*/*.py` (a mix of `ww3_tp*` and `mww3_test_*`)
  - Generate the WW3 namelist outputs and store them as baseline artifacts.
  - Record checksums for each generated `.nml` file.

  **Must NOT do**:
  - Do not change any model code in this task.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 6–9, Final Verification F1
  - **Blocked By**: None

  **References**:
  - `src/rompy_ww3/namelists/basemodel.py` — rendering logic; baseline comparison target.
  - `examples/` — sample configurations.
  - `regtests/` — canonical test configurations.

  **Acceptance Criteria**:
  - [ ] Baseline artifacts exist under `.sisyphus/evidence/enum-baseline/` with a checksum manifest.

  **QA Scenarios**:
  ```
  Scenario: Capture baseline namelist checksums
    Tool: Bash
    Steps:
      1. Generate namelists for selected examples/regtests.
      2. Compute checksums for all produced .nml files.
      3. Save outputs + checksums under .sisyphus/evidence/enum-baseline/.
    Expected Result: Stable baseline files and checksums exist.
    Evidence: .sisyphus/evidence/task-01-enum-baseline.txt
  ```

- [ ] 2. Define centralized Enums for all fixed-vocabulary fields

  **What to do**:
  - Add canonical enum definitions (recommended: `src/rompy_ww3/namelists/enums.py`).
  - For string tokens use `class X(str, Enum)`; for integer code sets use `IntEnum`.
  - Ensure **Enum.value equals the canonical WW3 token/code**.
  - Provide parsing helpers that accept YAML/JSON/CLI scalars with the agreed precedence:
    - Enum member → pass-through
    - string matching Enum.value (exact) → normalize
    - string matching Enum.value (case-insensitive) → normalize
    - string matching Enum.name (case-insensitive) → normalize
    - for IntEnum: numeric strings (e.g., "3")
  - Unknown/ambiguous → hard fail with a message listing allowed canonical values.

  **Must NOT do**:
  - Do not add boolean enums.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 4–8
  - **Blocked By**: None

  **References**:
  - `src/rompy_ww3/namelists/validation.py` — canonical sets to convert.
  - Metis guardrail: avoid global `use_enum_values=True` if possible.

  **Acceptance Criteria**:
  - [ ] Enums exist for every fixed-vocab set in the namelists.
  - [ ] Parse helper accepts name/value and hard-fails on invalid.

  **QA Scenarios**:
  ```
  Scenario: Enum parsing is strict and normalized
    Tool: Bash (python -c)
    Steps:
      1. Parse by value token/code.
      2. Parse by member name.
      3. Parse an invalid token.
    Expected Result: (1)-(2) normalize; (3) raises ValueError listing allowed values.
    Evidence: .sisyphus/evidence/task-02-enum-parse.txt
  ```

- [ ] 3. Build an inventory mapping of all fixed-vocab fields → Enums

  **What to do**:
  - Scan `src/rompy_ww3/namelists/**` for finite vocab validators (membership in sets, explicit allowed lists, `Literal[...]`, etc.).
  - Produce an inventory table: file, class, field, allowed values, target enum.
  - Use this inventory as the checklist for conversion completeness.
  - Include a short “search recipe” at the top of the inventory (patterns/commands) so the executor can re-run it.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 6–7
  - **Blocked By**: None

  **References**:
  - `src/rompy_ww3/namelists/validation.py` — starting point.

  **Acceptance Criteria**:
  - [ ] Inventory saved to `.sisyphus/evidence/enum-inventory.md`.
  - [ ] Inventory includes every match found by searching for: `Literal[`, `must be one of`, and set-membership validators in namelists.

  **QA Scenarios**:
  ```
  Scenario: Inventory covers all fixed vocab validators
    Tool: Bash
    Steps:
      1. Search namelists for fixed allowed-value validators.
      2. Confirm each appears in the inventory.
    Expected Result: No fixed-vocab validator is missing from the inventory.
    Evidence: .sisyphus/evidence/task-03-enum-inventory.txt
  ```

- [ ] 4. Update shared serializer + renderer to emit Enum.value

  **What to do**:
  - Update the shared namelist serialization and rendering hooks so enums never leak as `EnumClass.MEMBER` representations.
  - Ensure JSON/YAML dumps used by CLI/export paths emit canonical values.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 6–9, Final Verification F1/F2
  - **Blocked By**: Task 2

  **References**:
  - `src/rompy_ww3/namelists/basemodel.py` — `@model_serializer`, `process_value()`.
  - `src/rompy_ww3/components/basemodel.py` — component-level serialization.
  - `src/rompy_ww3/cli.py` — `model_dump_json()`/`model_validate_json()` surfaces.

  **Acceptance Criteria**:
  - [ ] `model_dump_json()` succeeds for configs containing enums.
  - [ ] Rendered namelists contain canonical tokens/codes.

  **QA Scenarios**:
  ```
  Scenario: model_dump_json emits canonical enum values
    Tool: Bash (python -c)
    Steps:
      1. Construct a config with enum fields.
      2. Call model_dump_json().
      3. Assert serialized output contains canonical values.
    Expected Result: JSON includes "RECT" not "GridType.RECT".
    Evidence: .sisyphus/evidence/task-04-json-dump-enums.txt
  ```

- [ ] 5. Make validation helpers Enum-aware (defensive)

  **What to do**:
  - Update `src/rompy_ww3/namelists/validation.py` helpers to accept Enum members by converting to `.value`.
  - Keep error messages canonical.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Tasks 6–7
  - **Blocked By**: Task 2

  **Acceptance Criteria**:
  - [ ] Passing Enum members through validate helpers does not error.

  **QA Scenarios**:
  ```
  Scenario: validation helpers accept Enum members
    Tool: Bash (python -c)
    Steps:
      1. Import one of the new Enums and pass a member into a representative validation helper.
      2. Confirm it behaves identically to passing the raw canonical value.
    Expected Result: No exception; validated behavior matches baseline.
    Evidence: .sisyphus/evidence/task-05-validation-enum-aware.txt
  ```

- [ ] 6. Convert core namelist modules (grid/domain/input)

  **What to do**:
  - Convert the most reused fixed-vocab fields:
    - Grid type/coord/closure
    - Domain iostyp
    - Forcing values (F/T/H/C)
  - Validators accept name/value scalars and normalize.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (split per module)
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 7–9
  - **Blocked By**: Tasks 2,4

  **Acceptance Criteria**:
  - [ ] Existing tests for these modules pass.

  **QA Scenarios**:
  ```
  Scenario: core modules accept name/value scalars
    Tool: Bash (python -c)
    Steps:
      1. Construct models using canonical values (e.g., "RECT", 1).
      2. Construct models using case-insensitive values (e.g., "rect").
      3. Construct models using Enum names (case-insensitive).
      4. Construct models with invalid tokens.
    Expected Result: (1)-(3) normalize; (4) hard-fails with allowed values listed.
    Evidence: .sisyphus/evidence/task-06-core-modules-parse.txt
  ```

- [ ] 7. Convert remaining fixed-vocab fields across namelists (inventory-driven)

  **What to do**:
  - Convert every inventory entry outside the core modules.
  - Focus hotspots:
    - `bound.py`, `field.py`, `point.py`, `output_file.py`
    - repeated `idla`/`idfm` patterns in file-like namelists (depth/curv/smc/mask/slope/obstacle/sediment/unst/etc.)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`

  **Parallelization**:
  - **Can Run In Parallel**: YES (split per module)
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 9
  - **Blocked By**: Tasks 2,3,4

  **Acceptance Criteria**:
  - [ ] Every inventory entry is converted or explicitly marked excluded (with reason) in the inventory.

  **QA Scenarios**:
  ```
  Scenario: inventory-driven conversion is complete
    Tool: Bash
    Steps:
      1. Re-run the inventory search recipe.
      2. Confirm no fixed-vocab validators remain in namelists without an Enum mapping.
    Expected Result: No unaccounted fixed-vocab validators remain.
    Evidence: .sisyphus/evidence/task-07-inventory-completeness.txt
  ```

- [ ] 8. Add targeted tests for enum parsing + dumps + rendering

  **What to do**:
  - Add tests asserting:
    - name/value scalar inputs normalize to Enum
    - invalid input hard-fails with allowed list
    - JSON dumps emit canonical values
    - rendering uses canonical tokens
    - ambiguity handling (if multiple matches remain → hard fail listing candidates)

  **Recommended Agent Profile**:
  - **Category**: `deep`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 9, Final Verification
  - **Blocked By**: Tasks 4,6,7

- [ ] 9. Re-run baseline generation + diff + full suite

  **What to do**:
  - Re-generate the same configs used for baseline.
  - Diff content/checksums against baseline.
  - Run `pytest tests/`.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 4
  - **Blocks**: Final Verification
  - **Blocked By**: Tasks 6–8

---

## Final Verification Wave

- [ ] F1. **Rendering Invariance Audit**
  - Generate WW3 namelists for a representative sample (examples + a few regtests) before/after and diff.

- [ ] F2. **Roundtrip Audit (CLI + YAML)**
  - CLI: init → validate/load.
  - YAML: regtests runner loads YAML and constructs configs.

- [ ] F3. **Full Test Suite**
  - `pytest tests/`

- [ ] F4. **Scope Fidelity Check**
  - Confirm only fixed-vocab fields changed; booleans remain bool.

---

## Commit Strategy

- Prefer 4–8 atomic commits aligned to waves (enum infra; serializer; per-module conversions; roundtrip/docs; final cleanups).

## Success Criteria

- [ ] No user-facing entry point accepts invalid enum inputs.
- [ ] All outputs (namelist render, JSON/YAML dumps) emit canonical WW3 tokens/codes.
- [ ] All tests pass; diffs against baseline are empty.
