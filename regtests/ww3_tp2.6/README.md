# WW3 tp2.6 Regression Test

## Test Description

**Test ID**: ww3_tp2_6_regression
**Type**: 2-D propagation on spherical grid with wind forcing and LIMON grid (LIMON coastline).
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.6

This test exercises wind-forced 2-D propagation on a curved SPHE grid with a LIMON contour grid to validate coastal interactions.

## Key Characteristics
- Duration: 0 hours (instant) – configuration heavy test; cadence driven by output_times
- Grid: LIMON (UNST, SPHE) with square grid 22×3; curvature enabled
- Propagation: flcx and flcy both true; wind forcing present (WND) with SF and OGBC control
- Output: HS, CUR, FP, DIR, SPR, T02, T01, UST, CGE, DTD, QP, QKK
- Output interval: 10 minutes
- Depth: Bathymetry and LIMON grid depth inputs

## Files
- regtests/ww3_tp2.6/rompy_ww3_tp2_6.yaml
- regtests/ww3_tp2.6/rompy_ww3_tp2_6.py

## Running the Test
### Generate Configuration
```bash
cd regtests/ww3_tp2.6
python rompy_ww3_tp2_6.py
```

### Run with WW3 (requires WW3 installation)
Follow your standard WW3 workflow.

## Physics Tested
- Wind-forced 2-D propagation on a curved SPHE grid with a LIMON unstructured grid; tests cross-grid forcing and grid interactions.
