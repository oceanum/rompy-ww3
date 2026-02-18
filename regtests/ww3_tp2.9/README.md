# WW3 tp2.9 Regression Test

## Test Description

**Test ID**: ww3_tp2_9_regression
**Type**: 2-D propagation with obstructions and a curvilinear SPHE grid; nonlinear curvilinear test.
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.9

This test validates 2-D wave propagation with obstructions on a curved grid, with a set of additional inputs to exercise proper curvature handling and obstacle interaction.

## Key Characteristics
- Duration: 24 hours
- Grid: CURV SPHE; grid 2D with obstructions and a complex boundary mask
- Propagation: flcx, flcy, and refraction enabled; dtxy 0.25-0.5 s depending on configuration
- Output: HS, T01, FP, DIR, SPR, DP
- Output interval: 3 hours
- Depth: depth, curvature and mask inputs provided

## Files
- regtests/ww3_tp2.9/rompy_ww3_tp2_9.yaml
- regtests/ww3_tp2.9/rompy_ww3_tp2_9.py

## Running the Test
### Generate Configuration
```bash
cd regtests/ww3_tp2.9
python rompy_ww3_tp2_9.py
```

### Run with WW3 (requires WW3 installation)
Follow your standard WW3 workflow with the generated namelist files.

## Physics Tested
- 2-D propagation with obstructions and curvature; tests the interaction of obstacles with wave fields in a 2-D setting.
