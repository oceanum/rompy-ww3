# PR #7: Fix mis-typed WW3 namelist fields (str -> int/date/bool)

## TL;DR
Convert WW3 namelist Pydantic model fields that are currently `str` but semantically represent **dates**, **integers**, or **booleans** into appropriate Python types, while **preserving WW3 Fortran-style namelist rendering** (dates `YYYYMMDD HHMMSS`, booleans `T/F`) and maintaining **backward-compatible parsing** for existing configs.

## Context

### Original request
Plan to address PR #7 feedback: several inputs should be ints/dates rather than strings, and many booleans are currently strings.

### Key observations (from initial scan)
- `src/rompy_ww3/namelists/` contains many `Optional[str] = Field(...)` declarations (grep previously observed 115 matches).
- Multiple models already validate date-like fields as strings (e.g., `start/stop/timestart/...`) but represent them as `str`.
- Rendering currently happens via `NamelistBaseModel.render()` -> `_render_recursive()` -> `process_value()`, which converts Python `bool` to `T/F` and quotes strings, but does **not** explicitly handle `datetime`.
- Validation helpers for dates and WW3 booleans exist and appear duplicated in `namelists/validation.py` and `namelists/basemodel.py`.

### Non-goals / guardrails
- Do **not** convert fields that are truly textual (file paths, prefixes, names, format identifiers) even if they are `str`.
- Do **not** introduce new WW3 scientific validation constraints; only change types/serialization/validators needed for correctness.
- Avoid broad refactors (e.g., deduplicating validation helpers) unless required to safely support typed fields.
- Defer multi-valued flag conversions (e.g., forcing selectors like `F/T/H/C`) to a later effort; keep them as validated strings in this work.

---

## Work objectives

### Core objective
Introduce stronger typing for WW3 namelist fields (date/int/bool) with backwards-compatible input parsing, and ensure namelist output formatting remains WW3-compliant and (where possible) byte-for-byte unchanged.

### Concrete deliverables
- A reviewed inventory of candidate fields: `File | Field | Current type | Proposed type | Confidence | Notes`.
- Updated namelist rendering/serialization to support typed values (esp. `datetime`).
- Incremental conversion of high-confidence fields (dates, counts/strides, WW3 booleans) with tests.
- Regression protection: golden-output comparisons (or equivalent) to ensure namelist rendering stability.

---

## Verification strategy

### Test decision
- **Infrastructure exists**: YES (project has `tests/` and Make targets per repo docs).
- **Automated tests**: **YES (Tests-after)** — keep refactor safe by validating after each conversion wave.

### QA policy (mandatory)
Every task below includes **agent-executed QA scenarios** with concrete commands and evidence paths.

Evidence directory: `.sisyphus/evidence/`

---

## Execution strategy

### Parallel execution waves
The work is structured to maximize parallelism while keeping the critical path short:

- **Wave 1**: inventory + mapping + baseline outputs (foundation)
- **Wave 2**: rendering/serialization support for typed values (foundation)
- **Wave 3**: type conversions in parallel by concern (dates / ints / booleans)
- **Wave 4**: integration + docs + final verification

Critical path: Inventory -> Baseline outputs -> Rendering support -> Conversions -> Full test + golden diff

---

## TODOs

> NOTE: Tasks are written to be independently executable and reviewable. Each task targets 1 module/concern and 1-3 files.

- [x] 1. Map the full serialization/rendering surface area for namelists

  **What to do**:
  - Identify every code path where namelist models are converted to strings/files (not just `NamelistBaseModel.process_value`).
  - Confirm whether any Jinja2 templates or other renderers directly access field values.
  - Produce a short mapping: entry points 7 functions/methods 7 output artifacts.

  **Must NOT do**:
  - Do not change any behavior yet.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: mostly search + mapping.
  - **Skills**: []

  **Parallelization**:
  - Can Run In Parallel: YES
  - Parallel Group: Wave 1
  - Blocks: Tasks 5-12 (type conversions)
  - Blocked By: None

  **References**:
  - `src/rompy_ww3/namelists/basemodel.py`  `render()`, `_render_recursive()`, `process_value()`
  - `src/rompy_ww3/namelist_composer.py` (likely orchestration)
  - `src/rompy_ww3/components/` (where namelists are written)

  **Acceptance Criteria**:
  - [ ] A markdown note (in PR description or comment) lists the complete render flow and all call sites.

  **QA Scenarios**:
  ```
  Scenario: Locate all namelist render call sites
    Tool: Bash
    Steps:
      1. Run a repo-wide search for `.render(` calls on namelist models.
      2. Search for `.write_nml(` call sites.
      3. Search for direct file writes of `*.nml`.
    Expected Result: A list of file paths and functions/methods is produced and saved.
    Evidence: .sisyphus/evidence/task-01-render-surface.txt

  Scenario: Confirm no template-based rendering depends on string types
    Tool: Bash
    Steps:
      1. Search for `jinja`/`templates` directories and usage.
      2. If templates exist, identify whether they render date/bool fields directly.
    Expected Result: Either (a) no templates exist, or (b) impacted templates are enumerated.
    Evidence: .sisyphus/evidence/task-01-template-scan.txt
  ```

- [x] 2. Create a complete inventory of candidate fields for type conversion

  **What to do**:
  - Generate a table of all `Optional[str]` (and similar) fields across `src/rompy_ww3/namelists/`.
  - Categorize candidates into:
    - **Date/time** (e.g., `start`, `stop`, `timestart`, `restarttime`, `update_time`)
    - **Integer-like** (e.g., `stride`, `timestride`, `timecount`, `count`)
    - **WW3 boolean** (T/F)
    - **Enum-like flags** (e.g., `F/T/H/C`)  decide whether to convert now or defer
    - **True strings** (file paths, names, prefixes, format strings)  explicitly exclude
  - Mark each row with **confidence** (High/Med/Low) and rationale (validator present? WW3 docs? used in tests?).

  **Must NOT do**:
  - Do not change code yet.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: broad scanning + careful classification.
  - **Skills**: []

  **Parallelization**:
  - Can Run In Parallel: YES
  - Parallel Group: Wave 1
  - Blocks: Tasks 6-12 (conversion work)
  - Blocked By: None

  **References**:
  - `src/rompy_ww3/namelists/` (all models)
  - `src/rompy_ww3/namelists/validation.py` (canonical allowed values)
  - `src/rompy_ww3/namelists/basemodel.py` (`_is_date_field`, `boolean_to_string`, `string_to_boolean`)

  **Acceptance Criteria**:
  - [ ] Inventory table is produced and saved to `.sisyphus/evidence/task-02-field-inventory.md`.
  - [ ] Each conversion candidate includes a confidence score and rationale.

  **QA Scenarios**:
  ```
  Scenario: Generate candidate inventory table
    Tool: Bash
    Steps:
      1. Grep for type annotations containing `Optional[str]` in `src/rompy_ww3/namelists/`.
      2. Compile matches into a table grouped by file.
      3. Manually classify top 30 highest-confidence candidates (dates/strides).
    Expected Result: A markdown table of candidates exists.
    Evidence: .sisyphus/evidence/task-02-field-inventory.md

  Scenario: Identify explicit exclusion list
    Tool: Bash
    Steps:
      1. Search for fields containing `filename`, `file`, `path`, `prefix`, `format`, `name`.
      2. Add them to an exclusion list unless strong evidence suggests otherwise.
    Expected Result: Exclusion list is documented.
    Evidence: .sisyphus/evidence/task-02-exclusions.txt
  ```

- [x] 3. Establish test + namelist output baseline (golden outputs)

  **What to do**:
  - Run the full test suite to ensure current branch baseline is green.
  - Generate representative namelist outputs from tests/examples and store them as golden artifacts for diffing.
  - Decide on a golden-output mechanism:
    - Prefer storing under `.sisyphus/evidence/golden/` (agent artifact) and diffing in CI/task QA.

  **Must NOT do**:
  - Do not change code.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - Can Run In Parallel: YES
  - Parallel Group: Wave 1
  - Blocks: Tasks 6-12 (must prove no regressions)
  - Blocked By: None

  **References**:
  - `Makefile` targets: `make test` (per repo docs)
  - `tests/` (where namelist outputs are created/validated)

  **Acceptance Criteria**:
  - [ ] Baseline test run passes.
  - [ ] Golden namelist outputs exist for later diffing.

  **QA Scenarios**:
  ```
  Scenario: Run baseline test suite
    Tool: Bash
    Steps:
      1. Run `make test`.
      2. Save terminal output.
    Expected Result: Exit code 0.
    Evidence: .sisyphus/evidence/task-03-make-test.txt

  Scenario: Generate baseline namelist artifacts
    Tool: Bash
    Preconditions: Identify at least 2 test cases or examples that render namelists.
    Steps:
      1. Run the commands/scripts that generate namelists (from tests/examples).
      2. Copy the produced `*.nml` files into `.sisyphus/evidence/golden/`.
    Expected Result: Golden files are present and readable.
    Evidence: .sisyphus/evidence/task-03-golden-file-list.txt
  ```

- [x] 4. Decide and document conversion rules + backward compatibility policy

  **What to do**:
  - Define explicit criteria for converting a `str` field:
    - Date -> `datetime` (with parsing from WW3 string)
    - T/F -> `bool` (with parsing from string)
    - Numeric strings -> `int`
    - Multi-valued flags -> Enum or keep as validated `str`
  - Document timezone policy for `datetime` (recommend: naive only; reject aware).
  - Define whether Enum conversions are in-scope now or deferred.

  **Must NOT do**:
  - Do not refactor validation duplication yet.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - Can Run In Parallel: YES
  - Parallel Group: Wave 1 (after tasks 1-2)
  - Blocks: Tasks 612
  - Blocked By: Task 2

  **References**:
  - `src/rompy_ww3/namelists/validation.py`  allowed values and existing validation rules
  - `src/rompy_ww3/namelists/basemodel.py`  current bool serialization and date heuristics

  **Acceptance Criteria**:
  - [ ] A short policy doc exists at `.sisyphus/evidence/task-04-conversion-policy.md`.

  **QA Scenarios**:
  ```
  Scenario: Draft conversion policy
    Tool: Bash
    Steps:
      1. Write down conversion rules with examples of accepted inputs and rendered outputs.
      2. Include explicit exclusions and deferrals.
    Expected Result: Policy document is complete and unambiguous.
    Evidence: .sisyphus/evidence/task-04-conversion-policy.md
  ```

- [x] 5. Add `datetime` rendering support in namelist formatting layer

  **What to do**:
  - Extend the namelist rendering path to correctly render `datetime` values as WW3 `YYYYMMDD HHMMSS`.
  - Ensure behavior is identical whether input is string date or `datetime`.
  - Add unit tests specifically for `datetime` -> rendered string.

  **Must NOT do**:
  - Do not convert any model fields yet (this is foundational).

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: touches central rendering logic; must avoid regressions.
  - **Skills**: []

  **Parallelization**:
  - Can Run In Parallel: NO
  - Parallel Group: Wave 2 (foundation)
  - Blocks: Tasks 6-8 (date conversions)
  - Blocked By: Tasks 1, 3

  **References**:
  - `src/rompy_ww3/namelists/basemodel.py:process_value()`
  - `src/rompy_ww3/namelists/basemodel.py:validate_date_format()` (or canonical helper)
  - `src/rompy_ww3/namelists/validation.py:validate_date_format()`

  **Acceptance Criteria**:
  - [ ] A test demonstrates `datetime(2020,1,2,3,4,5)` renders as `20200102 030405` in namelist output.
  - [ ] Full test suite passes.

  **QA Scenarios**:
  ```
  Scenario: Prove datetime renders correctly
    Tool: Bash
    Steps:
      1. Run the new/updated unit test targeting datetime rendering.
      2. Render a small namelist containing a datetime field and capture output.
    Expected Result: Output contains `YYYYMMDD HHMMSS` (no ISO8601, no timezone suffix).
    Evidence: .sisyphus/evidence/task-05-datetime-render.txt

  Scenario: Regression check
    Tool: Bash
    Steps:
      1. Run `make test`.
    Expected Result: Exit code 0.
    Evidence: .sisyphus/evidence/task-05-make-test.txt
  ```

- [ ] 6. Convert high-confidence date fields in DOMAIN/OUTPUT_DATE/TRACK/RESTART models

  **What to do**:
  - Using the inventory, convert only high-confidence date fields currently validated as dates.
  - Add `before` validators to accept existing string inputs and parse to `datetime`.
  - Ensure `set_default_dates()` still works (it currently assigns strings; must be reconciled with typed fields).

  **Must NOT do**:
  - Do not touch fields that may accept both keywords and dates (keep as `str` or `Union`).

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - Can Run In Parallel: YES (by file)
  - Parallel Group: Wave 3
  - Blocks: Later integration verification
  - Blocked By: Task 5

  **References**:
  - `src/rompy_ww3/namelists/output_date.py`
  - `src/rompy_ww3/namelists/domain.py`
  - `src/rompy_ww3/namelists/track.py`
  - `src/rompy_ww3/namelists/restart.py`
  - `src/rompy_ww3/namelists/restartupdate.py`

  **Acceptance Criteria**:
  - [ ] Existing tests and examples that previously supplied date strings still load.
  - [ ] Namelist output for those models matches golden outputs (or differs only in expected, reviewed ways).
  - [ ] `make test` passes.

  **QA Scenarios**:
  ```
  Scenario: Backward-compatible date parsing
    Tool: Bash
    Steps:
      1. Instantiate models using existing string date inputs from tests/examples.
      2. Render namelists.
    Expected Result: Rendered dates are in WW3 format.
    Evidence: .sisyphus/evidence/task-06-date-parse-render.txt

  Scenario: Golden diff
    Tool: Bash
    Steps:
      1. Re-generate the same namelists as Task 3.
      2. Diff against `.sisyphus/evidence/golden/`.
    Expected Result: No unexpected diffs.
    Evidence: .sisyphus/evidence/task-06-golden-diff.txt
  ```

- [ ] 7. Convert high-confidence stride/count fields (string 7 int)

  **What to do**:
  - Convert clearly numeric fields (e.g., `timestride`, `timecount`, `stride`, `count`) to `int`.
  - Accept numeric strings via `before` validators.
  - Ensure rendering produces unquoted integers (not `'123'`).

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - Can Run In Parallel: YES (by file)
  - Parallel Group: Wave 3
  - Blocks: Integration verification
  - Blocked By: Task 3

  **References**:
  - `src/rompy_ww3/namelists/track.py` (timestride/timecount)
  - `src/rompy_ww3/namelists/output_date.py` (stride)
  - Other inventory-identified models

  **Acceptance Criteria**:
  - [ ] Rendering output uses numeric literals (no quotes).
  - [ ] All affected tests pass.

  **QA Scenarios**:
  ```
  Scenario: Numeric stride renders unquoted
    Tool: Bash
    Steps:
      1. Create model with `stride="3600"` (string) and render.
      2. Create model with `stride=3600` (int) and render.
    Expected Result: Both render as `... = 3600` (no quotes).
    Evidence: .sisyphus/evidence/task-07-int-render.txt
  ```

- [ ] 8. Convert WW3 T/F string booleans to `bool` where truly boolean

  **What to do**:
  - Identify fields that are genuine WW3 booleans (values limited to T/F) and convert to `bool`.
  - Ensure parsing accepts `'T'/'F'` strings AND Python bool values.
  - Verify rendering outputs `T/F` (not quoted).

  **Must NOT do**:
  - Do not convert multi-valued flags like forcing selectors (`F/T/H/C`) to bool.

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []

  **Parallelization**:
  - Can Run In Parallel: YES (by file group)
  - Parallel Group: Wave 3
  - Blocks: Integration verification
  - Blocked By: Task 3

  **References**:
  - `src/rompy_ww3/namelists/basemodel.py:boolean_to_string()`
  - Any field validators currently calling `validate_ww3_boolean`

  **Acceptance Criteria**:
  - [ ] Fields accept both `True/False` and `'T'/'F'` inputs.
  - [ ] Rendered namelists contain bare `T`/`F` tokens in the right positions.
  - [ ] Full test suite passes.

  **QA Scenarios**:
  ```
  Scenario: Boolean parsing and rendering
    Tool: Bash
    Steps:
      1. Instantiate a model with a boolean field set to `'T'` and render.
      2. Instantiate the same model with the field set to `True` and render.
      3. Compare outputs.
    Expected Result: Both render with `= T` (no quotes).
    Evidence: .sisyphus/evidence/task-08-bool-render.txt
  ```

- [ ] 9. Reconcile `set_default_dates()` with typed date fields

  **What to do**:
  - Update default-date setting logic to set `datetime` values where fields are typed as datetime.
  - Ensure nested models still have defaults applied correctly.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`

  **Parallelization**:
  - Can Run In Parallel: NO
  - Parallel Group: Wave 3 (after date conversions)
  - Blocks: Final verification
  - Blocked By: Task 6

  **References**:
  - `src/rompy_ww3/namelists/basemodel.py:set_default_dates()`
  - `src/rompy_ww3/namelists/basemodel.py:_is_date_field()`

  **Acceptance Criteria**:
  - [ ] A test proves defaults are applied correctly for a datetime-typed field.
  - [ ] No regression in existing behavior.

  **QA Scenarios**:
  ```
  Scenario: Default dates applied with typed fields
    Tool: Bash
    Steps:
      1. Create a model with date fields set to None.
      2. Call `set_default_dates(period)`.
      3. Render and verify formatted WW3 dates appear.
    Expected Result: Render contains expected start/stop values.
    Evidence: .sisyphus/evidence/task-09-default-dates.txt
  ```

- [ ] 10. Golden output regeneration and diff review

  **What to do**:
  - Re-generate the golden namelist outputs after all conversions.
  - Perform a diff and either:
    - Confirm byte-for-byte identical outputs, or
    - Document and justify any expected diffs (ideally none).

  **Recommended Agent Profile**:
  - **Category**: `quick`

  **Parallelization**:
  - Can Run In Parallel: YES
  - Parallel Group: Wave 4
  - Blocks: Final verification wave
  - Blocked By: Tasks 6-9

  **Acceptance Criteria**:
  - [ ] Diff is clean or reviewed/approved.

  **QA Scenarios**:
  ```
  Scenario: Golden diff is clean
    Tool: Bash
    Steps:
      1. Re-run the golden output generation workflow.
      2. Diff the resulting files against the baseline.
    Expected Result: No diffs (or diffs explained in an evidence note).
    Evidence: .sisyphus/evidence/task-10-golden-diff.txt
  ```

- [ ] 11. Update docs/examples minimally (only if required by typed inputs)

  **What to do**:
  - If example configs or docs show date/boolean fields as strings in a way that no longer works, update them.
  - Prefer backward compatibility so updates are minimal.

  **Recommended Agent Profile**:
  - **Category**: `writing`

  **Parallelization**:
  - Can Run In Parallel: YES
  - Parallel Group: Wave 4
  - Blocks: None
  - Blocked By: Tasks 6-8

  **Acceptance Criteria**:
  - [ ] Examples continue to validate/run under the new typing rules.

  **QA Scenarios**:
  ```
  Scenario: Validate example configs
    Tool: Bash
    Steps:
      1. Run example validation command(s) (e.g., via CLI or tests).
    Expected Result: Examples load successfully.
    Evidence: .sisyphus/evidence/task-11-examples-validate.txt
  ```

---

## Final verification wave (run in parallel after all tasks)

- [ ] F1. Plan compliance audit — `oracle`
  Verify: (1) converted only high-confidence fields, (2) no scope creep (paths/names unchanged), (3) evidence files exist, (4) golden diffs clean or justified.

- [ ] F2. Code quality review — `unspecified-high`
  Run lint/type checks and `make test`. Ensure no `as any` / suppressed errors / duplicated helpers refactored unintentionally.

- [ ] F3. Regression QA run — `unspecified-high`
  Re-run all QA scenarios from the tasks, ensuring evidence present under `.sisyphus/evidence/`.

- [ ] F4. Scope fidelity check — `deep`
  Confirm changes are limited to typed-field conversions + rendering/test updates only.

---

## Commit strategy
- Prefer small, reviewable commits aligned to the critical milestones:
  1) Rendering support for `datetime`
  2) Date field conversions
  3) Int conversions
  4) Bool conversions
  5) Golden diff + tests

---

## Success criteria
- All tests pass (`make test`).
- Namelist rendering remains WW3-compliant, and baseline golden outputs are unchanged (or diffs are minimal and justified).
- Existing configs using string inputs continue to load (backward-compatible parsing).
- PR feedback addressed with a clear inventory + incremental, low-risk conversions.
