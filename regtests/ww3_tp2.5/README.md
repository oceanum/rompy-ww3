# WW3 tp2.5 Regression Test

## Test Description

**Test ID**: ww3_tp2_5_regression
**Type**: 2-D propagation on spherical surface with a curved grid; depth and curvilinear grid interactions.
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.5

This test validates a 2-D propagation scenario with a curved SPHE grid, including depth, curvature, and oblique grid definitions.

## Key Characteristics
- Duration: 12 hours
- Grid: 2-D GRID 2.5 with RECT-based propagated grid; curvature enabled
- Propagation: flcx and flcy both enabled; dtxy = 550 s; dtmax = 1650 s
- Output: HS, DP, FP, DIR, SPR
- Output interval: 1 hour
- Depth: depth.361x361.IDLA1.dat; curvature grid with lon/lat files

## Files
- regtests/ww3_tp2.5/rompy_ww3_tp2_5.yaml
- regtests/ww3_tp2.5/rompy_ww3_tp2_5.py

## Running the Test
### Generate Configuration
```bash
cd regtests/ww3_tp2.5
python rompy_ww3_tp2_5.py
```

### Run with WW3 (requires WW3 installation)
Follow your standard WW3 workflow.

## Physics Tested
- 2-D propagation with curvature and depth interactions; tests the 2-D grid with spherical projections.
