# WW3 tp1.10 Regression Test

## Test Description

**Test ID**: ww3_tp1_10_regression
**Type**: 2-D propagation with obstructions on a curvilinear spherical grid (SMC-like test).
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.10

This test exercises 2-D wave propagation on a curved SPHE grid with obstructions and boundary obstacles, validating wave propagation in a 2-D setting with directional diversity.

## Key Characteristics
- Duration: 6 hours
- Grid: 2-D PROPAGATION TEST 2.4 style grid on SPHE with a curvilinear layout
- Propagation: 2-D with both X and Y components enabled (flcx = true, flcy = true)
- Output: HS, SPR, DP, DIR among multiple fields, plus EF and TH1M outputs in the OUNF chain
- Output interval: 1 hour (3600 seconds)
- Sources: None (wind and other forcing fields are not explicitly enabled in this test)

## Files
- regtests/ww3_tp1.10/rompy_ww3_tp1_10.yaml
- regtests/ww3_tp1.10/rompy_ww3_tp1_10.py  (if present)

## Running the Test
### Generate Configuration (if Python script is available)
```bash
cd regtests/ww3_tp1.10
python rompy_ww3_tp1_10.py
```

### Run with WW3 (requires WW3 installation)
Follow your standard WW3 workflow with the generated namelist files.
```

## Physics Tested
- 2-D propagation on a curved grid with 2-D directional components; tests the handling of curved coordinates and grid interactions.
