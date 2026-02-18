# WW3 tp1.8 Regression Test

## Test Description

**Test ID**: ww3_tp1_8_regression
**Type**: 1-D propagation with full output across many fields on a short-duration run.
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.8

This test exercises a short, highly-parameterized 1-D propagation case with a relatively dense output specification to validate the end-to-end namelist generation and basic propagation behavior.

## Key Characteristics
- Duration: 0 hours (instantaneous test window) with a short 6-minute cycle implied by output schedule
- Grid: 1-D GRID - WAVE BLOCKING TEST; CURV or CART depending on configuration; HAS a Haas Warner-like validation grid
- Propagation: X direction (flcx = true) with y-propagation disabled (flcy = false)
- Output: A broad set of outputs including DPT, CUR, HS, FP, DIR, SPR, TAW, etc.
- Output interval: 1/6th to 1/10 of an hour depending on config (as defined by timestride in YAML)
- Source terms: NONE

## Files
- regtests/ww3_tp1.8/rompy_ww3_tp1_8.yaml
- regtests/ww3_tp1.8/rompy_ww3_tp1_8.py  (if present)

## Running the Test
### Generate Configuration (if Python script is available)
```bash
cd regtests/ww3_tp1.8
python rompy_ww3_tp1_8.py
```

### Run with WW3 (requires WW3 installation)
Proceed with your standard WW3 run using the generated namelist files.
```

## Physics Tested
- 1-D propagation with extensive output fields to verify data routing and timing in a dense output configuration.
