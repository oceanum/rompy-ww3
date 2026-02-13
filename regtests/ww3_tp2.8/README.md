# WW3 tp2.8 Regression Test

## Test Description

**Test ID**: ww3_tp2_8_regression
**Type**: 2-D propagation with wind and currents; validates a baseline 2-D propagation with meteorological forcing.
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.8

This test validates 2-D propagation under wind and current forcing on a base grid with standard rectangular cells and SPHE coordinates.

## Key Characteristics
- Duration: 0 hours (test window defined by output cadence)
- Grid: 2-D grid with RECT, SPHE, close NONE; nested inbound points
- Propagation: flcx and flcy true; dtxy around 45-60 seconds; 1-hour cadence
- Output: DPT, CUR, HS, FP, DIR, SPR
- Output interval: 1 hour
- Depth: Bathymetry data blob is provided

## Files
- regtests/ww3_tp2.8/rompy_ww3_tp2_8.yaml
- regtests/ww3_tp2.8/rompy_ww3_tp2_8.py

## Running the Test
### Generate Configuration
```bash
cd regtests/ww3_tp2.8
python rompy_ww3_tp2_8.py
```

### Run with WW3 (requires WW3 installation)
Follow your standard WW3 workflow with generated namelist files.

## Physics Tested
- 2-D propagation with wind-driven forcing and current interactions; tests basic cross-grid propagation and boundary handling.
