# mww3_test_03 - Advanced Multi-Grid Configuration

## Test Overview

**Test Name:** mww3_test_03  
**Type:** Multi-grid regression test  
**Purpose:** Validate advanced multi-grid WW3 capabilities with differential forcing, extended output, and complex resource allocation  
**Reference:** https://github.com/NOAA-EMC/WW3/tree/develop/regtests/mww3_test_03

## Test Description

This test validates advanced multi-grid capabilities of WAVEWATCH III by running three coupled model grids with extended features:

1. **Coarse Grid** (outer domain):
   - Name: "coarse"
   - MPI Rank: 1
   - Communication fraction: 0.00-0.30 (30% of resources)
   - Forcing: winds + currents

2. **Medium Grid** (intermediate domain):
   - Name: "medium"
   - MPI Rank: 2
   - Communication fraction: 0.30-0.65 (35% of resources)
   - Forcing: winds + currents

3. **Fine Grid** (nested inner domain):
   - Name: "fine"  
   - MPI Rank: 3
   - Communication fraction: 0.65-1.00 (35% of resources)
   - Forcing: winds + currents + water levels

## Advanced Features Tested

### Differential Forcing Per Grid
- **Coarse/Medium Grids**: Winds + currents only
- **Fine Grid**: Winds + currents + water levels
- Tests selective physics activation based on grid needs

### Non-Uniform Resource Allocation
- **Coarse**: 30% (less computational demand)
- **Medium**: 35% (intermediate)
- **Fine**: 35% (highest resolution needs more resources)
- Tests flexible resource distribution for load balancing

### Comprehensive Output Fields
Output variables include (20+ fields):
- **Basic**: HS FP DP DIR SPR (height, period, direction, spread)
- **Wind**: WND (wind speed/direction)
- **Currents**: CUR (current speed/direction)
- **Wave Components**: WCC WCF WCH WCM (spectral components)
- **Mean Periods**: T02 T01 T0M1 (various mean period definitions)
- **Peak Parameters**: FP0 THP0 THS (peak frequency/direction)
- **Spectral Moments**: EF TH1M TH2M (energy flux, directional moments)

### High-Frequency Output
- Output every 15 minutes (stride=900s)
- Tests I/O performance with frequent output
- Provides detailed temporal evolution

### Extended Simulation Duration
- 1.5 days (36 hours) vs 1 day in previous tests
- Tests stability over longer periods

## Configuration Details

### Domain Configuration

```
Start: 2020-01-01 00:00:00
Stop:  2020-01-02 12:00:00
Duration: 1.5 days (36 hours)
Number of grids: 3 (all model grids)
I/O type: 1 (unified point output)
```

### Resource Allocation Summary

| Grid | Rank | Comm Fraction | % of Resources |
|------|------|---------------|----------------|
| Coarse | 1 | 0.00-0.30 | 30% |
| Medium | 2 | 0.30-0.65 | 35% |
| Fine | 3 | 0.65-1.00 | 35% |

### Forcing Configuration Summary

| Grid | Winds | Currents | Water Levels |
|------|-------|----------|--------------|
| Coarse | ✓ | ✓ | ✗ |
| Medium | ✓ | ✓ | ✗ |
| Fine | ✓ | ✓ | ✓ |

## Differences from Previous Tests

| Feature | mww3_test_01 | mww3_test_02 | mww3_test_03 |
|---------|--------------|--------------|--------------|
| Number of grids | 2 | 3 | 3 |
| Differential forcing | No | No | **Yes** |
| Water levels | No | No | **Yes (fine)** |
| Currents | No | No | **Yes (all)** |
| Output fields | 4 | 7 | **20+** |
| Output frequency | 3600s (60min) | 1800s (30min) | **900s (15min)** |
| Resource split | 50/50 | 33/33/34 | **30/35/35** |
| Simulation duration | 1 day | 1 day | **1.5 days** |

## Files Generated

- `rompy_ww3_mww3_test_03.py`: Python configuration script
- `ww3_multi.nml`: Advanced multi-grid namelist configuration (generated)

## Input Data Requirements

**Status:** Input data download required

Input files needed:
- Grid depth files for coarse, medium, and fine grids (g1.depth.60x60, g2.depth.40x40, g3.depth.20x20)
- Wind forcing files for simulation period
- Current forcing files for simulation period
- Water level files for fine grid
- Boundary condition files for nested grids
- Points list file (points.list)

To download input data:
```bash
python regtests/download_input_data.py --test mww3_test_03
```

## Running the Test

### Using Python Script

```bash
cd regtests/mww3_test_03
python rompy_ww3_mww3_test_03.py
```

### Using Test Runner

```bash
python regtests/run_regression_tests.py --test mww3_test_03
```

## Expected Outputs

- Multi-grid namelist: `ww3_multi.nml` with per-grid configurations
- Field output files for all three grids (20+ variables per grid)
- High-frequency output: 97 output timesteps per grid (every 15 min over 1.5 days)
- Successful grid coupling and boundary exchange
- Demonstration of differential physics (water levels only on fine grid)

## Validation Criteria

- [ ] Multi-grid namelist generates correctly
- [ ] MODEL(1)%, MODEL(2)%, MODEL(3)% indexing correct
- [ ] Resource allocation sums to 1.0 (30% + 35% + 35%)
- [ ] Differential forcing per grid (water levels on fine only)
- [ ] All three grids execute successfully
- [ ] Boundary exchange between grids works
- [ ] Output files generated for all three grids
- [ ] Extended output fields (20+ variables) captured
- [ ] High-frequency output (900s stride) works
- [ ] Simulation runs for full 36-hour duration

## Advanced Concepts Demonstrated

### 1. Differential Forcing
Different grids can have different forcing configurations:
- Water levels enabled only where needed (fine grid near coast)
- Reduces computational cost on coarse/medium grids
- Demonstrates flexible forcing configuration

### 2. Resource Optimization
Non-uniform allocation based on computational demand:
- Coarse grid: Less work, less resources (30%)
- Fine grids: More work, more resources (35% each)

### 3. Extended Output
Comprehensive field list tests multiple output capabilities:
- Wave parameters (HS, FP, DP, DIR, SPR)
- Forcing fields (WND, CUR)
- Wave components (WCC, WCF, WCH, WCM)
- Multiple period definitions (T02, T01, T0M1)
- Peak parameters (FP0, THP0, THS)
- Spectral moments (EF, TH1M, TH2M)

## Notes

- This is the most advanced multi-grid test in the regression suite
- Uses `Multi` component from rompy-ww3 (not `Shel`)
- Demonstrates full flexibility of WW3 multi-grid forcing system
- Extended output list tests comprehensive field output
- High-frequency output tests I/O subsystem performance
- No separate input grids (nrinp=1), all 3 are model grids
- Longer simulation (36 hours) tests stability over extended periods
- Non-uniform resource allocation demonstrates load balancing
- Differential forcing (water levels on fine grid only) reduces computational cost

## Physics Considerations

### Forcing Hierarchy
- **Winds**: Required for wave generation (all grids)
- **Currents**: Affects wave propagation (all grids)
- **Water Levels**: Critical near coast (fine grid only)

### Resource Distribution
Non-uniform allocation optimizes performance:
- Coarser grids typically need less computation per timestep
- Finer grids benefit from additional resources
- Total must sum to 1.0 (100% of available resources)

## References

- Official WW3 documentation: [WAVEWATCH III User Manual](https://github.com/NOAA-EMC/WW3/wiki)
- Multi-grid configuration: WW3 User Manual Section 3.4
- Forcing configuration: WW3 User Manual Section 2.5
- rompy-ww3 Multi component: `src/rompy_ww3/components/multi.py`
- Previous tests: `regtests/mww3_test_01/` (2-grid), `regtests/mww3_test_02/` (3-grid basic)

