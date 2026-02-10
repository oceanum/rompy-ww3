# mww3_test_01 - Multi-Grid Basic Configuration

## Test Overview

**Test Name:** mww3_test_01  
**Type:** Multi-grid regression test  
**Purpose:** Validate basic multi-grid WW3 configuration with 2 coupled model grids  
**Reference:** https://github.com/NOAA-EMC/WW3/tree/develop/regtests/mww3_test_01

## Test Description

This test validates the fundamental multi-grid capabilities of WAVEWATCH III by running two coupled model grids:

1. **Coarse Grid** (outer domain):
   - Name: "coarse"
   - MPI Rank: 1
   - Communication fraction: 0.00-0.50
   - Time steps: dtmax=900s, dtxy=300s, dtkth=450s

2. **Fine Grid** (nested domain):
   - Name: "fine"  
   - MPI Rank: 2
   - Communication fraction: 0.50-1.00
   - Time steps: dtmax=450s, dtxy=150s, dtkth=225s (finer for accuracy)

## Multi-Grid Features Tested

- **Grid Coupling**: Two grids with proper MPI rank assignment
- **Boundary Exchange**: Communication between coarse and fine grids
- **Resource Allocation**: Per-grid communication fraction allocation
- **Time Step Configuration**: Different timesteps for each grid
- **Spectrum Configuration**: Per-grid spectral discretization
- **Output Management**: Per-grid output type specification

## Configuration Details

### Domain Configuration

```
Start: 2020-01-01 00:00:00
Stop:  2020-01-02 00:00:00
Duration: 1 day
Number of grids: 2 (both model grids, no separate input grids)
I/O type: 1 (unified point output)
```

### Forcing Configuration

Both grids use:
- Wind forcing: T (from files)
- Water levels: F (disabled)
- Currents: F (disabled)
- Ice: F (disabled)

### Spectrum Settings

Both grids use:
- Frequency multiplier (xfr): 1.1
- First frequency (freq1): 0.04118 Hz
- Number of frequencies (nk): 25
- Number of directions (nth): 24
- Direction offset (thoff): 0.0°

### Output Configuration

Output fields: HS FP DP DIR
Output frequency: Every 3600 seconds (hourly)

## Files Generated

- `rompy_ww3_mww3_test_01.py`: Python configuration script
- `ww3_multi.nml`: Multi-grid namelist configuration (generated)

## Input Data Requirements

**Status:** Input data download required

Input files needed:
- Grid depth files for coarse and fine grids
- Wind forcing files for simulation period
- Boundary condition files (if applicable)

To download input data:
```bash
python regtests/download_input_data.py --test mww3_test_01
```

## Running the Test

### Using Python Script

```bash
cd regtests/mww3_test_01
python rompy_ww3_mww3_test_01.py
```

### Using Test Runner

```bash
python regtests/run_regression_tests.py --test mww3_test_01
```

## Expected Outputs

- Multi-grid namelist: `ww3_multi.nml`
- Field output files for both grids
- Successful grid coupling and boundary exchange
- Output fields: significant wave height (HS), peak frequency (FP), peak direction (DP), mean direction (DIR)

## Validation Criteria

- [ ] Multi-grid namelist generates correctly
- [ ] MODEL(1)% and MODEL(2)% indexing correct
- [ ] MPI resource allocation properly configured
- [ ] Both grids execute successfully
- [ ] Boundary exchange between grids works
- [ ] Output files generated for both grids

## Notes

- This is the first multi-grid test in the regression suite
- Uses `Multi` component from rompy-ww3 (not `Shel`)
- Demonstrates proper MODEL(n)% indexing for multi-grid configurations
- Fine grid has finer timesteps than coarse grid (typical nesting pattern)
- No separate input grids (nrinp=0), both grids are model grids

## References

- Official WW3 documentation: [WAVEWATCH III User Manual](https://github.com/NOAA-EMC/WW3/wiki)
- Multi-grid configuration: WW3 User Manual Section 3.4
- rompy-ww3 Multi component: `src/rompy_ww3/components/multi.py`
