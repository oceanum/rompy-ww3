# WW3 tp2.1 Regression Test

## Test Description

**Test ID**: ww3_tp2_1_regression
**Type**: 2-D propagation test on a spherical grid (SPHE) with a 2-D RECT grid for propagation.
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.1

This test validates 2-D propagation on a curved spherical grid with a rectangular grid and depth data, including a goal to verify cross-track propagation in SPHE coordinates.

## Key Characteristics
- Duration: 5 hours
- Grid: 2-D PROPAGATION TEST #1; RECT grid, SPHE coordinates, zlim -5, dmin 5.75, nx=43, ny=43
- Propagation: flcx: true, flcy: true; dtxy=300, dtmax=900, dtkth=450
- Output: HS, DIR, SPR, DP, EF, TH1M, STH1M, TH2M, STH2M
- Output interval: 1 hour
- Depth data: 2-D depth file; inbound and boundary setup present

## Files
- regtests/ww3_tp2.1/rompy_ww3_tp2_1.yaml
- regtests/ww3_tp2.1/rompy_ww3_tp2_1.py

## Running the Test
### Generate Configuration
```bash
cd regtests/ww3_tp2.1
python rompy_ww3_tp2_1.py
```

### Run with WW3 (requires WW3 installation)
Follow your standard WW3 workflow with the generated namelist files.

## Physics Tested
- 2-D propagation on spherical coordinates with a CURV dispersion grid and depth-driven propagation; tests 2-D interactions and boundary handling.
