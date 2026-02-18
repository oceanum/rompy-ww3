# WW3 tp2.7 Regression Test

## Test Description

**Test ID**: ww3_tp2_7_regression
**Type**: 2-D propagation on spherical grid; 2-D base grid with obstructions and two-way propagation.
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.7

This test exercises 2-D wave propagation on a SPHE grid with multiple obstructions and a wide grid to validate 2-D propagation in a more complex domain.

## Key Characteristics
- Duration: 12 hours
- Grid: 2-D PROPAGATION TEST #7 with base grid; UNST refugations
- Propagation: flcx and flcy true; flcth true; flck true; flsou true
- Output: HS, T02, T01, ABR, UBR
- Output interval: 1 hour
- Depth: 2-D depth with ref file inputs

## Files
- regtests/ww3_tp2.7/rompy_ww3_tp2_7.yaml
- regtests/ww3_tp2.7/rompy_ww3_tp2_7.py

## Running the Test
### Generate Configuration
```bash
cd regtests/ww3_tp2.7
python rompy_ww3_tp2_7.py
```

### Run with WW3 (requires WW3 installation)
Follow your standard WW3 workflow.

## Physics Tested
- 2-D propagation with obstructions on a SPHE grid; validates cross-grid propagation and obstructions handling.
