# WW3 tp1.4 Regression Test

## Test Description

**Test ID**: ww3_tp1_4_regression
**Type**: 1-D propagation with refraction along a Cartesian grid (refraction test).
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.4

This test targets 1-D refraction effects along a Cartesian grid, validating basic wave propagation with refraction terms enabled and no source terms.

## Key Characteristics
- Duration: 12 hours
- Grid: 1-D RECT grid, Cartesian, with 13×3 points (REFRACTION X)
- Propagation: X-direction with refraction enabled (flcth = true) and no Y-propagation (flcy = false)
- Output: HS and DPT (depth) plus DIR and SPR in the OUNF/NML outputs per configuration
- Output interval: 15 minutes (900 seconds)
- Source terms: NONE

## Files
- regtests/ww3_tp1.4/rompy_ww3_tp1_4.yaml
- regtests/ww3_tp1.4/rompy_ww3_tp1_4.py  (if present)

## Running the Test
### Generate Configuration (if Python script is available)
```bash
cd regtests/ww3_tp1.4
python rompy_ww3_tp1_4.py
```

### Run with WW3 (requires WW3 installation)
Follow your standard WW3 execution workflow using the generated namelist files.
```

## Physics Tested
- Refraction behavior in a 1-D Cartesian setting with no source terms.
