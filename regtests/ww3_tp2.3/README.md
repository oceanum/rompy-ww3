# WW3 tp2.3 Regression Test

## Test Description

**Test ID**: ww3_tp2_3_regression
**Type**: 2-D propagation on spherical grid (base) with RECT grid and depth handling.
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.3

This test exercises standard 2-D propagation on a spherical grid with a rectangular grid, validating multi-directional propagation and depth configuration.

## Key Characteristics
- Duration: 5 days, hourly cadence (5D, dtxy=1H)
- Grid: 2-D PROPAGATION TEST #3; RECT, SPHE; nx=48, ny=38
- Propagation: flcx: true, flcy: true; dtxy=300s; dtmax=900s; dtkth=450s
- Output: HS, DIR, SPR, DP, EF, TH1M, STH1M, TH2M, STH2M
- Depth: data_blob with regtests/ww3_tp2.3/input/GARDEN.depth

## Files
- regtests/ww3_tp2.3/rompy_ww3_tp2_3.yaml
- regtests/ww3_tp2.3/rompy_ww3_tp2_3.py

## Running the Test
### Generate Configuration
```bash
cd regtests/ww3_tp2.3
python rompy_ww3_tp2_3.py
```

### Run with WW3 (requires WW3 installation)
Use the generated namelist files.

## Physics Tested
- 2-D propagation on a spherical grid; validates cross-grid propagation and depth handling in a 2-D setting.
