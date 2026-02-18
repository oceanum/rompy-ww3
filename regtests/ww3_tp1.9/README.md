# WW3 tp1.9 Regression Test

## Test Description

**Test ID**: ww3_tp1_9_regression
**Type**: 1-D propagation with nonlinear shoaling setup (NONLINEAR SHOALING) on spherical grid.
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.9

This test exercises nonlinear shoaling behavior in a 1-D configuration, validating nonlinear effects in a controlled setup with a large, dense depth and grid configuration.

## Key Characteristics
- Duration: 0 hours (instant window) with a small time step grid
- Grid: 2-D cell with Nonlinear Shoaling X on a rectangular cartesian grid
- Propagation: X-direction with strong nonlinear effects enabled in depth and shoreline terms
- Output: HS and T0M1 among other fields; depth and current fields included depending on configuration
- Output interval: 5 seconds scale (as defined by YAML timestride)
- Source terms: Nonlinear effects included

## Files
- regtests/ww3_tp1.9/rompy_ww3_tp1_9.yaml
- regtests/ww3_tp1.9/rompy_ww3_tp1_9.py  (if present)
- regtests/ww3_tp1.9/input/ (depth and nonlinear priors)

## Running the Test
### Generate Configuration (if Python script is available)
```bash
cd regtests/ww3_tp1.9
python rompy_ww3_tp1_9.py
```

### Run with WW3 (requires WW3 installation)
Follow your standard WW3 workflow with the generated namelist files.
```

## Physics Tested
- Nonlinear shoaling physics in a 1-D setup; tests the nonlinear coupling with depth and shoreline terms.
