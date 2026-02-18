# WW3 tp1.5 Regression Test

## Test Description

**Test ID**: ww3_tp1_5_regression
**Type**: 1-D propagation on Cartesian grid with refraction in Y-direction (rolling refraction test).
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.5

This test exercises refraction in the Y-direction on a 1-D setup, with no source terms, validating directional bending of wave energy in a quasi-1-D scenario.

## Key Characteristics
- Duration: 12 hours
- Grid: 1-D RECT grid, Cartesian, REFRACTION Y configuration
- Propagation: Y-direction with refraction (flcy = true, flcx = false, flcth = true)
- Output: HS, T01, FP, and DIR in outputs
- Output interval: 15 minutes (900 seconds)
- Source terms: NONE

## Files
- regtests/ww3_tp1.5/rompy_ww3_tp1_5.yaml
- regtests/ww3_tp1.5/rompy_ww3_tp1_5.py  (if present)

## Running the Test
### Generate Configuration (if Python script is available)
```bash
cd regtests/ww3_tp1.5
python rompy_ww3_tp1_5.py
```

### Run with WW3 (requires WW3 installation)
Use your standard WW3 workflow with the generated namelist files.
```

## Physics Tested
- 1-D refraction in the transverse direction with no sources.
