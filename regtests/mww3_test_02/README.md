# mww3_test_02 - Multi-Grid 3-Level Nesting

## Test Overview

**Test Name:** mww3_test_02  
**Type:** Multi-grid regression test  
**Purpose:** Validate multi-grid WW3 configuration with 3-level grid hierarchy  
**Reference:** https://github.com/NOAA-EMC/WW3/tree/develop/regtests/mww3_test_02

## Test Description

This test validates the 3-level nested multi-grid capabilities of WAVEWATCH III by running three coupled model grids with increasing resolution:

1. **Coarse Grid** (outer domain):
   - Name: "coarse"
   - MPI Rank: 1
   - Communication fraction: 0.00-0.33
   - Coarsest resolution covering largest area

2. **Medium Grid** (intermediate domain):
   - Name: "medium"
   - MPI Rank: 2
   - Communication fraction: 0.33-0.67
   - Intermediate resolution

3. **Fine Grid** (nested inner domain):
   - Name: "fine"  
   - MPI Rank: 3
   - Communication fraction: 0.67-1.00
   - Finest resolution for detailed inner region

## Multi-Grid Features Tested

- **3-Level Grid Hierarchy**: Three grids with progressive nesting
- **Grid Coupling**: Proper MPI rank assignment for 3 grids
- **Boundary Exchange**: Communication between all three grid levels
- **Resource Allocation**: Equal resource distribution across 3 MPI ranks
- **Output Frequency**: More frequent output than mww3_test_01 (30 min vs 1 hour)
- **Extended Output Fields**: Additional fields (SPR, WND, CUR) compared to test_01

## Configuration Details

### Domain Configuration

```
Start: 2020-01-01 00:00:00
Stop:  2020-01-02 00:00:00
Duration: 1 day
Number of grids: 3 (all model grids)
I/O type: 1 (unified point output)
```

### Forcing Configuration

All three grids use:
- Wind forcing: T (from files)
- Water levels: F (disabled)
- Currents: F (disabled)
- Ice: F (disabled)

### Resource Allocation

Resource distribution across 3 MPI ranks:
- Grid 1 (coarse): 33.3% (rank 1)
- Grid 2 (medium): 33.3% (rank 2)
- Grid 3 (fine): 33.4% (rank 3)

### Output Configuration

Output fields: HS FP DP DIR SPR WND CUR (7 fields)
Output frequency: Every 1800 seconds (30 minutes)

## Differences from mww3_test_01

| Feature | mww3_test_01 | mww3_test_02 |
|---------|--------------|--------------|
| Number of grids | 2 | 3 |
| Grid hierarchy | 2-level | 3-level |
| Output frequency | 3600s (hourly) | 1800s (30 min) |
| Output fields | 4 (HS FP DP DIR) | 7 (+ SPR WND CUR) |
| Resource split | 50/50 | 33/33/34 |
| Complexity | Basic nesting | Advanced 3-level nesting |

## Files Generated

- `rompy_ww3_mww3_test_02.py`: Python configuration script
- `ww3_multi.nml`: Multi-grid namelist configuration (generated)

## Input Data Requirements

**Status:** Input data download required

Input files needed:
- Grid depth files for coarse, medium, and fine grids
- Wind forcing files for simulation period
- Boundary condition files for nested grids

To download input data:
```bash
python regtests/download_input_data.py --test mww3_test_02
```

## Running the Test

### Using Python Script

```bash
cd regtests/mww3_test_02
python rompy_ww3_mww3_test_02.py
```

### Using Test Runner

```bash
python regtests/run_regression_tests.py --test mww3_test_02
```

## Expected Outputs

- Multi-grid namelist: `ww3_multi.nml`
- Field output files for all three grids
- Successful grid coupling and boundary exchange
- Output fields: significant wave height (HS), peak frequency (FP), peak direction (DP), mean direction (DIR), directional spread (SPR), wind speed/direction (WND), current speed/direction (CUR)

## Validation Criteria

- [ ] Multi-grid namelist generates correctly
- [ ] MODEL(1)%, MODEL(2)%, MODEL(3)% indexing correct
- [ ] MPI resource allocation properly configured (3 ranks)
- [ ] All three grids execute successfully
- [ ] Boundary exchange between grids works
- [ ] Output files generated for all three grids
- [ ] More frequent output (30 min) works correctly
- [ ] Extended output fields (SPR, WND, CUR) captured

## Notes

- This is the second multi-grid test in the regression suite
- Uses `Multi` component from rompy-ww3 (not `Shel`)
- Demonstrates 3-level grid nesting (more complex than test_01)
- Tests equal resource distribution across 3 MPI ranks
- More frequent output tests I/O performance
- Extended field list validates additional output variables
- No separate input grids (nrinp=1), all 3 are model grids

## References

- Official WW3 documentation: [WAVEWATCH III User Manual](https://github.com/NOAA-EMC/WW3/wiki)
- Multi-grid configuration: WW3 User Manual Section 3.4
- rompy-ww3 Multi component: `src/rompy_ww3/components/multi.py`
- Previous test: `regtests/mww3_test_01/` (2-grid basic configuration)
