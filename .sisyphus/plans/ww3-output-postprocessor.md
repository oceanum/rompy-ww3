# WW3 Output Upload Postprocessor - Work Plan

## TL;DR

**Objective**: Create a rompy postprocessor for WW3 that uploads model output files to multiple destinations (S3, GCS, filesystem, HTTP, Oceanum) with datestamped filenames.

**Architecture**: 
- **Generic components in rompy core**: Uploaders (CloudPath, HTTP), LifecycleManager, Retry logic, Base interfaces
- **WW3-specific in rompy-ww3**: File discovery (namelist parsing), Restart renaming, WW3UploadPostprocessor, Plugin registration

**Key Features**:
- Handles all 6 WW3 OutputType types: field, point, track, partition, coupling, restart
- Renames restart files from `restartN.ww3` to `restart.YYYYMMDD_HHMMSS.ww3` format using calculated valid dates
- Supports simultaneous upload to multiple destinations
- Implements retry logic with exponential backoff (via rompy core)
- Follows rompy backend postprocessor patterns
- **NEW**: Cloud storage via CloudPath (S3, GCS, Azure Blob) using fsspec (rompy core)
- **NEW**: Oceanum storage integration via oceanum-python library (rompy-ww3)
- **NEW**: Lifecycle management for restarts (retain last 24h, minimum 2 files) (via rompy core)
- **NEW**: Registered as rompy plugin via entrypoints

**Estimated Effort**: Large (7 waves, 20+ tasks) - assumes rompy core components available
**Parallel Execution**: YES - 4-6 tasks per wave
**Critical Path**: Config Schema → File Discovery → WW3-Specific Glue → Integration

---

## Context

### Original Request
Create a rompy postprocessor for handling uploading of WW3 output, including all types listed in OutputType, with datestamps in filenames. For restarts, use the valid date so subsequent runs can copy the file into place.

### Interview Summary

**Key Decisions Confirmed**:

1. **File Discovery**: Configuration-based - parse OutputType/Field/Point namelists to determine expected output files
2. **Restart Files**: WW3 produces `restart1.ww3`, `restart2.ww3`, etc. Postprocessor must rename to `restart.YYYYMMDD_HHMMSS.ww3`
3. **Valid Date Calculation**: For restart file N, valid date = startdate + stride × N
4. **Upload Config**: Separate configuration passed to `model_run.postprocess()`, not part of NMLConfig
5. **Multiple Destinations**: Support simultaneous upload to all configured destinations
6. **Failure Handling**: Continue with retry (exponential backoff), configurable failure severity
7. **Credentials**: Environment variables (AWS_ACCESS_KEY_ID, etc.)

**Research Findings**:

1. **WW3 Output Types** (`src/rompy_ww3/namelists/output_type.py`):
   - field: Gridded output (HS, DIR, SPR, etc.)
   - point: Point output at specific locations
   - track: Track output format
   - partition: Partitioned output regions
   - coupling: Coupled model exchange data
   - restart: Restart files for model continuation

2. **WW3 Date Format**: `'YYYYMMDD HHMMSS'` (e.g., `'20240115 120000'`)

3. **WW3 File Naming**:
   - Field: Prefix + date + `.nc` (e.g., `ww3.20240115.nc`)
   - Point: Similar to field
   - Restart: `restart.ww3` or numbered variants
   - Time splitting: Controls date inclusion (0=no date, 4=yearly, 6=monthly, 8=daily, 10=hourly)

4. **Rompy Postprocessor Pattern**:
   - Interface: `process(model_run, validate_outputs, output_dir, **kwargs) -> Dict[str, Any]`
   - Located in: `rompy.backends.postprocessors`
   - Current: `NoopPostprocessor` (placeholder)

5. **Component Architecture**:
   - Base: `WW3ComponentBaseModel` in `src/rompy_ww3/components/basemodel.py`
   - Provides: `render()`, `write_nml()`, `run_cmd`, `nml_filename`

### Metis Review Summary

**Identified Gaps Addressed**:
- File discovery algorithm: Configuration-based approach selected
- Restart file naming: Confirmed rename operation from restartN.ww3 format
- Valid date source: Formula provided (startdate + stride × N)
- Upload configuration: Separate config approach selected
- Failure handling: Retry with exponential backoff confirmed
- Credential strategy: Environment variables confirmed

**Scope Guardrails**:
- **INCLUDE**: Upload postprocessor, file discovery from config, restart renaming, retry logic
- **EXCLUDE**: Input data upload, file format conversion, compression, encryption, database cataloging

---

## Work Objectives

### Core Objective
Implement a rompy-compatible postprocessor that uploads WW3 output files to configured destinations with proper datestamped filenames and restart file handling.

### Concrete Deliverables

**Rompy Core (Prerequisites - assumed available)**:
1. **Upload Backend Modules** (`rompy.backends.uploaders`):
   - `CloudUploader`: Cloud storage via CloudPath (S3, GCS, Azure)
   - `HTTPUploader`: HTTP POST upload
   - `BaseUploader`: Base uploader interface

2. **Lifecycle Management** (`rompy.backends.lifecycle`):
   - `LifecycleManager`: Track files with timestamps
   - `RetentionPolicy`: Enforce retention rules (time-based, count-based)

3. **Retry Utilities** (`rompy.backends.retry`):
   - Retry decorator with exponential backoff
   - Transient error detection

**Rompy-WW3 (This Implementation)**:

1. **Configuration Module** (`src/rompy_ww3/postprocess/config.py`):
   - `WW3UploadConfig` - WW3-specific upload configuration
   - Destination configs referencing rompy core uploaders
   - File selection and filtering options

2. **File Discovery Module** (`src/rompy_ww3/postprocess/discovery.py`):
   - Parse OutputType/Field/Point namelists
   - Generate expected file patterns
   - Scan and validate file existence

3. **Oceanum Uploader** (`src/rompy_ww3/postprocess/uploaders/oceanum.py`):
   - `OceanumUploader` - Oceanum-specific uploader using oceanum-python
   - Datamesh integration

4. **Restart Handling Module** (`src/rompy_ww3/postprocess/restart.py`):
   - Calculate valid dates from namelist config
   - Rename restartN.ww3 files to dated format
   - Handle multiple restart files

5. **Postprocessor Module** (`src/rompy_ww3/postprocess/__init__.py`):
   - `WW3UploadPostprocessor` class
   - Integrates rompy core uploaders and lifecycle
   - WW3-specific orchestration logic

6. **Plugin Registration** (`pyproject.toml`):
   - Entrypoint for `rompy.postprocessors`
   - Registers `WW3UploadPostprocessor`

7. **Tests** (`tests/postprocess/`):
   - Unit tests for WW3-specific modules
   - Integration tests with mocked backends
   - Configuration validation tests

8. **Documentation** (`docs/postprocessing.md`):
   - Configuration examples
   - Usage guide
   - Troubleshooting

### Definition of Done
- [ ] All 6 OutputType types can be uploaded
- [ ] Restart files correctly renamed with valid dates
- [ ] Multiple destinations upload simultaneously
- [ ] Retry logic works with exponential backoff
- [ ] GCS upload via CloudPath works
- [ ] Oceanum storage upload works
- [ ] Lifecycle management retains last 24h with minimum 2 files
- [ ] All tests pass
- [ ] Documentation complete with examples

### Must Have
- Configuration-based file discovery
- Restart file renaming with valid date calculation
- Filesystem, cloud storage (via CloudPath/fsspec), HTTP, and Oceanum upload backends
- Retry logic with exponential backoff
- Configurable failure severity
- Environment variable credential handling
- Follow rompy postprocessor interface
- Lifecycle management for restart files (24h retention, min 2 files)
- Plugin registration via rompy entrypoints

### Must NOT Have
- Input data upload
- File format conversion
- Compression/encryption
- Database cataloging
- Email notifications
- Progress bars (logging only)
- Concurrent uploads (sequential only)

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (pytest)
- **Automated tests**: TDD-style (write tests first, then implementation)
- **Framework**: pytest with fixtures

### QA Policy
Every task MUST include agent-executed QA scenarios. Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

| Deliverable Type | Verification Tool | Method |
|------------------|-------------------|--------|
| Python modules | pytest | Run test files, assert PASS |
| Configuration | Python REPL | Import models, validate schema |
| File operations | Bash | List files, verify existence, check checksums |
| Integration | pytest | Mock backends, verify upload calls |

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation - can start immediately):
├── Task 1: Create postprocess package structure [quick]
├── Task 2: Define configuration schema (UploadConfig, Destinations) [deep]
├── Task 3: Implement base uploader interface [deep]
└── Task 4: Write test fixtures and mocks [quick]

Wave 2 (File Discovery - after Wave 1):
├── Task 5: Parse OutputType namelists [unspecified-high]
├── Task 6: Generate file patterns from config [unspecified-high]
├── Task 7: Implement file discovery scanner [unspecified-high]
└── Task 8: Write discovery tests [quick]

Wave 3 (Restart Handling - after Wave 1):
├── Task 9: Implement valid date calculation [deep]
├── Task 10: Implement restart file renaming [unspecified-high]
├── Task 11: Handle multiple restart files [quick]
└── Task 12: Write restart handling tests [quick]

**Prerequisites (Rompy Core) - Assumed Available:**
- `rompy.backends.uploaders.CloudUploader` - Cloud storage via CloudPath
- `rompy.backends.uploaders.HTTPUploader` - HTTP POST upload
- `rompy.backends.lifecycle.LifecycleManager` - File lifecycle tracking
- `rompy.backends.retry` - Retry decorators with exponential backoff

Wave 4 (WW3-Specific Uploaders - after Wave 1):
├── Task 13: Implement OceanumUploader with oceanum-python [unspecified-high]
├── Task 14: Write Oceanum uploader tests [quick]

Wave 5 (WW3 Core Postprocessor - after Waves 2, 3, 4):
├── Task 15: Implement WW3UploadPostprocessor class [deep]
├── Task 16: Integrate rompy core components [unspecified-high]
├── Task 17: Write integration tests [unspecified-high]

Wave 6 (Plugin & Documentation - after Wave 5):
├── Task 18: Add plugin registration via entrypoints [quick]
├── Task 19: Add config validation [quick]
├── Task 20: Write documentation [writing]
└── Task 21: Write end-to-end tests [unspecified-high]

Wave 7 (Final Review - after Wave 6):
├── Task F1: Code quality review (ruff, mypy) [quick]
├── Task F2: Run full test suite [quick]
├── Task F3: Verify documentation examples [unspecified-high]
└── Task F4: Check test coverage [quick]

Critical Path: Task 1 → Task 2 → Task 5 → Task 9 → Task 15 → Task 18 → F1-F4
Parallel Speedup: ~60% faster than sequential
Max Concurrent: 3-4 (Waves 2, 3)
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|------------|--------|------|
| 1 | None | 2, 3, 4, 5, 9 | 1 |
| 2 | 1 | 5, 13 | 1 |
| 3 | 1 | 13 | 1 |
| 4 | None | 8, 12, 14, 17, 21 | 1 |
| 5 | 1, 2 | 15 | 2 |
| 6 | 5 | 15 | 2 |
| 7 | 6 | 15 | 2 |
| 8 | 4, 7 | None | 2 |
| 9 | 1 | 10, 11 | 3 |
| 10 | 9 | 15 | 3 |
| 11 | 10 | 15 | 3 |
| 12 | 4, 11 | None | 3 |
| 13 | 2, 3 | 15 | 4 |
| 14 | 3, 4 | None | 4 |
| 15 | 5, 7, 10, 13 | 18 | 5 |
| 16 | 15 | 18 | 5 |
| 17 | 4, 16 | None | 5 |
| 18 | 15, 16 | 20 | 6 |
| 19 | 18 | None | 6 |
| 20 | 18 | None | 6 |
| 21 | 16 | None | 6 |

### Agent Dispatch Summary

| Wave | # Parallel | Tasks → Agent Category |
|------|------------|----------------------|
| 1 | 4 | T1, T4 → `quick`, T2 → `deep`, T3 → `deep` |
| 2 | 4 | T5-T7 → `unspecified-high`, T8 → `quick` |
| 3 | 4 | T9 → `deep`, T10-T12 → `unspecified-high/quick` |
| 4 | 2 | T13 → `unspecified-high`, T14 → `quick` |
| 5 | 3 | T15-T16 → `deep/unspecified-high`, T17 → `unspecified-high` |
| 6 | 4 | T18-T19 → `quick`, T20 → `writing`, T21 → `unspecified-high` |
| 7 | 4 | F1-F4 → `quick` |

---

## TODOs

### Wave 1: Foundation

- [x] **1. Create postprocess package structure**

  **What to do**:
  - Create `src/rompy_ww3/postprocess/` directory
  - Create `__init__.py` with package exports
  - Create subdirectories: `uploaders/`, tests in `tests/postprocess/`
  - Add `__init__.py` files in all subdirectories

  **Must NOT do**:
  - Don't implement any logic yet
  - Don't add dependencies to pyproject.toml yet

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: Simple directory creation and boilerplate

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3, 4)
  - **Blocks**: Tasks 5, 9, 13, 14, 15
  - **Blocked By**: None

  **References**:
  - `src/rompy_ww3/components/__init__.py` - Package structure pattern
  - `src/rompy_ww3/namelists/__init__.py` - Export pattern

  **Acceptance Criteria**:
  - [ ] Directory structure exists:
    - `src/rompy_ww3/postprocess/__init__.py`
    - `src/rompy_ww3/postprocess/config.py`
    - `src/rompy_ww3/postprocess/discovery.py`
    - `src/rompy_ww3/postprocess/restart.py`
    - `src/rompy_ww3/postprocess/uploaders/__init__.py`
    - `src/rompy_ww3/postprocess/uploaders/base.py`
    - `src/rompy_ww3/postprocess/uploaders/filesystem.py`
    - `src/rompy_ww3/postprocess/uploaders/s3.py`
    - `src/rompy_ww3/postprocess/uploaders/http.py`
    - `tests/postprocess/__init__.py`
    - `tests/postprocess/test_config.py`
    - `tests/postprocess/test_discovery.py`
    - `tests/postprocess/test_restart.py`
    - `tests/postprocess/test_uploaders.py`
    - `tests/postprocess/test_integration.py`

  **QA Scenarios**:
  ```
  Scenario: Verify package structure
    Tool: Bash
    Steps:
      1. ls -la src/rompy_ww3/postprocess/
      2. ls -la src/rompy_ww3/postprocess/uploaders/
      3. ls -la tests/postprocess/
    Expected Result: All directories and __init__.py files exist
    Evidence: .sisyphus/evidence/task-1-structure.txt
  ```

  **Commit**: YES
  - Message: `feat(postprocess): create package structure for upload postprocessor`
  - Files: All new files in src/rompy_ww3/postprocess/ and tests/postprocess/

---

- [x] **2. Define configuration schema**

  **What to do**:
  - Implement `UploadConfig` Pydantic model in `config.py`
  - Implement destination models: `FilesystemDestination`, `S3Destination`, `HTTPDestination`
  - Include file selection options (output types, patterns)
  - Include retry configuration (max_retries, backoff_factor)
  - Include failure severity setting

  **Must NOT do**:
  - Don't implement upload logic
  - Don't add credential fields (use env vars)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []
  - **Reason**: Requires careful Pydantic model design with validation

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3, 4)
  - **Blocks**: Tasks 5, 13, 14, 15
  - **Blocked By**: Task 1

  **References**:
  - `src/rompy_ww3/namelists/output_type.py` - Pydantic model patterns
  - `src/rompy_ww3/components/basemodel.py` - Base model patterns
  - `src/rompy_ww3/namelists/basemodel.py` - Validation patterns

  **Acceptance Criteria**:
  - [ ] `UploadConfig` model defined with:
    - `destinations: List[Destination]` field
    - `file_selection: FileSelection` field
    - `retry: RetryConfig` field
    - `failure_mode: Literal["strict", "lenient"]` field
  - [ ] Destination models defined:
    - `FilesystemDestination`: path, create_dirs
    - `S3Destination`: bucket, prefix, region, endpoint_url (optional)
    - `HTTPDestination`: url, headers, timeout
  - [ ] All models have proper Field descriptions and validation

  **QA Scenarios**:
  ```
  Scenario: Validate configuration schema
    Tool: Python REPL (Bash)
    Preconditions: Task 1 complete
    Steps:
      1. cd /home/user/repos/rompy-ww3 && python -c "from rompy_ww3.postprocess.config import UploadConfig, FilesystemDestination, S3Destination, HTTPDestination; print('Import OK')"
      2. python -c "from rompy_ww3.postprocess.config import UploadConfig; c = UploadConfig(destinations=[FilesystemDestination(path='/tmp/test')]); print(c.model_dump())"
    Expected Result: No import errors, model validates and dumps correctly
    Evidence: .sisyphus/evidence/task-2-config.py
  ```

  **Commit**: YES (group with Task 3)
  - Message: `feat(postprocess): add configuration models for upload destinations`
  - Files: `src/rompy_ww3/postprocess/config.py`

---

- [x] **3. Implement base uploader interface**

  **What to do**:
  - Create abstract base class `BaseUploader` in `uploaders/base.py`
  - Define interface: `upload(file_path, destination) -> UploadResult`
  - Define `UploadResult` dataclass with success, message, bytes_uploaded fields
  - Include logging hooks

  **Must NOT do**:
  - Don't implement concrete uploaders
  - Don't add destination-specific logic

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []
  - **Reason**: Interface design affects all uploaders

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 4)
  - **Blocks**: Tasks 13, 14, 15
  - **Blocked By**: Task 1

  **References**:
  - `src/rompy_ww3/components/basemodel.py` - Interface pattern
  - Python ABC module documentation

  **Acceptance Criteria**:
  - [ ] `BaseUploader` abstract class defined with `upload()` abstract method
  - [ ] `UploadResult` dataclass with fields: success (bool), message (str), bytes_uploaded (int)
  - [ ] Abstract method signature: `upload(self, file_path: Path, destination: Destination) -> UploadResult`

  **QA Scenarios**:
  ```
  Scenario: Verify base uploader interface
    Tool: Python REPL (Bash)
    Steps:
      1. python -c "from rompy_ww3.postprocess.uploaders.base import BaseUploader, UploadResult; print('Import OK')"
      2. python -c "from rompy_ww3.postprocess.uploaders.base import UploadResult; r = UploadResult(success=True, message='test', bytes_uploaded=100); print(r)"
    Expected Result: Imports work, UploadResult can be instantiated
    Evidence: .sisyphus/evidence/task-3-interface.py
  ```

  **Commit**: YES (group with Task 2)

---

- [x] **4. Write test fixtures and mocks**

  **What to do**:
  - Create pytest fixtures in `tests/postprocess/conftest.py`
  - Create mock uploaders for testing
  - Create sample WW3 output files for testing
  - Create mock namelist configurations

  **Must NOT do**:
  - Don't write actual tests yet
  - Don't implement real upload logic

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: Test infrastructure setup

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3)
  - **Blocks**: Tasks 8, 12, 16, 20, 24
  - **Blocked By**: None

  **References**:
  - `tests/conftest.py` - Existing fixture patterns
  - `tests/test_config.py` - Test patterns

  **Acceptance Criteria**:
  - [ ] `conftest.py` created with fixtures:
    - `mock_output_dir` - Temporary directory with sample files
    - `sample_upload_config` - Valid UploadConfig instance
    - `mock_namelist_config` - Sample WW3 namelist data
    - `mock_s3_client` - Mocked boto3 client
    - `mock_http_server` - HTTP server fixture

  **QA Scenarios**:
  ```
  Scenario: Verify fixtures work
    Tool: pytest
    Steps:
      1. python -m pytest tests/postprocess/conftest.py -v --collect-only
    Expected Result: Fixtures are collected without errors
    Evidence: .sisyphus/evidence/task-4-fixtures.txt
  ```

  **Commit**: YES
  - Message: `test(postprocess): add test fixtures and mocks`

---

### Wave 2: File Discovery

- [ ] **5. Parse OutputType namelists**

  **What to do**:
  - Implement parser for OutputType namelist in `discovery.py`
  - Extract: field.list, point.file, track.format, partition settings, coupling settings, restart settings
  - Handle optional fields (some output types may not be configured)

  **Must NOT do**:
  - Don't implement file scanning yet
  - Don't handle file patterns yet

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: Requires understanding WW3 namelist structure

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 7, 8)
  - **Blocks**: Task 17
  - **Blocked By**: Tasks 1, 2

  **References**:
  - `src/rompy_ww3/namelists/output_type.py` - OutputType model
  - `src/rompy_ww3/namelists/field.py` - Field output model
  - `src/rompy_ww3/namelists/point.py` - Point output model

  **Acceptance Criteria**:
  - [ ] Function `parse_output_type(output_type: OutputType) -> Dict[str, Any]` implemented
  - [ ] Returns dict with all 6 output types and their configurations
  - [ ] Handles None values gracefully (unconfigured output types)

  **QA Scenarios**:
  ```
  Scenario: Parse sample OutputType
    Tool: pytest
    Preconditions: Task 4 complete
    Steps:
      1. Create test with sample OutputType(field=OutputTypeField(list="HS DIR"))
      2. Call parse_output_type()
      3. Verify returned dict has field key with correct config
    Expected Result: Parser extracts field configuration correctly
    Evidence: .sisyphus/evidence/task-5-parser.txt
  ```

  **Commit**: YES
  - Message: `feat(postprocess): add OutputType namelist parser`

---

- [ ] **6. Generate file patterns from config**

  **What to do**:
  - Implement pattern generator in `discovery.py`
  - Generate glob patterns based on:
    - Output type (field, point, etc.)
    - Prefix configuration (from File namelist)
    - Time splitting option (0, 4, 6, 8, 10)
  - Handle restart files specially (restart.ww3, restart1.ww3, etc.)

  **Must NOT do**:
  - Don't scan filesystem yet
  - Don't verify file existence

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: Logic for pattern generation from config

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 5, 7, 8)
  - **Blocks**: Task 17
  - **Blocked By**: Task 5

  **References**:
  - `src/rompy_ww3/namelists/output_file.py` - File prefix configuration
  - `src/rompy_ww3/namelists/field.py` - Time splitting options

  **Acceptance Criteria**:
  - [ ] Function `generate_file_patterns(namelist_config) -> List[str]` implemented
  - [ ] Returns glob patterns like `ww3.*.nc`, `points.*.nc`, `restart*.ww3`
  - [ ] Handles different time splitting options correctly

  **QA Scenarios**:
  ```
  Scenario: Generate patterns for different configs
    Tool: pytest
    Steps:
      1. Test with prefix="ww3.", timesplit=8 (daily) → expect "ww3.*.nc"
      2. Test with prefix="points.", timesplit=0 → expect "points.*.nc"
      3. Test with restart enabled → expect "restart*.ww3"
    Expected Result: Correct patterns generated for each case
    Evidence: .sisyphus/evidence/task-6-patterns.txt
  ```

  **Commit**: YES (group with Task 7)

---

- [ ] **7. Implement file discovery scanner**

  **What to do**:
  - Implement scanner in `discovery.py`
  - Scan output directory using generated patterns
  - Return list of discovered files with metadata (path, size, type)
  - Handle missing files gracefully (log warning, don't fail)

  **Must NOT do**:
  - Don't upload files yet
  - Don't verify file contents

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: File system scanning with error handling

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 5, 6, 8)
  - **Blocks**: Task 17
  - **Blocked By**: Task 6

  **References**:
  - Python `pathlib.Path.glob()` documentation
  - Python `os.path.getsize()` for file size

  **Acceptance Criteria**:
  - [ ] Function `discover_files(output_dir, patterns) -> List[DiscoveredFile]` implemented
  - [ ] Returns list of `DiscoveredFile` objects with path, size, type
  - [ ] Handles glob patterns correctly
  - [ ] Logs warnings for expected but missing files

  **QA Scenarios**:
  ```
  Scenario: Discover files in test directory
    Tool: pytest
    Preconditions: Task 4 complete (fixtures create test files)
    Steps:
      1. Create test files: ww3.20240101.nc, points.20240101.nc, restart.ww3
      2. Call discover_files() with patterns
      3. Verify all 3 files are discovered with correct metadata
    Expected Result: All files discovered with correct types and sizes
    Evidence: .sisyphus/evidence/task-7-discovery.txt
  ```

  **Commit**: YES (group with Task 6)

---

- [ ] **8. Write discovery tests**

  **What to do**:
  - Write comprehensive tests in `tests/postprocess/test_discovery.py`
  - Test pattern generation for all output types
  - Test file discovery with various configurations
  - Test handling of missing files

  **Must NOT do**:
  - Don't test upload logic
  - Don't use real S3/HTTP

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: Unit tests for discovery module

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 5, 6, 7)
  - **Blocks**: None
  - **Blocked By**: Tasks 4, 7

  **Acceptance Criteria**:
  - [ ] Tests for `parse_output_type()` with all 6 output types
  - [ ] Tests for `generate_file_patterns()` with various configs
  - [ ] Tests for `discover_files()` with mock directory
  - [ ] All tests pass: `pytest tests/postprocess/test_discovery.py -v`

  **QA Scenarios**:
  ```
  Scenario: Run discovery tests
    Tool: pytest
    Steps:
      1. python -m pytest tests/postprocess/test_discovery.py -v
    Expected Result: All tests PASS
    Evidence: .sisyphus/evidence/task-8-tests.txt
  ```

  **Commit**: YES
  - Message: `test(postprocess): add discovery module tests`

---

### Wave 3: Restart Handling

- [ ] **9. Implement valid date calculation**

  **What to do**:
  - Implement in `restart.py`
  - Parse OutputDate.restart.start (format: 'YYYYMMDD HHMMSS')
  - Parse OutputDate.restart.stride (in seconds)
  - Calculate valid date for restart N: start + stride × N
  - Return datetime object or formatted string

  **Must NOT do**:
  - Don't rename files yet
  - Don't handle file operations

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []
  - **Reason**: Date math with WW3 format

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 10, 11, 12)
  - **Blocks**: Tasks 10, 11
  - **Blocked By**: Task 1

  **References**:
  - `src/rompy_ww3/namelists/output_date.py` - OutputDateRestart model
  - Python `datetime` module documentation
  - WW3 date format: 'YYYYMMDD HHMMSS'

  **Acceptance Criteria**:
  - [ ] Function `calculate_restart_valid_date(start: str, stride: str, n: int) -> datetime` implemented
  - [ ] Correctly parses 'YYYYMMDD HHMMSS' format
  - [ ] Correctly adds stride (seconds) × N to start date
  - [ ] Handles edge cases (DST, leap years)

  **QA Scenarios**:
  ```
  Scenario: Calculate valid dates
    Tool: pytest
    Steps:
      1. Test: start='20240101 000000', stride='86400', n=1 → expect 2024-01-02 00:00:00
      2. Test: start='20240101 120000', stride='3600', n=5 → expect 2024-01-01 17:00:00
      3. Test leap year: start='20240228 000000', stride='86400', n=1 → expect 2024-02-29
    Expected Result: All calculations correct
    Evidence: .sisyphus/evidence/task-9-dates.txt
  ```

  **Commit**: YES
  - Message: `feat(postprocess): add restart valid date calculation`

---

- [ ] **10. Implement restart file renaming**

  **What to do**:
  - Implement in `restart.py`
  - Find restart files matching pattern `restart*.ww3`
  - Parse restart number from filename (e.g., restart1.ww3 → N=1)
  - Calculate valid date using Task 9 function
  - Rename to `restart.YYYYMMDD_HHMMSS.ww3` format
  - Handle errors (file not found, permission denied)

  **Must NOT do**:
  - Don't move files between directories (keep in place, rename only)
  - Don't delete original files until confirmed

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: File operations with error handling

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 9, 11, 12)
  - **Blocks**: Task 17
  - **Blocked By**: Task 9

  **References**:
  - Python `pathlib.Path.rename()` documentation
  - Python `shutil.move()` for cross-device moves

  **Acceptance Criteria**:
  - [ ] Function `rename_restart_files(output_dir, namelist_config) -> List[Path]` implemented
  - [ ] Finds all restart*.ww3 files
  - [ ] Renames each to `restart.YYYYMMDD_HHMMSS.ww3` format
  - [ ] Returns list of new file paths
  - [ ] Handles errors gracefully with logging

  **QA Scenarios**:
  ```
  Scenario: Rename restart files
    Tool: pytest
    Preconditions: Task 4 complete
    Steps:
      1. Create test files: restart1.ww3, restart2.ww3
      2. Set namelist: start='20240101 000000', stride='86400'
      3. Call rename_restart_files()
      4. Verify: restart.20240102_000000.ww3, restart.20240103_000000.ww3 exist
    Expected Result: Files renamed correctly with valid dates
    Evidence: .sisyphus/evidence/task-10-rename.txt
  ```

  **Commit**: YES (group with Task 11)

---

- [ ] **11. Handle multiple restart files**

  **What to do**:
  - Extend Task 10 to handle multiple restart files
  - Sort restart files by number (restart1, restart2, etc.)
  - Process in order, calculating correct valid date for each
  - Handle case where restart files have gaps (restart1, restart3, no restart2)

  **Must NOT do**:
  - Don't assume continuous numbering
  - Don't skip files with unexpected names

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: Extension of Task 10

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 9, 10, 12)
  - **Blocks**: Task 17
  - **Blocked By**: Task 10

  **Acceptance Criteria**:
  - [ ] Correctly handles restart1, restart2, restart3, etc.
  - [ ] Calculates unique valid date for each restart file
  - [ ] Handles gaps in numbering gracefully
  - [ ] Logs warnings for unexpected files

  **QA Scenarios**:
  ```
  Scenario: Handle multiple restarts with gaps
    Tool: pytest
    Steps:
      1. Create: restart1.ww3, restart3.ww3 (skip restart2)
      2. Process with stride=86400
      3. Verify: restart.20240102_000000.ww3, restart.20240104_000000.ww3
    Expected Result: Correct dates for N=1 and N=3, gap handled
    Evidence: .sisyphus/evidence/task-11-multi.txt
  ```

  **Commit**: YES (group with Task 10)

---

- [ ] **12. Write restart handling tests**

  **What to do**:
  - Write tests in `tests/postprocess/test_restart.py`
  - Test valid date calculation for various scenarios
  - Test renaming with different configurations
  - Test error handling (missing files, bad permissions)

  **Must NOT do**:
  - Don't test other modules

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: Unit tests for restart module

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 9, 10, 11)
  - **Blocks**: None
  - **Blocked By**: Tasks 4, 11

  **Acceptance Criteria**:
  - [ ] Tests for date calculation with various start/stride/N combinations
  - [ ] Tests for renaming single and multiple files
  - [ ] Tests for error handling
  - [ ] All tests pass: `pytest tests/postprocess/test_restart.py -v`

  **QA Scenarios**:
  ```
  Scenario: Run restart tests
    Tool: pytest
    Steps:
      1. python -m pytest tests/postprocess/test_restart.py -v
    Expected Result: All tests PASS
    Evidence: .sisyphus/evidence/task-12-tests.txt
  ```

  **Commit**: YES
  - Message: `test(postprocess): add restart handling tests`

---

### Wave 4: Upload Backends

- [ ] **13. Implement FilesystemUploader**

  **What to do**:
  - Implement in `uploaders/filesystem.py`
  - Inherit from `BaseUploader`
  - Implement `upload(file_path, destination)` method
  - Copy file to destination path
  - Create destination directories if needed
  - Preserve file metadata (timestamps, permissions)

  **Must NOT do**:
  - Don't use shutil.copy without preserving metadata
  - Don't create symlinks (copy actual files)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: File copy with metadata preservation

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4 (with Tasks 14, 15, 16)
  - **Blocks**: Task 17
  - **Blocked By**: Tasks 2, 3

  **References**:
  - Python `shutil.copy2()` documentation (preserves metadata)
  - Python `pathlib.Path.mkdir()` with parents=True

  **Acceptance Criteria**:
  - [ ] `FilesystemUploader` class implements `upload()` method
  - [ ] Copies files with `shutil.copy2()` (preserves metadata)
  - [ ] Creates destination directories if needed
  - [ ] Returns `UploadResult` with success status
  - [ ] Handles errors (disk full, permission denied)

  **QA Scenarios**:
  ```
  Scenario: Upload file to filesystem
    Tool: pytest
    Steps:
      1. Create test file: /tmp/test_source/file.nc (100 bytes)
      2. Upload to /tmp/test_dest/
      3. Verify: /tmp/test_dest/file.nc exists
      4. Verify: size == 100 bytes
    Expected Result: File copied correctly
    Evidence: .sisyphus/evidence/task-13-filesystem.txt
  ```

  **Commit**: YES
  - Message: `feat(postprocess): add filesystem upload backend`

---

- [ ] **14. Implement CloudUploader with CloudPath/fsspec**

  **What to do**:
  - Implement in `uploaders/cloud.py`
  - Inherit from `BaseUploader`
  - Implement `upload(file_path, destination)` method
  - Use CloudPath library for cloud storage operations
  - Support multiple cloud backends: S3 (`s3://`), GCS (`gs://`), Azure Blob (`az://`)
  - Use environment variables for credentials:
    - S3: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
    - GCS: GOOGLE_APPLICATION_CREDENTIALS
    - Azure: AZURE_STORAGE_CONNECTION_STRING
  - Support custom endpoint URLs (for MinIO, etc.)

  **Must NOT do**:
  - Don't use boto3 directly (use CloudPath/fsspec)
  - Don't hardcode credentials
  - Don't require credentials in config

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: Unified cloud storage via CloudPath (S3, GCS, Azure)

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4 (with Tasks 13, 15, 16)
  - **Blocks**: Task 21
  - **Blocked By**: Tasks 2, 3

  **References**:
  - cloudpathlib documentation: `CloudPath`, `S3Path`, `GSPath`, `AzureBlobPath`
  - fsspec documentation for underlying filesystem operations
  - CloudPath authentication via environment variables

  **Acceptance Criteria**:
  - [ ] `CloudUploader` class implements `upload()` method
  - [ ] Uses CloudPath for cloud operations (no direct boto3)
  - [ ] Supports S3 (s3://), GCS (gs://), Azure (az://)
  - [ ] Supports environment variable credentials
  - [ ] Supports custom endpoint URLs
  - [ ] Returns `UploadResult` with success status
  - [ ] Handles cloud errors (bucket not found, auth errors)

  **QA Scenarios**:
  ```
  Scenario: Upload file to mocked S3 via CloudPath
    Tool: pytest (with moto mock)
    Steps:
      1. Mock S3 with moto
      2. Create bucket: test-bucket
      3. Upload file.nc to s3://test-bucket/prefix/ via CloudPath
      4. Verify file exists in bucket
    Expected Result: File uploaded via CloudPath abstraction
    Evidence: .sisyphus/evidence/task-14-cloud-s3.txt

  Scenario: Upload file to mocked GCS via CloudPath
    Tool: pytest (with fake-gcs-server or gcsfs mock)
    Steps:
      1. Mock GCS
      2. Create bucket: test-bucket
      3. Upload file.nc to gs://test-bucket/prefix/ via CloudPath
      4. Verify file exists in bucket
    Expected Result: File uploaded via CloudPath abstraction
    Evidence: .sisyphus/evidence/task-14-cloud-gcs.txt
  ```

  **Commit**: YES
  - Message: `feat(postprocess): add unified cloud storage uploader via CloudPath/fsspec`

---

- [ ] **15. Implement OceanumUploader with oceanum-python**

  **What to do**:
  - Implement in `uploaders/oceanum.py`
  - Inherit from `BaseUploader`
  - Implement `upload(file_path, destination)` method
  - Use oceanum-python library for Datamesh operations
  - Support token-based authentication (DATAMESH_TOKEN)
  - Upload to Oceanum Datamesh catalog

  **Must NOT do**:
  - Don't hardcode tokens
  - Don't require tokens in config

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: Oceanum integration with oceanum-python

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4 (with Tasks 13, 14, 16)
  - **Blocks**: Task 21
  - **Blocked By**: Tasks 2, 3

  **References**:
  - oceanum-python documentation: `oceanum.datamesh`
  - Oceanum authentication: `DATAMESH_TOKEN` environment variable

  **Acceptance Criteria**:
  - [ ] `OceanumUploader` class implements `upload()` method
  - [ ] Uses oceanum-python library for uploads
  - [ ] Supports DATAMESH_TOKEN environment variable
  - [ ] Uploads files to Oceanum Datamesh
  - [ ] Returns `UploadResult` with success status
  - [ ] Handles Oceanum API errors

  **QA Scenarios**:
  ```
  Scenario: Upload file to Oceanum (mocked)
    Tool: pytest (with requests mock)
    Steps:
      1. Mock Oceanum API endpoints
      2. Set DATAMESH_TOKEN env var
      3. Upload file.nc to Oceanum
      4. Verify API called with correct auth header
    Expected Result: File uploaded to Oceanum
    Evidence: .sisyphus/evidence/task-15-oceanum.txt
  ```

  **Commit**: YES
  - Message: `feat(postprocess): add Oceanum storage upload backend`

---

- [ ] **16. Implement HTTPUploader with requests**

  **What to do**:
  - Implement in `uploaders/http.py`
  - Inherit from `BaseUploader`
  - Implement `upload(file_path, destination)` method
  - Use requests library to POST file
  - Support custom headers (auth tokens, content-type)
  - Support timeout configuration
  - Handle response status codes

  **Must NOT do**:
  - Don't hardcode auth tokens
  - Don't ignore HTTP error status codes

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: HTTP upload with requests

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4 (with Tasks 13, 14, 15)
  - **Blocks**: Task 21
  - **Blocked By**: Tasks 2, 3

  **References**:
  - requests documentation: `requests.post()` with files
  - requests timeout handling

  **Acceptance Criteria**:
  - [ ] `HTTPUploader` class implements `upload()` method
  - [ ] Uses requests to POST file as multipart/form-data
  - [ ] Supports custom headers from config
  - [ ] Supports timeout configuration
  - [ ] Returns `UploadResult` with success status
  - [ ] Handles HTTP errors (4xx, 5xx)

  **QA Scenarios**:
  ```
  Scenario: Upload file via HTTP POST
    Tool: pytest (with httpserver fixture)
    Steps:
      1. Start mock HTTP server
      2. Upload file.nc to http://localhost:port/upload/
      3. Verify server received POST request with file
    Expected Result: File uploaded via HTTP
    Evidence: .sisyphus/evidence/task-16-http.txt
  ```

  **Commit**: YES
  - Message: `feat(postprocess): add HTTP upload backend`

---

- [ ] **17. Write uploader tests**

  **What to do**:
  - Write tests in `tests/postprocess/test_uploaders.py`
  - Test each uploader with mocked backends
  - Test error handling (network errors, auth failures)
  - Test upload result structure

  **Must NOT do**:
  - Don't test with real S3/GCS/HTTP (use mocks)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: Unit tests for uploaders

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4 (with Tasks 13, 14, 15, 16)
  - **Blocks**: None
  - **Blocked By**: Tasks 3, 4

  **Acceptance Criteria**:
  - [ ] Tests for FilesystemUploader with temp directories
  - [ ] Tests for CloudUploader with CloudPath (S3, GCS mocks)
  - [ ] Tests for OceanumUploader with requests mock
  - [ ] Tests for HTTPUploader with httpserver fixture
  - [ ] All tests pass: `pytest tests/postprocess/test_uploaders.py -v`

  **QA Scenarios**:
  ```
  Scenario: Run uploader tests
    Tool: pytest
    Steps:
      1. python -m pytest tests/postprocess/test_uploaders.py -v
    Expected Result: All tests PASS
    Evidence: .sisyphus/evidence/task-17-tests.txt
  ```

  **Commit**: YES
  - Message: `test(postprocess): add uploader tests`

---

### Wave 5: Lifecycle Management

- [ ] **18. Implement restart lifecycle tracking**

  **What to do**:
  - Implement in `lifecycle.py`
  - Track restart files with their valid dates
  - Store metadata: filename, valid_date, upload_timestamp, destination
  - Support persistent storage of lifecycle state (JSON file)

  **Must NOT do**:
  - Don't implement retention policy yet (Task 19)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []
  - **Reason**: State tracking and persistence

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 5 (with Tasks 19, 20)
  - **Blocks**: Task 19
  - **Blocked By**: Task 9

  **References**:
  - Python `json` module for state persistence
  - Python `datetime` for timestamp handling

  **Acceptance Criteria**:
  - [ ] `LifecycleTracker` class implemented
  - [ ] Tracks restart files with valid dates and timestamps
  - [ ] Persists state to JSON file
  - [ ] Can load previous state on startup

  **QA Scenarios**:
  ```
  Scenario: Track restart files
    Tool: pytest
    Steps:
      1. Create test restart files with valid dates
      2. Call LifecycleTracker.track()
      3. Verify state file created with correct metadata
      4. Load state and verify data integrity
    Expected Result: Files tracked correctly
    Evidence: .sisyphus/evidence/task-19-lifecycle-track.txt
  ```

  **Commit**: YES
  - Message: `feat(postprocess): add restart lifecycle tracking`

---

- [ ] **19. Implement retention policy enforcement**

  **What to do**:
  - Implement in `lifecycle.py`
  - Default policy: retain last 24h, minimum 2 files
  - Configurable: retention_hours, min_files, max_files
  - Apply policy per destination
  - Delete expired files from destinations
  - Log all deletions

  **Must NOT do**:
  - Don't delete files without logging
  - Don't delete below minimum count

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: Policy enforcement and cleanup

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 5 (with Tasks 18, 20)
  - **Blocks**: Task 21
  - **Blocked By**: Task 18

  **Acceptance Criteria**:
  - [ ] `RetentionPolicy` class with configurable parameters
  - [ ] Default: 24h retention, min 2 files
  - [ ] Enforces policy on each destination
  - [ ] Deletes expired files
  - [ ] Respects minimum file count
  - [ ] Logs all actions

  **QA Scenarios**:
  ```
  Scenario: Enforce retention policy
    Tool: pytest
    Steps:
      1. Create 5 restart files with various dates (some >24h old)
      2. Apply retention policy (24h, min 2)
      3. Verify old files deleted
      4. Verify at least 2 files remain
    Expected Result: Policy enforced correctly
    Evidence: .sisyphus/evidence/task-19-retention.txt
  ```

  **Commit**: YES
  - Message: `feat(postprocess): add restart retention policy enforcement`

---

- [ ] **20. Write lifecycle tests**

  **What to do**:
  - Write tests in `tests/postprocess/test_lifecycle.py`
  - Test lifecycle tracking
  - Test retention policy with various scenarios
  - Test edge cases (no files, all files expired)

  **Must NOT do**:
  - Don't test with real cloud storage

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: Unit tests for lifecycle

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 5 (with Tasks 18, 19)
  - **Blocks**: None
  - **Blocked By**: Tasks 4, 19

  **Acceptance Criteria**:
  - [ ] Tests for lifecycle tracking
  - [ ] Tests for retention policy (various scenarios)
  - [ ] Tests for edge cases
  - [ ] All tests pass: `pytest tests/postprocess/test_lifecycle.py -v`

  **QA Scenarios**:
  ```
  Scenario: Run lifecycle tests
    Tool: pytest
    Steps:
      1. python -m pytest tests/postprocess/test_lifecycle.py -v
    Expected Result: All tests PASS
    Evidence: .sisyphus/evidence/task-20-lifecycle-tests.txt
  ```

  **Commit**: YES
  - Message: `test(postprocess): add lifecycle management tests`

---

### Wave 6: Core Postprocessor

- [ ] **21. Implement WW3UploadPostprocessor class**

  **What to do**:
  - Implement in `postprocess/__init__.py`
  - Follow rompy postprocessor interface: `process(model_run, validate_outputs, output_dir, **kwargs)`
  - Integrate file discovery (Task 7)
  - Integrate restart renaming (Task 11)
  - Integrate lifecycle management (Task 19)
  - Integrate uploaders (Tasks 13-16)
  - Upload to all configured destinations
  - Return result dict with upload status

  **Must NOT do**:
  - Don't implement retry yet (Task 22)
  - Don't handle errors specially yet

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []
  - **Reason**: Core orchestration logic

  **Parallelization**:
  - **Can Run In Parallel**: YES (after prerequisites)
  - **Parallel Group**: Wave 6 (with Tasks 22, 23, 24)
  - **Blocks**: Task 25
  - **Blocked By**: Tasks 5, 7, 10, 13, 14, 15, 16, 19

  **References**:
  - `rompy.backends.postprocessors` interface pattern
  - Python typing: `Dict[str, Any]` return type

  **Acceptance Criteria**:
  - [ ] `WW3UploadPostprocessor` class with `process()` method
  - [ ] Method signature: `process(model_run, validate_outputs, output_dir, config)`
  - [ ] Discovers files using discovery module
  - [ ] Renames restart files using restart module
  - [ ] Uploads to all destinations
  - [ ] Returns result dict: `{success: bool, uploaded: List[str], failed: List[str], message: str}`

  **QA Scenarios**:
  ```
  Scenario: Run postprocessor end-to-end
    Tool: pytest (integration test)
    Preconditions: Tasks 4, 17 complete
    Steps:
      1. Create mock output directory with files
      2. Create upload config with filesystem destination
      3. Call WW3UploadPostprocessor().process()
      4. Verify files uploaded to destination
    Expected Result: All files uploaded, result dict correct
    Evidence: .sisyphus/evidence/task-21-core.txt
  ```

  **Commit**: YES
  - Message: `feat(postprocess): implement WW3UploadPostprocessor core`

---

- [ ] **22. Implement retry logic with exponential backoff**

  **What to do**:
  - Add retry decorator or wrapper in uploaders
  - Configurable max_retries (default 3)
  - Exponential backoff: 1s, 2s, 4s, 8s...
  - Only retry on transient errors (network, timeout)
  - Don't retry on auth errors or 4xx HTTP errors

  **Must NOT do**:
  - Don't retry indefinitely
  - Don't retry on permanent failures

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: []
  - **Reason**: Retry logic with backoff

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 6 (with Tasks 21, 23, 24)
  - **Blocks**: Task 25
  - **Blocked By**: Task 21

  **References**:
  - Python `functools.wraps` for decorators
  - Python `time.sleep()` for backoff

  **Acceptance Criteria**:
  - [ ] Retry decorator/wrapper implemented
  - [ ] Exponential backoff: 2^attempt seconds
  - [ ] Max retries configurable (default 3)
  - [ ] Only retries on transient errors
  - [ ] Logs retry attempts

  **QA Scenarios**:
  ```
  Scenario: Test retry on network failure
    Tool: pytest
    Steps:
      1. Mock uploader to fail twice, then succeed
      2. Call upload with retry
      3. Verify: upload called 3 times total
      4. Verify: final result is success
    Expected Result: Retries work, eventually succeeds
    Evidence: .sisyphus/evidence/task-22-retry.txt
  ```

  **Commit**: YES (group with Task 23)

---

- [ ] **23. Integrate all components**

  **What to do**:
  - Wire together all modules in postprocessor
  - Ensure file discovery → restart renaming → upload flow works
  - Add comprehensive logging
  - Handle edge cases (no files found, all uploads fail)

  **Must NOT do**:
  - Don't add new features
  - Just integrate existing pieces

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: Integration and logging

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 6 (with Tasks 21, 22, 24)
  - **Blocks**: Task 25
  - **Blocked By**: Tasks 21, 22

  **Acceptance Criteria**:
  - [ ] All modules wired together
  - [ ] Logging added at key points (discovery, renaming, upload)
  - [ ] Edge cases handled gracefully
  - [ ] No module-level imports fail

  **QA Scenarios**:
  ```
  Scenario: Verify integration
    Tool: pytest
    Steps:
      1. Create test with all components
      2. Run full postprocessor workflow
      3. Verify logs show each step
      4. Verify result contains all expected data
    Expected Result: Complete workflow executes successfully
    Evidence: .sisyphus/evidence/task-23-integration.txt
  ```

  **Commit**: YES (group with Task 22)

---

- [ ] **24. Write integration tests**

  **What to do**:
  - Write tests in `tests/postprocess/test_integration.py`
  - Test full workflow with all components
  - Test multiple destinations simultaneously
  - Test failure scenarios and recovery

  **Must NOT do**:
  - Don't use real S3/HTTP (use mocks)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: End-to-end testing

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 6 (with Tasks 21, 22, 23)
  - **Blocks**: None
  - **Blocked By**: Tasks 4, 23

  **Acceptance Criteria**:
  - [ ] Full workflow test with filesystem destination
  - [ ] Full workflow test with CloudPath (S3/GCS mocked)
  - [ ] Full workflow test with multiple destinations
  - [ ] Failure recovery test
  - [ ] All tests pass: `pytest tests/postprocess/test_integration.py -v`

  **QA Scenarios**:
  ```
  Scenario: Run integration tests
    Tool: pytest
    Steps:
      1. python -m pytest tests/postprocess/test_integration.py -v
    Expected Result: All tests PASS
    Evidence: .sisyphus/evidence/task-24-integration-tests.txt
  ```

  **Commit**: YES
  - Message: `test(postprocess): add integration tests`

---

### Wave 7: Integration, Plugin & Documentation

- [ ] **25. Integrate with rompy ModelRun**

  **What to do**:
  - Ensure postprocessor works with `model_run.postprocess()`
  - Test integration with actual ModelRun workflow
  - Verify config can be passed through rompy API

  **Must NOT do**:
  - Don't modify rompy core (just ensure compatibility)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: Rompy integration testing

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 7 (with Tasks 26, 27, 28, 29)
  - **Blocks**: Task 28
  - **Blocked By**: Tasks 21, 22, 23

  **References**:
  - `rompy.model.ModelRun` documentation
  - `rompy.backends.postprocessors` usage

  **Acceptance Criteria**:
  - [ ] Postprocessor can be called via `model_run.postprocess(processor=WW3UploadPostprocessor, config=upload_config)`
  - [ ] Works with rompy's ModelRun workflow
  - [ ] Configuration passed correctly

  **QA Scenarios**:
  ```
  Scenario: Test rompy integration
    Tool: pytest
    Steps:
      1. Create ModelRun with WW3 config
      2. Call model_run.postprocess() with upload config
      3. Verify postprocessor executes
    Expected Result: Integration works
    Evidence: .sisyphus/evidence/task-25-rompy.txt
  ```

  **Commit**: YES (group with Task 27)

---

- [ ] **26. Add plugin registration via entrypoints**

  **What to do**:
  - Add entrypoint to `pyproject.toml`: `[project.entry-points."rompy.postprocessors"]`
  - Register `WW3UploadPostprocessor` with name `"ww3_upload"`
  - Ensure plugin is discoverable by rompy
  - Test plugin loading

  **Must NOT do**:
  - Don't register if already registered by another package

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: Plugin registration

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 7 (with Tasks 25, 27, 28, 29)
  - **Blocks**: None
  - **Blocked By**: Task 21

  **References**:
  - Python entrypoints documentation
  - `pyproject.toml` entry-points syntax
  - Rompy plugin discovery mechanism

  **Acceptance Criteria**:
  - [ ] Entrypoint added to `pyproject.toml`
  - [ ] Plugin registered as `"ww3_upload"`
  - [ ] Plugin discoverable via `rompy.postprocessors` group
  - [ ] Tests for plugin loading

  **QA Scenarios**:
  ```
  Scenario: Test plugin registration
    Tool: Python REPL (Bash)
    Steps:
      1. pip install -e . (install package)
      2. python -c "from importlib.metadata import entry_points; eps = entry_points(group='rompy.postprocessors'); assert 'ww3_upload' in [ep.name for ep in eps]"
    Expected Result: Plugin is registered and discoverable
    Evidence: .sisyphus/evidence/task-26-plugin.txt
  ```

  **Commit**: YES
  - Message: `feat(postprocess): add entrypoint registration for rompy plugin`

---

- [ ] **27. Add config validation**

  **What to do**:
  - Add validation to UploadConfig
  - Validate destination configurations
  - Check for missing required fields
  - Validate file patterns

  **Must NOT do**:
  - Don't validate credentials (just check they're provided)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - **Reason**: Pydantic validation

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 7 (with Tasks 25, 26, 28, 29)
  - **Blocks**: None
  - **Blocked By**: Task 25

  **Acceptance Criteria**:
  - [ ] UploadConfig validates on instantiation
  - [ ] Destination configs validate required fields
  - [ ] Clear error messages for invalid configs
  - [ ] Tests for validation errors

  **QA Scenarios**:
  ```
  Scenario: Test config validation
    Tool: pytest
    Steps:
      1. Test invalid config raises ValidationError
      2. Test valid config passes
    Expected Result: Validation works correctly
    Evidence: .sisyphus/evidence/task-27-validation.txt
  ```

  **Commit**: YES (group with Task 25)

---

- [ ] **28. Write documentation**

  **What to do**:
  - Create `docs/postprocessing.md`
  - Document configuration options
  - Provide examples for each destination type
  - Document environment variables for credentials
  - Troubleshooting guide

  **Must NOT do**:
  - Don't duplicate rompy documentation

  **Recommended Agent Profile**:
  - **Category**: `writing`
  - **Skills**: []
  - **Reason**: Documentation writing

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 6 (with Tasks 21, 22, 24)
  - **Blocks**: Task F3
  - **Blocked By**: Task 21

  **Acceptance Criteria**:
  - [ ] `docs/postprocessing.md` created
  - [ ] Configuration examples for all destination types
  - [ ] Usage examples
  - [ ] Environment variable reference
  - [ ] Troubleshooting section

  **QA Scenarios**:
  ```
  Scenario: Verify documentation
    Tool: Bash
    Steps:
      1. ls docs/postprocessing.md
      2. grep -c "Example" docs/postprocessing.md
    Expected Result: File exists with examples
    Evidence: .sisyphus/evidence/task-23-docs.txt
  ```

  **Commit**: YES
  - Message: `docs(postprocess): add postprocessor documentation`

---

- [ ] **29. Write end-to-end tests**

  **What to do**:
  - Create comprehensive end-to-end test
  - Test full workflow from config to upload
  - Test with realistic WW3 output structure

  **Must NOT do**:
  - Don't use real external services

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []
  - **Reason**: End-to-end testing

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 7 (with Tasks 25, 26, 27, 28)
  - **Blocks**: None
  - **Blocked By**: Task 23

  **Acceptance Criteria**:
  - [ ] End-to-end test with realistic scenario
  - [ ] Test passes: `pytest tests/postprocess/test_e2e.py -v`

  **QA Scenarios**:
  ```
  Scenario: Run E2E tests
    Tool: pytest
    Steps:
      1. python -m pytest tests/postprocess/test_e2e.py -v
    Expected Result: Test PASS
    Evidence: .sisyphus/evidence/task-29-e2e.txt
  ```

  **Commit**: YES
  - Message: `test(postprocess): add end-to-end tests`

---

### Wave 8: Final Review

- [ ] **F1. Code quality review**

  **What to do**:
  - Run ruff linter: `ruff check src/rompy_ww3/postprocess/`
  - Run mypy type checker: `mypy src/rompy_ww3/postprocess/`
  - Fix any issues

  **Acceptance Criteria**:
  - [ ] ruff passes with no errors
  - [ ] mypy passes with no errors

  **QA Scenarios**:
  ```
  Scenario: Run linters
    Tool: Bash
    Steps:
      1. ruff check src/rompy_ww3/postprocess/
      2. mypy src/rompy_ww3/postprocess/
    Expected Result: No errors
    Evidence: .sisyphus/evidence/f1-lint.txt
  ```

---

- [ ] **F2. Run full test suite**

  **What to do**:
  - Run all postprocess tests
  - Verify no regressions

  **Acceptance Criteria**:
  - [ ] All tests pass: `pytest tests/postprocess/ -v`

  **QA Scenarios**:
  ```
  Scenario: Run all tests
    Tool: pytest
    Steps:
      1. python -m pytest tests/postprocess/ -v
    Expected Result: All tests PASS
    Evidence: .sisyphus/evidence/f2-tests.txt
  ```

---

- [ ] **F3. Verify documentation examples**

  **What to do**:
  - Test all code examples in documentation
  - Ensure they work as written

  **Acceptance Criteria**:
  - [ ] All documentation examples tested
  - [ ] Examples work correctly

  **QA Scenarios**:
  ```
  Scenario: Test doc examples
    Tool: Python REPL
    Steps:
      1. Copy examples from docs
      2. Run each example
      3. Verify expected output
    Expected Result: Examples work
    Evidence: .sisyphus/evidence/f3-docs.txt
  ```

---

- [ ] **F4. Check test coverage**

  **What to do**:
  - Run tests with coverage: `pytest tests/postprocess/ --cov=src/rompy_ww3/postprocess`
  - Verify coverage >= 80%

  **Acceptance Criteria**:
  - [ ] Test coverage >= 80%

  **QA Scenarios**:
  ```
  Scenario: Check coverage
    Tool: pytest with coverage
    Steps:
      1. pytest tests/postprocess/ --cov=src/rompy_ww3/postprocess --cov-report=term
    Expected Result: Coverage >= 80%
    Evidence: .sisyphus/evidence/f4-coverage.txt
  ```

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1 | `feat(postprocess): create package structure` | All new directories | ls check |
| 2+3 | `feat(postprocess): add configuration and base uploader` | config.py, uploaders/base.py | Import test |
| 4 | `test(postprocess): add test fixtures` | tests/postprocess/conftest.py | pytest collect |
| 5 | `feat(postprocess): add OutputType parser` | discovery.py | Parse test |
| 6+7 | `feat(postprocess): add file pattern generation and discovery` | discovery.py | Pattern test |
| 8 | `test(postprocess): add discovery tests` | test_discovery.py | pytest |
| 9 | `feat(postprocess): add restart date calculation` | restart.py | Date test |
| 10+11 | `feat(postprocess): add restart file renaming` | restart.py | Rename test |
| 12 | `test(postprocess): add restart tests` | test_restart.py | pytest |
| 13 | `feat(postprocess): add filesystem uploader` | uploaders/filesystem.py | Upload test |
| 14 | `feat(postprocess): add cloud storage uploader (CloudPath)` | uploaders/cloud.py | CloudPath test |
| 15 | `feat(postprocess): add Oceanum uploader` | uploaders/oceanum.py | Oceanum test |
| 16 | `feat(postprocess): add HTTP uploader` | uploaders/http.py | HTTP test |
| 17 | `test(postprocess): add uploader tests` | test_uploaders.py | pytest |
| 18+19 | `feat(postprocess): add lifecycle tracking and retention` | lifecycle.py | Retention test |
| 20 | `test(postprocess): add lifecycle tests` | test_lifecycle.py | pytest |
| 21 | `feat(postprocess): implement core postprocessor` | __init__.py | Integration test |
| 22+23 | `feat(postprocess): add retry logic and integration` | uploaders/*, __init__.py | Retry test |
| 24 | `test(postprocess): add integration tests` | test_integration.py | pytest |
| 25+27 | `feat(postprocess): add rompy integration and validation` | __init__.py, config.py | Integration test |
| 26 | `feat(postprocess): add plugin entrypoint registration` | pyproject.toml | Entrypoint test |
| 28 | `docs(postprocess): add documentation` | docs/postprocessing.md | File exists |
| 29 | `test(postprocess): add end-to-end tests` | test_e2e.py | pytest |

---

## Success Criteria

### Verification Commands

```bash
# Run all postprocess tests
pytest tests/postprocess/ -v

# Check code quality
ruff check src/rompy_ww3/postprocess/
mypy src/rompy_ww3/postprocess/

# Check test coverage
pytest tests/postprocess/ --cov=src/rompy_ww3/postprocess --cov-report=term

# Verify imports work
python -c "from rompy_ww3.postprocess import WW3UploadPostprocessor; print('OK')"

# Test example from documentation
python docs/examples/postprocess_example.py
```

### Final Checklist

- [ ] All 6 OutputType types supported (field, point, track, partition, coupling, restart)
- [ ] Restart files correctly renamed with calculated valid dates
- [ ] Multiple destinations upload simultaneously
- [ ] Retry logic works with exponential backoff
- [ ] Cloud storage via CloudPath/fsspec (S3, GCS, Azure) works
- [ ] Oceanum storage upload works
- [ ] Lifecycle management retains last 24h with minimum 2 files
- [ ] Environment variable credential handling
- [ ] Plugin registered via rompy entrypoints
- [ ] All tests pass (pytest)
- [ ] Code quality checks pass (ruff, mypy)
- [ ] Test coverage >= 80%
- [ ] Documentation complete with examples
- [ ] No breaking changes to existing rompy-ww3 functionality

---

## Plan Compliance

### Must Have (Verified)
- [x] Configuration-based file discovery - **CONFIRMED**
- [x] Restart file renaming with valid date calculation - **CONFIRMED**
- [x] Filesystem, cloud storage (via CloudPath/fsspec), HTTP, and Oceanum upload backends - **CONFIRMED**
- [x] Retry logic with exponential backoff - **CONFIRMED**
- [x] Configurable failure severity - **CONFIRMED**
- [x] Environment variable credential handling - **CONFIRMED**
- [x] Follow rompy postprocessor interface - **CONFIRMED**
- [x] Lifecycle management for restart files (24h retention, min 2 files) - **CONFIRMED**
- [x] Plugin registration via rompy entrypoints - **CONFIRMED**

### Must NOT Have (Verified)
- [x] Input data upload - **EXCLUDED**
- [x] File format conversion - **EXCLUDED**
- [x] Compression/encryption - **EXCLUDED**
- [x] Database cataloging - **EXCLUDED**
- [x] Email notifications - **EXCLUDED**
- [x] Progress bars - **EXCLUDED** (logging only)
- [x] Concurrent uploads - **EXCLUDED** (sequential)
- [x] boto3 dependency - **EXCLUDED** (use CloudPath/fsspec instead)

---

## Notes

### Restart File Valid Date Calculation

Formula: `valid_date = start_date + (stride_seconds × restart_number)`

Example:
- Start: 2024-01-01 00:00:00
- Stride: 86400 (1 day in seconds)
- Restart N=1: valid date = 2024-01-02 00:00:00
- Restart N=2: valid date = 2024-01-03 00:00:00

### Datestamp Format

Format: `YYYYMMDD_HHMMSS`

Examples:
- `ww3.20240115_120000.nc`
- `restart.20240115_120000.ww3`

### Multiple Destinations

Upload to all configured destinations in sequence:
1. Upload to destination 1
2. Upload to destination 2
3. ...continue for all destinations

Each destination has independent retry logic.

### Failure Modes

**Strict Mode**: Upload failure → entire postprocessor fails
**Lenient Mode**: Upload failure → log warning, continue with other files

User configures in UploadConfig.

---

## Next Steps

1. Run `/start-work` to begin execution
2. Sisyphus will execute tasks in order, respecting dependencies
3. Each task includes detailed QA scenarios for verification
4. Final verification in Wave 7 ensures quality

---

*Plan generated by Prometheus based on user requirements, codebase research, and Metis gap analysis.*
