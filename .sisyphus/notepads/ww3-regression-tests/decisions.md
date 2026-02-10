# WW3 Regression Tests Decisions

## 2026-02-10

### Decision: Skip Git Worktree (Task 0.0)
- **Reason**: Already running in main repository, boulder.json is set up here
- **Alternative**: Will work in main repo on feature branch
- **Impact**: All 29+ test files will be in main repo (acceptable for now)

### Decision: Parallel Execution of Pre-phase Tasks
- Task 0.1 (Download infrastructure) and Task 0.2 (Documentation) can run in parallel
- Both are independent and don't conflict
- Task 1.1+ depend on 0.1 being complete

### Decision: Start with tp1.1 Implementation
- tp1.1 is simplest: 1-D propagation, Cartesian, no sources
- Will serve as template for other tp1.x tests
- Uses same pattern as tp2.4 but simplified

### File Naming Convention
- YAML: `rompy_ww3_tpX_X.yaml`
- Python: `rompy_ww3_tpX_X.py`
- Directory: `regtests/ww3_tpX.X/`

### Input Data Strategy
- Create download script to fetch from NOAA-EMC/WW3 GitHub raw URLs
- Store in `regtests/ww3_tpX.X/input/` maintaining structure
- Don't commit large binaries (add to .gitignore)
- Support bulk and selective downloads
