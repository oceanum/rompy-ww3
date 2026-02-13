# WW3 tp2.4 Regression Test

## Test Description

**Test ID**: ww3_tp2_4_regression
**Type**: 2-D propagation with rectilinear and spherical grid, advanced wave-field outputs.
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.4

This test exercises 2-D wave propagation with a 2-D grid setup and field outputs, including depth, U (x-current), and other fields on a curved SPHE grid.

## Key Characteristics
- Duration: 3 hours
- Grid: 2-D RECT grid with SPHE coordinates; 2-D propagation test 2.4
- Propagation: flcx, flcy, and refraction enabled with flcth; dtxy ~ 1100 s
- Output: DPT HS FP DIR SPR
- Output interval: 1 hour (3600 s)
- Depth: 2-D depth data blob

## Files
- regtests/ww3_tp2.4/rompy_ww3_tp2_4.yaml
- regtests/ww3_tp2.4/rompy_ww3_tp2_4.py

## Running the Test
### Generate Configuration
```bash
cd regtests/ww3_tp2.4
python rompy_ww3_tp2_4.py
```

### Run with WW3 (requires WW3 installation)
Follow your standard WW3 workflow.

## Physics Tested
- 2-D propagation with refraction and multiple output fields on a curved grid.
