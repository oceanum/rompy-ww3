# WW3 tp1.3 Regression Test

## Test Description

**Test ID**: ww3_tp1_3_regression
**Type**: 1-D propagation on Cartesian grid with monochromatic shoaling (no source terms).
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.3

This test exercises monochromatic shoaling on a 1-D Cartesian grid (shoaling in the x-direction) with no source terms, focusing on depth-dependent wave evolution in a simplified setting.

## Key Characteristics
- Duration: 8 days
- Grid: 1-D rectangular Cartesian grid with 43 points in x and 3 in y; grid name: MONOCHROMATIC SHOALING X
- Propagation: X-direction (flcx = true, flcy = false)
- Output: Depth (DPT), Significant Wave Height (HS), Frequency (FC), and X-current (CFX)
- Output interval: 1 hour (3600 seconds)
- Source terms: NONE (homog_input empty, wind input disabled)
- Depth data: provided via data_blob from regtests/ww3_tp1.3/input/MONOCHROMATIC.depth

## Files
- regtests/ww3_tp1.3/rompy_ww3_tp1_3.yaml
- regtests/ww3_tp1.3/rompy_ww3_tp1_3.py  (if present)
- regtests/ww3_tp1.3/input/ (depth and any required input files)

## Running the Test
### Generate Configuration (if Python script is available)
```bash
cd regtests/ww3_tp1.3
python rompy_ww3_tp1_3.py
```

### Run with WW3 (requires WW3 installation)
See the README for tp1.3 in the WW3 repository for exact run instructions or use your normal WW3 execution workflow with the generated namelists.
```

## Physics Tested
- Monochromatic shoaling on Cartesian grid with no source terms.
- Validation of shoaling physics and depth dependence in a 1-D setting.
