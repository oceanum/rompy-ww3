# WW3 Output Transfer Postprocessor (rompy-ww3 + rompy-core) — Work Plan

## TL;DR

> Implement a **WW3 postprocessor** in **rompy-ww3** that (1) discovers WW3 outputs by **manifest-from-namelists** and (2) computes **target names** (datestamped; restart uses **valid-date**), then delegates copying/uploading to multiple **destination prefixes** using **rompy-core transfer entrypoints** (`rompy.transfer`).

**Deliverables**
- rompy-core (`../../rompy/transfer_entrypoint`): `TransferManager` helper that fans out local files to multiple destination prefixes via existing `rompy.transfer` backends.
- rompy-ww3: `WW3TransferPostprocessor` registered under `rompy.postprocess` that selects outputs, computes names, invokes `TransferManager`, and (optionally) prunes old restart files on destinations.
- Optional: restart retention via **rompy-ops** if installed; transfer-only path must work without it.

**Estimated effort**: Large
**Parallel execution**: YES (waves)
**Critical path**: TransferManager → WW3 naming/manifest → Postprocessor wiring → Integration tests

---

## Context

### Original request (as executed)
Create a rompy postprocessor for WW3 that transfers/uploads WW3 output files to one or more destinations with datestamped filenames. For restarts, the datestamp must use the **valid date** so subsequent runs can copy the restart file into place.

### Key decisions (confirmed)
- **Authoritative architecture**: TransferManager + `rompy.transfer` entrypoints (NOT the older uploader-based plan).
- **Sources**: always local files produced by WW3.
- **Destinations**: treated as **prefixes** (folder-like). Final object URI is `join_prefix(dest_prefix, target_filename)`.
- **Discovery**: **manifest-from-namelists** (compute expected filenames/timestamps from WW3 namelists; do not rely on filesystem scanning as the primary method).
- **Naming enforcement**:
  - Non-restart outputs: enforce `YYYYMMDD_HHMMSS` (auto-normalize the target name if not datestamped).
  - Restart outputs: datestamp uses **valid date**.
- **Retention**: delete old restarts from **destinations only**, configurable (default 24h retention + minimum 2 files). Prune all restarts under destination prefix (list/filter/delete), not just ones uploaded in this run.
- **rompy-ops**: lifecycle/retention infra lives in rompy-ops and is **optional**. rompy-ww3 must work without rompy-ops installed.

### Repo facts (evidence)
- rompy-core transfer entrypoints:
  - Entry point group: `rompy.transfer`
  - Factory: `rompy.transfer.registry.get_transfer(uri_or_pathlike)` (scheme-based)
  - Interface: `rompy.transfer.base.TransferBase` with `put/get/exists/list/delete/stat`
- rompy postprocessor hook:
  - Entry point group: `rompy.postprocess`
  - Invoked via `ModelRun.postprocess()` calling `.process(model_run, **kwargs)`

---

## Work objectives

### Core objective
Provide a WW3 postprocessor that reliably transfers WW3 outputs to multiple destination prefixes via rompy-core transfer backends, enforcing consistent target naming (datestamped + restart valid-date), without implementing backend logic in rompy-ww3.

### Must have
- Multi-destination fan-out in a single call with aggregated results.
- Destinations treated as **prefixes**.
- Configurable failure policy: **continue** vs **fail-fast**.
- Manifest-from-namelists discovery (OUTPUT_DATE_NML-driven).
- Datestamp format enforcement `YYYYMMDD_HHMMSS`.
- Restart naming uses **valid date**.
- Restart retention pruning on destinations only (24h + min2 default).

### Must NOT have (guardrails)
- No new transfer backend implementations in rompy-ww3.
- No conversion/compression/encryption/catalog/db.
- No concurrency in v1 (sequential is fine).
- No hard dependency on rompy-ops.

---

## Verification strategy (MANDATORY)

> ZERO HUMAN INTERVENTION. All acceptance criteria must be agent-executable.

### Test decision
- **Infrastructure exists**: YES (pytest)
- **Automated tests**: tests-after (write unit tests alongside implementation)

### Evidence
Save command outputs to `.sisyphus/evidence/task-*-*.txt`.

---

## Execution strategy

### Parallel waves (high-level)

Wave 1 (rompy-core foundation): Tasks 1–6

Wave 2 (rompy-ww3 naming + manifest + postprocessor wiring): Tasks 7–13

Wave Ops (optional): Tasks TO1–TO4

Final verification: F1–F4

---

## TODOs

### Wave 1 — rompy-core (`../../rompy/transfer_entrypoint`)

- [ ] 1. Inventory transfer_entrypoint API and decide module placement

  **What to do**:
  - Confirm module location for new helper: `rompy/transfer/manager.py`.
  - Confirm public import surface in `rompy/transfer/__init__.py`.
  - Identify transfer_entrypoint test patterns to follow.

  **Acceptance Criteria**:
  - [ ] Decision recorded in evidence.

  **QA Scenarios**:
  ```
  Scenario: Locate transfer_entrypoint integration points
    Tool: Bash
    Steps:
      1. ls ../../rompy/transfer_entrypoint/src/rompy/transfer/
      2. python -c "from rompy.transfer.registry import get_transfer; print(get_transfer)"
    Expected Result: Directory listing succeeds; import prints a function.
    Evidence: .sisyphus/evidence/task-1-transfer-inventory.txt
  ```

- [x] 2. Define TransferManager public API + result types

  **What to do**:
  - Add `TransferFailurePolicy` enum: `CONTINUE`, `FAIL_FAST`.
  - Add dataclasses:
    - `TransferItemResult` (local_path, dest_prefix, target_name, dest_uri, ok, error)
    - `TransferBatchResult` (counts + items, helpers like all_succeeded)
  - Define `TransferManager.transfer_files(...)` signature + docstrings (prefix semantics).

  **Acceptance Criteria**:
  - [ ] `python -c "from rompy.transfer.manager import TransferManager, TransferFailurePolicy; print(TransferFailurePolicy.CONTINUE)"` succeeds.

  **QA Scenarios**:
  ```
  Scenario: Import TransferManager types
    Tool: Bash
    Steps:
      1. python -c "from rompy.transfer.manager import TransferManager, TransferFailurePolicy; print(TransferFailurePolicy.CONTINUE)"
    Expected Result: Imports succeed.
    Evidence: .sisyphus/evidence/task-2-transfermanager-import.txt
  ```

- [x] 3. Implement prefix URI join utility (backend-agnostic)

  **What to do**:
  - Implement `join_prefix(prefix: str, name: str) -> str`.
  - Handle `file://`, `s3://`, `gs://`, plain paths; avoid double slashes.

  **Acceptance Criteria**:
  - [ ] Tests for join behavior pass.

- [x] 4. Implement TransferManager.transfer_files fan-out (sequential)

  **What to do**:
  - For each destination prefix: resolve backend once via `get_transfer(dest_prefix)`.
  - For each file: `target_name = name_map[file]`, `dest_uri = join_prefix(dest_prefix, target_name)`.
  - Call `transfer.put(local_path, dest_uri)`.
  - Implement failure policies.
  - Return aggregated `TransferBatchResult`.

  **Acceptance Criteria**:
  - [ ] Can transfer 1 file to 2 local prefixes using FileTransfer.
  - [ ] CONTINUE records partial failures.
  - [ ] FAIL_FAST raises after first failure.

- [x] 5. Add TransferManager to public import surface

  **What to do**:
  - Export new types in `rompy.transfer.__init__`.

  **Acceptance Criteria**:
  - [ ] `python -c "from rompy.transfer import TransferManager"` works.

- [ ] 6. Dev-install transfer_entrypoint and smoke test

  **What to do**:
  - Run `uv pip install -e ../../rompy/transfer_entrypoint` in this workspace env.
  - Smoke import `TransferManager`.

  **Acceptance Criteria**:
  - [ ] Dev install succeeds and import works.

---

### Wave 2 — rompy-ww3 (`src/rompy_ww3/postprocess/`)

- [x] 7. Implement WW3 naming helpers (datestamp normalization + restart valid-date)
- [ ] 8. Implement manifest-from-namelists output selection
- [ ] 9. Implement `WW3TransferPostprocessor.process()` delegating to TransferManager
- [ ] 10. Register postprocessor entrypoint under `rompy.postprocess`
- [ ] 11. Add WW3-side config schema (destinations + failure policy + retention)
- [ ] 12. Hermetic integration test (FileTransfer destinations only)
- [ ] 13. Update minimal usage docs

---

### Wave Ops — optional rompy-ops lifecycle

- [ ] TO1. Create rompy-ops skeleton + optional dependency wiring
- [ ] TO2. Implement LifecycleTracker + JSON persistence
- [ ] TO3. Implement RetentionPolicy helpers
- [ ] TO4. Implement WW3 restart retention by destination listing

---

## Final verification wave

- [ ] F1. Plan compliance audit
- [ ] F2. Code quality review (lint/format/tests)
- [ ] F3. QA run (execute all QA scenarios + evidence)
- [ ] F4. Scope fidelity check

---

## Commit strategy

- Keep commits atomic and per-repo (rompy-core vs rompy-ww3).
- Do not commit `.sisyphus/` artifacts.
