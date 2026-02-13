# WW3 tp1.7 Regression Test

## Test Description

**Test ID**: ww3_tp1_7_regression
**Type**: 1-D propagation with 1-D IG (wave-IG) generation on a curved path.
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.7

This test exercises 1-D wave generation at an incoming wave grid with a 1-D IG configuration, validating wave generation and basic propagation in a curved coordinate system.

## Key Characteristics
- Duration: 6 hours
- Grid: 1-D GRID: IG WAVE GENERATION; curved path in SPHE coordinates for a 1-D directed wave evolution
- Propagation: X and Y components enabled (flcx = true, flcy = true)
- Output: DPT HS T0M1 DIR SPR HIG EF P2L; include point outputs for reference data
- Output interval: 5 minutes (300 seconds)
- Source terms: NONE beyond IG setup

## Files
- regtests/ww3_tp1.7/rompy_ww3_tp1_7.yaml
- regtests/ww3_tp1.7/rompy_ww3_tp1_7.py  (if present)

## Running the Test
### Generate Configuration (if Python script is available)
```bash
cd regtests/ww3_tp1.7
python rompy_ww3_tp1_7.py
```

### Run with WW3 (requires WW3 installation)
As per your usual WW3 workflow with the generated namelist files.
```

## Physics Tested
- 1-D wave propagation with 1-D IG wave generation on a curved SPHE grid.
- Validation of IG-driven generation and directional propagation in a simplified setup.
