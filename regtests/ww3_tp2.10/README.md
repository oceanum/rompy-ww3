# WW3 tp2.10 Regression Test

## Test Description

**Test ID**: ww3_tp2_10_regression
**Type**: 2-D propagation with SMC Great Lakes; test includes SMC grid interactions and boundary definitions.
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.10

This test validates a multi-grid system in the Great Lakes region using SMC (Spherical Multi-Cell) grids with a detailed depth and boundary configuration.

## Key Characteristics
- Duration: 6 hours
- Grid: SMC0512 Grid for Great Lakes; SPHE curvilinear projection; multiple mesh cells
- Propagation: flcx, flcy true
- Output: WND, HS, T01, DP, SPR, DIR, EF, TH1M, STH1M, TH2M, STH2M; boundary and depth data handled via smc inputs
- Output interval: 10 minutes
- Depth: Erie region smc data inputs

## Files
- regtests/ww3_tp2.10/rompy_ww3_tp2_10.yaml
- regtests/ww3_tp2.10/rompy_ww3_tp2_10.py

## Running the Test
### Generate Configuration
```bash
cd regtests/ww3_tp2.10
python rompy_ww3_tp2_10.py
```

### Run with WW3 (requires WW3 installation)
Follow your standard WW3 workflow with the generated namelist files.

## Physics Tested
- Multi-grid SMC propagation in the Great Lakes region; validates SMC grid interactions and lake boundary handling.
