# WW3 Regression Test Implementation Plan

## TL;DR

> **Goal**: Implement comprehensive WW3 regression test suite in rompy-ww3, aligning with official NOAA-EMC WW3 tests to ensure correctness and guide feature development.
>
> **Approach**: Phased implementation starting with foundational tp1.x and tp2.x tests, building toward multi-grid support and switch-based compilation.
>
> **Development Environment**: Git worktree recommended for isolated development (see Setup section below)
>
> **Deliverables**: 
> - Pre-phase: Input data download infrastructure
> - Phase 1: 10+ tp1.x test configurations with documentation
> - Phase 2: 15+ tp2.x tests (complementing existing tp2.4)
> - Phase 3: Test runner infrastructure with switch file support
> - Phase 4: Multi-grid foundation with mww3 test preparations
>
> **Estimated Effort**: Pre-phase (1 week) + 4 phases × 2-3 weeks each = 9-13 weeks
> **Parallel Execution**: Tests within phases can run parallel; phases are sequential
> **Prerequisite**: Input data download infrastructure must be completed before Phase 1

---

## Development Setup (Recommended)

### Using Git Worktree for Isolated Development

This work involves creating many new files (29+ test configurations + input data). To keep the main repository clean and enable easy switching between development and stable states, **using a git worktree is strongly recommended**.

#### What is a Git Worktree?
A git worktree allows you to have multiple working directories (worktrees) attached to the same repository. Each worktree can have its own branch and working state, while sharing the same git history.

#### Benefits for This Work
1. **Isolation**: 29+ new test files + downloaded input data won't clutter main working directory
2. **Clean Switching**: Easily switch between development and stable code without stashing
3. **Parallel Work**: Can work on regression tests while maintaining clean main branch for other tasks
4. **Easy Cleanup**: Simply delete worktree when done - no risk to main repo
5. **Large File Handling**: Input data files (GBs potentially) stay isolated

#### Setup Instructions

**Step 1: Create Worktree from main branch**
```bash
# From main repository directory
cd /home/tdurrant/source/rompy/rompy-meta/repos/rompy-ww3/main

# Create worktree on new branch
git worktree add -b feature/regression-tests ../rompy-ww3-regtests

# Navigate to worktree
cd ../rompy-ww3-regtests
```

**Step 2: Initialize Development Environment**
```bash
# Verify you're in worktree
git branch  # Should show: feature/regression-tests

# Install dependencies (if not using existing venv)
uv pip install -e ".[dev,test]"

# Verify rompy-ww3 works
rompy_ww3 --help
```

**Step 3: During Development**
```bash
# All work happens in worktree directory
cd /home/tdurrant/source/rompy/rompy-meta/repos/rompy-ww3-regtests

# Regular git workflow - commits go to feature/regression-tests branch
git add regtests/ww3_tp1.1/
git commit -m "Add tp1.1 test configuration"

# Push branch when ready
git push -u origin feature/regression-tests
```

**Step 4: Cleanup (when work is merged)**
```bash
# Return to main repo
cd /home/tdurrant/source/rompy/rompy-meta/repos/rompy-ww3/main

# Remove worktree
git worktree remove ../rompy-ww3-regtests

# Delete branch (optional)
git branch -d feature/regression-tests
```

#### Worktree Structure
```
/home/tdurrant/source/rompy/rompy-meta/repos/
├── rompy-ww3/                    # Main repository
│   ├── src/
│   ├── tests/
│   ├── .git/                     # Main git directory
│   └── ...
└── rompy-ww3-regtests/           # Worktree (isolated development)
    ├── src/                      # Shared with main (same git)
    ├── regtests/                 # NEW: All test configurations
    │   ├── ww3_tp1.1/
    │   ├── ww3_tp1.2/
    │   └── ...
    ├── input_data/               # NEW: Downloaded input files
    └── ...
```

#### Important Notes
- **Input Data**: Downloaded input files should be in worktree's `.gitignore` (they're large binaries)
- **Docker**: Docker commands work the same in worktree (bind mounts use absolute paths)
- **IDE**: Point your IDE to the worktree directory for isolated development
- **Testing**: Can run tests in both main repo and worktree simultaneously

---

## Context

### Original Request
The regtests directory contains an attempt to recreate official WW3 regression tests from the NOAA-EMC source code. Currently only `ww3_tp2.4` is implemented. The goal is to:

1. Document the purpose of these tests and their relation to official WW3 regtests
2. Examine alignment opportunities with the original `run_test` script
3. Implement more tests with a clear target priority
4. Use these tests to extend rompy-ww3 functionality to match full WW3 capabilities

### Key Constraints Identified
- **Switch compilation**: Not currently tackled, but should be planned for
- **ww3_multi**: Implementation incomplete, so mww3 tests blocked pending ww3_multi work
- **Scope**: Test configurations + runner (no CI/CD for now)
- **Approach**: Phased implementation

### Background Research

**Official WW3 Test Suite Structure:**
```
NOAA-EMC/WW3/regtests/
├── tp1.x/          # 1-D propagation tests (~10 tests)
│   ├── ww3_tp1.1/  # 1-D propagation with no source terms
│   ├── ww3_tp1.2/  # 1-D propagation with wind input
│   └── ...
├── tp2.x/          # 2-D propagation tests (~17 tests)
│   ├── ww3_tp2.1/  # 2-D propagation on Cartesian grid
│   ├── ww3_tp2.4/  # 2-D propagation on spherical grid (IMPLEMENTED)
│   └── ...
├── mww3_test_xx/   # Multi-grid tests (~15 tests)
│   └── Requires ww3_multi component
└── bin/run_test    # Official test orchestration script
```

**Official run_test Script Capabilities:**
- Switch file handling per test
- Sequential execution: grid → strt → bound → prep → shel → output
- Multi-grid model support (ww3_multi)
- Parallel execution (MPI/OpenMP)
- Multiple output formats (native, NetCDF, GRIB)
- Compilation time tracking

**Current rompy-ww3 State:**
- One test: `ww3_tp2.4` (2-D propagation, spherical grid, no source terms)
- Two backends: local and Docker
- Two config formats: Python script and YAML
- Execution: `rompy run <config> --backend-config <backend>`
- No switch file handling
- No automated validation

---

## Work Objectives

### Core Objective
Build a comprehensive regression test suite that validates rompy-ww3 produces identical results to official WW3, while using the tests to drive feature completeness.

### Concrete Deliverables

**Phase 1: Foundation (tp1.x Series)**
- [x] 10 tp1.x test configurations (YAML + Python)
- [x] Input data acquisition for each test
- [x] Test documentation (purpose, physics, expected outputs)
- [x] Reference output comparison baseline

**Phase 2: 2-D Expansion (tp2.x Series)**
- [x] 16 additional tp2.x tests (tp2.1-tp2.17, excluding existing tp2.4)
- [x] Coverage of all grid types: Cartesian, spherical, curvilinear, unstructured
- [x] Source term variations: no sources, wind input, full physics
- [x] Boundary condition tests

**Phase 3: Test Runner Infrastructure**
- [x] Automated test runner script (`run_regression_tests.py`)
- [x] Switch file compilation system design
- [x] Sequential execution orchestration (grid → strt → bound → prep → shel → output)
- [x] Test result aggregation and reporting
- [x] Reference output download and comparison

**Phase 4: Multi-Grid Foundation**
- [x] ww3_multi component completion plan
- [x] 3 foundational mww3 test preparations (configs, data, documentation)
- [x] Multi-grid execution sequence support
- [x] Integration test for ww3_multi + mww3 together

### Definition of Done
- All planned tests run successfully with Docker backend
- At least one test per category produces outputs matching official WW3 references
- Test runner can execute full suite with single command
- Documentation explains each test's purpose and physics
- Switch compilation architecture designed (even if not fully implemented)

### Must Have
- [x] All tp1.x tests implemented and documented
- [x] All tp2.x tests implemented and documented
- [x] Test runner infrastructure operational
- [x] Reference output validation working
- [x] Multi-grid test foundation ready

### Must NOT Have (Guardrails)
- **No CI/CD integration** (out of scope for this plan)
- **No GUI/visualization tools** (use existing tools)
- **No performance benchmarking** (focus on correctness)
- **No switch compilation implementation** (design only, implement later)
- **No ww3_multi completion** (plan only, implement in parallel work)

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (pytest, Docker)
- **Automated tests**: Tests-after (validate outputs post-execution)
- **Framework**: pytest for runner, custom comparison for outputs

### Reference Output Validation

**Approach**: Download official WW3 reference outputs from NOAA-EMC releases, compare rompy-ww3 outputs programmatically.

**Validation Criteria:**
- NetCDF output files: Compare variable values within tolerance (1e-6 relative)
- Binary output files: Byte-for-byte comparison where applicable
- Log files: Check for absence of ERROR/FATAL messages
- Namelist files: Text comparison (should be identical)

**Evidence Capture:**
- Screenshots of test execution
- Diff reports for output comparisons
- Execution logs and timing metrics

---

## Execution Strategy

### Parallel Execution Waves

```
Pre-Phase (Week 0): Input Data Infrastructure
Wave 0.0: Setup git worktree (recommended) - create isolated development environment
Wave 0.1: Create download script and documentation
Wave 0.2: Download and verify all tp1.x input files
Wave 0.3: Download and verify all tp2.x input files

Phase 1 (Weeks 1-3): tp1.x Foundation
Wave 1.1: tp1.1-tp1.3 (Cartesian, no sources)
Wave 1.2: tp1.4-tp1.7 (With wind input)
Wave 1.3: tp1.8-tp1.10 (Full physics variations)
Wave 1.4: Documentation and validation setup

Phase 2 (Weeks 4-6): tp2.x Expansion  
Wave 2.1: tp2.1-tp2.3 (Cartesian grids)
Wave 2.2: tp2.5-tp2.8 (Spherical variations)
Wave 2.3: tp2.9-tp2.13 (Curvilinear/unstructured)
Wave 2.4: tp2.14-tp2.17 (Advanced features)
Wave 2.5: Documentation and validation

Phase 3 (Weeks 7-9): Infrastructure
Wave 3.1: Test runner core functionality
Wave 3.2: Switch compilation design
Wave 3.3: Reference output integration
Wave 3.4: Reporting and aggregation

Phase 4 (Weeks 10-12): Multi-Grid Foundation
Wave 4.1: ww3_multi assessment and planning
Wave 4.2: mww3_test_01-03 preparation
Wave 4.3: Integration test design
Wave 4.4: Documentation and handoff
```

### Dependency Matrix

| Task | Depends On | Blocks | Can Parallelize With |
|------|------------|--------|---------------------|
| 0.0 | None | 0.1-0.3 | None (setup task) |
| 0.1 | None | 0.2-0.3 | 0.0 |
| 0.2 | None | Phase 1 | 0.0-0.1 |
| 0.3 | None | Phase 1 | 0.0-0.2 |
| 1.1 | None | 1.2-1.4 | None |
| 1.2 | None | 1.4 | 1.1 |
| 1.3 | None | 1.4 | 1.1-1.2 |
| 1.4 | 1.1-1.3 | Phase 2 | None |
| 2.1-2.4 | Phase 1 | 2.5 | Each other |
| 2.5 | 2.1-2.4 | Phase 3 | None |
| 3.1 | Phase 2 | 3.2-3.4 | None |
| 3.2 | 3.1 | 3.4 | 3.3 |
| 3.3 | 3.1 | 3.4 | 3.2 |
| 3.4 | 3.2-3.3 | Phase 4 | None |
| 4.1 | Phase 3 | 4.2-4.4 | None |
| 4.2-4.4 | 4.1 | None | Each other |

---

## Before You Begin

### Verify Your Development Environment

**If using Git Worktree (recommended):**
```bash
# Ensure you're in the worktree directory
cd /home/tdurrant/source/rompy/rompy-meta/repos/rompy-ww3-regtests

# Verify branch
git branch  # Should show: feature/regression-tests

# Verify rompy-ww3 CLI works
rompy_ww3 --version
```

**If working in main repository:**
```bash
# Create and switch to feature branch
git checkout -b feature/regression-tests

# Verify environment
rompy_ww3 --version
```

### Input Data Download
Before starting Phase 1, ensure input data infrastructure is ready:
```bash
# Download script should exist
ls regtests/download_input_data.py

# Or create it as part of Task 0.1
```

---

## Pre-Phase: Input Data Infrastructure (Week 0)

### Overview
Before implementing test configurations, we need infrastructure to download and manage static input files from the official WW3 repository. This pre-phase also includes setting up the development environment (git worktree recommended).

### TODOs

- [x] **0.0 Setup Git Worktree (Optional but Recommended)**

  **What to do:**
  - Create isolated git worktree for regression test development
  - Initialize development environment in worktree
  - Document worktree workflow
  
  **Setup Steps:**
  ```bash
  # From main repository
  cd /home/tdurrant/source/rompy/rompy-meta/repos/rompy-ww3/main
  
  # Create worktree on new branch
  git worktree add -b feature/regression-tests ../rompy-ww3-regtests
  
  # Navigate to worktree
  cd ../rompy-ww3-regtests
  
  # Install dependencies
  uv pip install -e ".[dev,test]"
  
  # Verify
  rompy_ww3 --version  # Should work
  git branch  # Should show: feature/regression-tests
  ```
  
  **Why Worktree:**
  - Isolates 29+ new test files + downloaded input data
  - Keeps main repo clean
  - Easy to switch between dev and stable
  - Simple cleanup when done
  
  **Acceptance Criteria:**
  - [ ] Worktree created at `/home/tdurrant/source/rompy/rompy-meta/repos/rompy-ww3-regtests`
  - [ ] On branch `feature/regression-tests`
  - [ ] rompy-ww3 CLI works
  - [ ] Can commit and push from worktree

- [x] **0.1 Create Input Data Download Infrastructure (PREREQUISITE)**

  **What to do:**
  - Create `regtests/download_input_data.py` script
  - Script fetches static input files from NOAA-EMC/WW3 repository
  - Support downloading by test series (tp1.x, tp2.x) or individual tests
  - Verify file integrity with checksums
  
  **Download Logic:**
  ```python
  # Example implementation pattern:
  def download_test_inputs(test_name: str, output_dir: Path):
      base_url = "https://raw.githubusercontent.com/NOAA-EMC/WW3/develop/regtests"
      input_files = get_required_files(test_name)  # Map test->files
      for file in input_files:
          url = f"{base_url}/{test_name}/input/{file}"
          download(url, output_dir / test_name / "input" / file)
  ```
  
  **Required Features:**
  - [ ] Download from GitHub raw URLs
  - [ ] Support bulk download (entire test series)
  - [ ] Support selective download (specific tests)
  - [ ] Progress reporting
  - [ ] Resume interrupted downloads
  - [ ] Verify file sizes/checksums
  - [ ] Skip existing files (unless --force)
  
  **Acceptance Criteria:**
  - [ ] Can download tp2.4 inputs (verify with existing test)
  - [ ] Can download all tp1.x inputs
  - [ ] Can download all tp2.x inputs
  - [ ] Files organized in correct directory structure
  - [ ] Script documented with usage examples

- [x] **0.2 Document Input File Requirements**

  **What to do:**
  - Create `regtests/INPUT_DATA.md` documenting:
    - What input files each test requires
    - File sizes and approximate download time
  - Create mapping of test -> required input files
  - Document which tests can run without external inputs
  
  **Content:**
  ```markdown
  # Input Data Requirements
  
  ## Quick Reference
  | Test | Depth | Wind | Current | Ice | Boundary | Total Size |
  |------|-------|------|---------|-----|----------|------------|
  | tp1.1 | ✓ | ✗ | ✗ | ✗ | ✗ | ~500 KB |
  | tp1.2 | ✓ | ✓ | ✗ | ✗ | ✗ | ~2 MB |
  | tp2.4 | ✓ | ✗ | ✗ | ✗ | ✗ | ~500 KB |
  
  ## Download Instructions
  ```bash
  # Download all input data
  python regtests/download_input_data.py --all
  
  # Download specific test series
  python regtests/download_input_data.py --series tp1.x
  
  # Download specific test
  python regtests/download_input_data.py --test tp1.1
  ```
  
  **Acceptance Criteria:**
  - [ ] INPUT_DATA.md created
  - [ ] All tests documented
  - [ ] File requirements matrix complete
  - [ ] Download instructions clear

- [x] **1.1 Implement tp1.1: 1-D Propagation (Cartesian, No Sources)**

  **What to do:**
  - Create `regtests/ww3_tp1.1/rompy_ww3_tp1_1.yaml`
  - Create `regtests/ww3_tp1.1/rompy_ww3_tp1_1.py`
  - Configure: Cartesian grid, 1-D propagation, no source terms
  - Test parameters from official WW3 reference
  
  **Reference:** https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.1
  
  **Key Parameters:**
  - Grid: 1-D Cartesian
  - Domain: ~100-200 points along x-axis
  - Spectrum: 25 frequencies, 24 directions
  - No wind, no currents, no ice
  - Run: 6-12 hours
  
  **Must NOT do:**
  - Don't add source terms (keep it pure propagation)
  - Don't use spherical coordinates
  
  **Recommended Agent Profile:**
  - **Category**: `unspecified-high` (new test implementation)
  - **Skills**: None required
  
  **Parallelization:**
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1.1 (with 1.2, 1.3)
  
  **Acceptance Criteria:**
  - [ ] YAML config validates successfully
  - [ ] Python script runs without errors
  - [ ] Generates ww3_shel.nml and ww3_grid.nml
  - [ ] Test can be executed: `rompy run regtests/ww3_tp1.1/rompy_ww3_tp1_1.yaml`

- [x] **1.2 Implement tp1.2: 1-D Propagation (Cartesian, Wind Input)**

  **What to do:**
  - Similar to tp1.1 but with wind forcing enabled
  - Configure wind input source terms (SIN1 or SIN3)
  - Add homogeneous wind input configuration
  
  **Reference:** https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.2
  
  **Key Differences from tp1.1:**
  - Add InputForcing with winds='T'
  - Add HomogInput for wind data
  - Configure wind speed/direction
  
  **Acceptance Criteria:**
  - [ ] Wind forcing configured in Input namelist
  - [ ] HomogInput added with wind data
  - [ ] Source terms enabled in Run namelist (flsou=True)

- [x] **1.3 Implement tp1.3: 1-D Propagation (Cartesian, Full Physics)**

  **What to do:**
  - 1-D propagation with full physics package
  - Include wind input, nonlinear interactions, dissipation
  - Use ST4 (Ardhuin et al. 2010) physics
  
  **Reference:** https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.3
  
  **Physics Configuration:**
  - SIN4 (wind input)
  - SNL4 (nonlinear interactions)
  - SDS4 (dissipation)
  - SBT1 (bottom friction)
  - ST4 switch settings
  
  **Acceptance Criteria:**
  - [ ] All physics namelists configured (SIN4, SNL4, SDS4, SBT1)
  - [ ] Namelists component added to config
  - [ ] Switch file documented (for future compilation)

- [x] **1.4 Implement tp1.4-tp1.7: Variations**

  **What to do:**
  - tp1.4: With water levels
  - tp1.5: With currents
  - tp1.6: With ice
  - tp1.7: With tidal forcing
  
  **Pattern:** Each adds one forcing component to base tp1.1
  
  **Acceptance Criteria:**
  - [ ] Each test has unique forcing configuration
  - [ ] Document what each test is testing
  - [ ] Input data sources configured

- [x] **1.5 Implement tp1.8-tp1.10: Advanced Variations**

  **What to do:**
  - tp1.8: Multiple grid resolutions
  - tp1.9: Different boundary conditions
  - tp1.10: Point output variations
  
  **Acceptance Criteria:**
  - [ ] Advanced features exercised
  - [ ] Point output component configured where applicable
  - [ ] Boundary component configured where applicable

- [x] **1.6 Create tp1.x Documentation**

  **What to do:**
  - Create `regtests/ww3_tp1.x/README.md` explaining tp1.x series
  - Document each test's purpose and physics
  - Include parameter tables for quick reference
  
  **Content:**
  ```markdown
  # WW3 tp1.x Test Series: 1-D Propagation Tests
  
  ## Overview
  1-D propagation tests validate wave propagation physics along a single axis.
  These are foundational tests that should pass before 2-D tests are attempted.
  
  ## Test Matrix
  | Test | Grid | Sources | Forcing | Purpose |
  |------|------|---------|---------|---------|
  | tp1.1 | Cartesian | None | None | Pure propagation |
  | tp1.2 | Cartesian | SIN | Wind | Wind input validation |
  | tp1.3 | Cartesian | ST4 | Full | Full physics |
  ...
  ```
  
  **Acceptance Criteria:**
  - [ ] README.md created
  - [ ] All 10 tests documented
  - [ ] Parameter reference tables complete
  - [ ] Links to official WW3 docs included

- [x] **1.7 Set Up Reference Output Baseline**

  **What to do:**
  - Download official WW3 reference outputs for tp1.x tests
  - Store in `regtests/reference_outputs/tp1.x/`
  - Document download process and versions
  
  **Process:**
  1. Find reference outputs in NOAA-EMC releases
  2. Download NetCDF outputs for each test
  3. Organize by test case
  4. Create checksums for integrity
  
  **Acceptance Criteria:**
  - [ ] Reference outputs downloaded for all implemented tests
  - [ ] Directory structure organized
  - [ ] Download script documented
  - [ ] Version/tag of reference documented

---

## Phase 2: tp2.x Expansion (Weeks 4-6)

### Overview
Expand 2-D test coverage to include all grid types and physics variations. The existing tp2.4 covers spherical grids; this phase fills the gaps.

### TODOs

- [x] **2.1 Implement tp2.1-tp2.3: Cartesian Grid Tests**

  **What to do:**
  - tp2.1: 2-D Cartesian, no sources (baseline)
  - tp2.2: 2-D Cartesian, with wind
  - tp2.3: 2-D Cartesian, full physics
  
  **Key Configuration:**
  - coord='CART' in GRID_NML
  - Different domain sizes
  - Various boundary conditions
  
  **Acceptance Criteria:**
  - [ ] Cartesian coordinate tests working
  - [ ] Grid dimensions match official tests
  - [ ] Boundary conditions properly configured

- [x] **2.2 Implement tp2.5-tp2.8: Spherical Grid Variations**

  **What to do:**
  - tp2.5: Spherical with different resolutions
  - tp2.6: Spherical with global closure
  - tp2.7: Spherical with unstructured grid
  - tp2.8: Spherical with SMC grid
  
  **Note:** tp2.4 already implemented (reference)
  
  **Grid Types:**
  - RECT (tp2.5, tp2.6)
  - UNST (tp2.7) - unstructured
  - SMC (tp2.8) - Spherical Multiple Cell
  
  **Acceptance Criteria:**
  - [ ] Each grid type configured correctly
  - [ ] Grid-specific namelists added
  - [ ] Depth/mask files referenced correctly

- [x] **2.3 Implement tp2.9-tp2.13: Curvilinear and Advanced Grids**

  **What to do:**
  - tp2.9: Curvilinear grid basics
  - tp2.10: Curvilinear with wind
  - tp2.11: Curvilinear full physics
  - tp2.12: Tripole grid
  - tp2.13: Regional configurations
  
  **Configuration:**
  - CURV namelist instead of RECT
  - Coordinate data files required
  - More complex grid setup
  
  **Acceptance Criteria:**
  - [ ] Curvilinear grids working
  - [ ] Coordinate files configured
  - [ ] Regional boundary handling correct

- [x] **2.4 Implement tp2.14-tp2.17: Advanced Features**

  **What to do:**
  - tp2.14: With boundary conditions (ww3_bound)
  - tp2.15: With nested grids
  - tp2.16: With assimilation
  - tp2.17: With output post-processing (ounf, ounp)
  
  **Components Required:**
  - Bound component (tp2.14)
  - Bounc component (tp2.15)
  - Ounf/Ounp components (tp2.17)
  
  **Acceptance Criteria:**
  - [ ] All components exercised
  - [ ] Component configurations validated
  - [ ] Output post-processing working

- [x] **2.5 Create tp2.x Documentation**

  **What to do:**
  - Similar to tp1.x documentation
  - Include grid type comparison table
  - Document which components each test uses
  
  **Acceptance Criteria:**
  - [ ] tp2.x/README.md created
  - [ ] Grid type comparison included
  - [ ] Component usage matrix documented

- [x] **2.6 Download and Organize tp2.x Reference Outputs**

  **What to do:**
  - Download reference outputs for all tp2.x tests
  - Note: tp2.4 already has reference
  - Organize in `regtests/reference_outputs/tp2.x/`
  
  **Acceptance Criteria:**
  - [ ] All tp2.x reference outputs downloaded
  - [ ] Organized by test case
  - [ ] Integrity verified

---

## Phase 3: Test Runner Infrastructure (Weeks 7-9)

### Overview
Build the test runner infrastructure to automate test execution, switch handling, and result validation.

### TODOs

- [x] **3.1 Design Test Runner Architecture**

  **What to do:**
  - Design `run_regression_tests.py` script
  - Define configuration format (YAML)
  - Plan command-line interface
  
  **Proposed Interface:**
  ```bash
  # Run all tests
  python run_regression_tests.py --all
  
  # Run specific test series
  python run_regression_tests.py --series tp1.x
  
  # Run specific test
  python run_regression_tests.py --test tp1.1
  
  # With specific backend
  python run_regression_tests.py --all --backend docker
  
  # With validation
  python run_regression_tests.py --all --validate
  ```
  
  **Architecture Components:**
  1. Test discovery (find all test configs)
  2. Test execution (run via rompy)
  3. Result collection (gather outputs)
  4. Validation (compare to references)
  5. Reporting (generate report)
  
  **Acceptance Criteria:**
  - [ ] Design document created
  - [ ] CLI interface defined
  - [ ] Configuration schema documented
  - [ ] Reviewed and approved

- [x] **3.2 Implement Test Discovery and Execution**

  **What to do:**
  - Implement test discovery (scan regtests/ directory)
  - Implement test execution (call rompy run)
  - Handle execution errors gracefully
  - Support parallel test execution
  
  **Key Features:**
  - Auto-discover tests by pattern (ww3_tp*)
  - Parse test configuration
  - Execute with timeout handling
  - Capture stdout/stderr
  - Track execution time
  
  **Acceptance Criteria:**
  - [ ] Can discover all implemented tests
  - [ ] Can execute tests sequentially
  - [ ] Can execute tests in parallel (optional)
  - [ ] Error handling works correctly
  - [ ] Execution times captured

- [x] **3.3 Design Switch Compilation System**

  **What to do:**
  - Design architecture for switch-based model rebuilding
  - Document integration with Docker
  - Plan caching strategy for compiled binaries
  
  **Background:**
  WW3 uses "switch files" to configure which physics/features are compiled:
  ```
  F90 NOGRB NOPA NOIPL PR1 PR2 UQ FLX1 LN0 ST0 NL0 BT0 DB0 TR0 BS0 XX0 WNT0 WNX0 CRT0 CRX0 O0 O1 O2 O3 O4 O5 O6 O7 O10 O11
  ```
  
  **Design Considerations:**
  1. Switch file parsing and validation
  2. Docker image rebuilding with new switches
  3. Binary caching (don't rebuild if already exists)
  4. Version tracking (switch set → binary mapping)
  5. Integration with test runner
  
  **Proposed Architecture:**
  ```python
  class SwitchCompiler:
      def compile(self, switch_file: Path) -> Path:
          # Parse switch file
          # Check cache
          # Build Docker image if needed
          # Return path to compiled binaries
          pass
  ```
  
  **Acceptance Criteria:**
  - [ ] Design document created
  - [ ] Switch parsing defined
  - [ ] Caching strategy documented
  - [ ] Docker integration planned
  - [ ] Interface defined

- [x] **3.4 Implement Reference Output Comparison**

  **What to do:**
  - Implement NetCDF file comparison
  - Implement binary file comparison
  - Generate diff reports
  - Define tolerance levels
  
  **Comparison Logic:**
  ```python
  def compare_netcdf(ref_file: Path, test_file: Path) -> ComparisonResult:
      # Open both files
      # Compare dimensions
      # Compare variable values within tolerance
      # Return detailed diff
      pass
  ```
  
  **Tolerance Levels:**
  - Strict: 1e-9 relative tolerance
  - Normal: 1e-6 relative tolerance
  - Loose: 1e-3 relative tolerance
  
  **Acceptance Criteria:**
  - [ ] Can compare NetCDF files
  - [ ] Can compare binary files
  - [ ] Tolerance levels configurable
  - [ ] Diff reports generated
  - [ ] Summary statistics produced

- [x] **3.5 Implement Reporting and Aggregation**

  **What to do:**
  - Generate test execution reports
  - Create summary dashboards
  - Export results (JSON, HTML, markdown)
  
  **Report Types:**
  1. Console output (real-time)
  2. Markdown summary
  3. HTML report with diffs
  4. JSON for CI integration
  
  **Acceptance Criteria:**
  - [ ] Console reporting works
  - [ ] Markdown reports generated
  - [ ] HTML reports generated (optional)
  - [ ] JSON export available
  - [ ] Exit codes correct (0=pass, 1=fail)

- [x] **3.6 Create Test Runner Documentation**

  **What to do:**
  - Document how to use the test runner
  - Include troubleshooting guide
  - Document adding new tests
  
  **Content:**
  ```markdown
  # Regression Test Runner
  
  ## Quick Start
  ```bash
  python run_regression_tests.py --all
  ```
  
  ## Adding New Tests
  1. Create test directory
  2. Add YAML config
  3. Download reference outputs
  4. Update test registry
  ```
  
  **Acceptance Criteria:**
  - [ ] README.md created
  - [ ] Usage examples included
  - [ ] Troubleshooting section added

---

## Phase 4: Multi-Grid Foundation (Weeks 10-12)

### Overview
Prepare for multi-grid tests by assessing ww3_multi component and creating foundational mww3 test configurations.

### TODOs

- [x] **4.1 Assess ww3_multi Component Status**

  **What to do:**
  - Review current ww3_multi implementation
  - Identify gaps vs. full WW3 functionality
  - Create completion plan
  
  **Review Checklist:**
  - [ ] Multi-grid configuration parsing
  - [ ] Grid coupling logic
  - [ ] Boundary exchange setup
  - [ ] Input grid handling
  - [ ] Model grid handling
  - [ ] Point output handling
  
  **Deliverable:**
  - Gap analysis document
  - Implementation priority list
  - Estimated effort for completion

- [x] **4.2 Document ww3_multi Completion Plan**

  **What to do:**
  - Create detailed plan for completing ww3_multi
  - Prioritize features needed for mww3 tests
  - Define interfaces and data structures
  
  **Key Features for mww3 Tests:**
  1. Multi-grid namelist generation
  2. Grid-to-grid boundary mapping
  3. Input grid data handling
  4. Model grid execution coordination
  5. Output aggregation
  
  **Acceptance Criteria:**
  - [ ] Completion plan documented
  - [ ] Priorities defined
  - [ ] Interfaces specified
  - [ ] Effort estimated

- [x] **4.3 Implement mww3_test_01 Configuration**

  **What to do:**
  - Create configuration for mww3_test_01 (basic multi-grid)
  - Set up input data references
  - Document expected behavior
  
  **Note:** This will depend on ww3_multi completion
  
  **Test Characteristics:**
  - 2-3 grids
  - Simple boundary exchange
  - Basic input/output
  
  **Acceptance Criteria:**
  - [ ] YAML config created
  - [ ] Python config created
  - [ ] Documentation complete
  - [ ] Ready for ww3_multi integration

- [x] **4.4 Implement mww3_test_02 Configuration**

  **What to do:**
  - More complex multi-grid test
  - Include input grids
  - Include point grids
  
  **Test Characteristics:**
  - 3-5 grids
  - Input grids for forcing
  - Point grids for output
  - Global/regional nesting
  
  **Acceptance Criteria:**
  - [ ] Config created
  - [ ] Documentation complete

- [x] **4.5 Implement mww3_test_03 Configuration**

  **What to do:**
  - Advanced multi-grid features
  - Coupled grids
  - Complex boundary conditions
  
  **Test Characteristics:**
  - 5+ grids
  - Coupled physics
  - Complex exchanges
  
  **Acceptance Criteria:**
  - [ ] Config created
  - [ ] Documentation complete

- [x] **4.6 Design Integration Test for ww3_multi + mww3**

  **What to do:**
  - Design test that validates ww3_multi works end-to-end
  - Define success criteria
  - Plan validation approach
  
  **Integration Test:**
  1. Create multi-grid config
  2. Run through rompy
  3. Execute with Docker
  4. Validate outputs
  
  **Acceptance Criteria:**
  - [ ] Integration test designed
  - [ ] Success criteria defined
  - [ ] Validation approach documented

- [x] **4.7 Create Multi-Grid Documentation**

  **What to do:**
  - Document multi-grid concepts
  - Explain ww3_multi component
  - Document mww3 test series
  
  **Content:**
  ```markdown
  # Multi-Grid Tests (mww3 series)
  
  ## Overview
  Multi-grid tests validate WW3's ability to run multiple coupled grids simultaneously.
  
  ## ww3_multi Component
  The ww3_multi executable manages multiple grids, handling:
  - Grid initialization
  - Boundary exchanges
  - Input distribution
  - Output aggregation
  
  ## Test Series
  | Test | Grids | Complexity | Status |
  |------|-------|------------|--------|
  | mww3_test_01 | 2-3 | Basic | Planned |
  ...
  ```
  
  **Acceptance Criteria:**
  - [ ] Multi-grid documentation created
  - [ ] ww3_multi explained
  - [ ] Test series documented
  - [ ] Integration notes included

---

## Commit Strategy

### Committing from Git Worktree
If using the recommended git worktree, commits are made from the worktree directory:

```bash
cd /home/tdurrant/source/rompy/rompy-meta/repos/rompy-ww3-regtests

# Stage and commit as usual
git add regtests/ww3_tp1.1/
git commit -m "Add tp1.1 regression test configuration"

# Push branch
git push -u origin feature/regression-tests
```

### Commit Timeline

| After Task | Message | Files |
|------------|---------|-------|
| Pre-phase complete | `Add input data download infrastructure` | `regtests/download_input_data.py`, `regtests/INPUT_DATA.md` |
| Phase 1 complete | `Add tp1.x regression test configurations (10 tests)` | `regtests/ww3_tp1.*/*` |
| Phase 2 complete | `Add tp2.x regression test configurations (16 tests)` | `regtests/ww3_tp2.*/*` |
| Phase 3 complete | `Add regression test runner infrastructure` | `regtests/run_regression_tests.py`, `regtests/README.md` |
| Phase 4 complete | `Add multi-grid test foundation (mww3 series)` | `regtests/mww3_test_*/*` |

---

## Success Criteria

### Phase 1 Success
- All 10 tp1.x tests have working configurations
- Documentation explains each test
- At least 3 tests run successfully with Docker
- Reference outputs downloaded and organized

### Phase 2 Success
- All 16 tp2.x tests have working configurations (17 total with existing tp2.4)
- All grid types covered (Cartesian, spherical, curvilinear, unstructured, SMC)
- All major components exercised
- Documentation complete

### Phase 3 Success
- Test runner can execute all implemented tests
- Can compare outputs to references
- Reports generated in multiple formats
- Switch compilation architecture designed

### Phase 4 Success
- ww3_multi completion plan documented
- 3 mww3 test configurations ready
- Integration test designed
- Multi-grid documentation complete

### Overall Success
- 29+ test configurations implemented (tp1.x + tp2.x)
- Test runner operational
- Multi-grid foundation ready
- Clear path to full WW3 functionality

---

## Notes

### Critical Dependencies

#### 1. Static Input Files (NEW - Critical)
Many tests require static input files (depth data, wind fields, boundary conditions, etc.) from the official WW3 repository:

**File Categories:**
- **Depth files**: `depth.*.dat` - Bathymetry data for each grid
- **Wind files**: `wind.*.dat` or NetCDF - Forcing data for wind-input tests
- **Current files**: `current.*.dat` - Ocean current forcing
- **Ice files**: `ice.*.dat` - Sea ice concentration
- **Boundary files**: `nest.*.dat` - Spectral boundary conditions
- **Point files**: `points.list` - Location lists for point output
- **Mask files**: `mask.*.dat` - Land-sea mask definitions

**Download Strategy:**
```bash
# Official WW3 regtests location:
# https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tpX.X/input/

# Example download process:
# 1. Identify required files from test documentation
# 2. Download from NOAA-EMC/WW3 regtests input directories
# 3. Store in regtests/ww3_tpX.X/input/ maintaining original structure
# 4. Verify file integrity (checksums where available)
# 5. Document file versions and WW3 release tags
```

**Test-Specific Requirements:**
| Test | Required Files | Source |
|------|---------------|--------|
| tp1.1 | depth file | WW3 repo |
| tp1.2+ | depth + wind | WW3 repo |
| tp2.4 | depth + points.list | WW3 repo (already present) |
| tp2.14+ | depth + boundary files | WW3 repo |
| All tp1.x | Static depth files | WW3 repo |

**Storage Convention:**
```
regtests/ww3_tpX.X/
├── input/              # Downloaded from WW3 repo
│   ├── depth.*.dat
│   ├── wind.*.dat
│   └── points.list
├── rompy_ww3_tpX_X.yaml   # rompy-ww3 config
└── rompy_ww3_tpX_X.py     # Python config
```

#### 2. Input Data Acquisition Plan
**Phase 1 Pre-work**: Before implementing tp1.x tests:
- [x] Create download script to fetch input files from NOAA-EMC/WW3
- [x] Document file requirements for each test
- [x] Establish `regtests/input_data/` directory structure
- [x] Add input files to .gitignore (don't commit large binary files)
- [x] Document download process in README

#### 3. Docker Images
Tests require WW3 Docker image; may need updates for switch compilation

#### 4. ww3_multi
Multi-grid tests blocked until ww3_multi component is complete

#### 5. Reference Outputs
Need to download from NOAA-EMC releases

### Risk Mitigation
1. **Missing Input Data**: 
   - Input data download script (Task 0.1) addresses this
   - Document which tests can run without external data
   - Provide clear error messages when data is missing
   - Cache downloaded files to avoid re-downloading
2. **Docker Build Failures**: Maintain fallback to local backend
3. **ww3_multi Delays**: Phase 4 can proceed with planning/configs even if implementation delayed
4. **Reference Mismatches**: Define tolerance levels; document known differences

### Opportunities for Extension
1. **CI/CD Integration**: Once test runner is mature, integrate with GitHub Actions
2. **Performance Tracking**: Extend runner to track execution time trends
3. **Coverage Analysis**: Map tests to WW3 code coverage
4. **Visualization**: Add output plotting for quick visual validation

### Related Work
- **ww3_multi completion**: Separate work stream to complete multi-grid component
- **Switch compilation**: Future implementation of dynamic model rebuilding
- **CI/CD**: Future integration with GitHub Actions

---

## Appendix: Official WW3 Test Reference

### Test Categories

**tp1.x: 1-D Propagation Tests**
- Focus: Wave propagation along single axis
- Purpose: Validate 1-D physics
- Count: ~10 tests

**tp2.x: 2-D Propagation Tests**
- Focus: Wave propagation on 2-D grids
- Purpose: Validate 2-D physics, grid types
- Count: ~17 tests

**mww3_test_xx: Multi-Grid Tests**
- Focus: Multiple coupled grids
- Purpose: Validate grid coupling, exchanges
- Count: ~15 tests

### Official run_test Features

The official `run_test` script from NOAA-EMC provides:

1. **Sequential Execution**: grid → strt → bound → bounc → prep → prnc → shel → ounf → ounp → trnc
2. **Switch Handling**: Recompiles WW3 based on switch file
3. **Parallel Support**: MPI, OpenMP
4. **Multi-Grid**: ww3_multi execution
5. **Output Options**: Native, NetCDF, GRIB2
6. **Timing**: Compile and run time tracking
7. **Coupling**: OASIS, ESMF support

### rompy-ww3 Alignment Strategy

**What We Can Match Now:**
- Sequential execution (via test runner)
- Output format support (NetCDF via components)
- Test case configurations

**What Requires Future Work:**
- Switch compilation (design in Phase 3, implement later)
- MPI/OpenMP parallel execution (Docker limitation)
- OASIS/ESMF coupling (complex integration)
- GRIB2 output (additional libraries needed)

---

*Plan generated: 2026-02-10*
*Version: 1.0*
*Status: Ready for review*
