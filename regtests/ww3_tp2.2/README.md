# WW3 tp2.2 Regression Test

## Test Description

**Test ID**: ww3_tp2_2_regression
**Type**: 2-D propagation with a spherical grid on a RECT grid; base grid with global-like spectrum.
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.2

This test validates 2-D wave propagation on a spherical grid with a standard rectilinear grid and a base spectrum, focusing on multi-directional propagation and depth handling.

## Key Characteristics
- Duration: 5 days? (check YAML; here duration is 5D; treated as 5 days with 1-hour cadence)
- Grid: 2-D PROPAGATION HALF GLOBE; RECT, SPHE; nx=193, ny=93
- Propagation: flcx: true, flcy: true; dtxy=1.0s or 60s depending on YAML; use 1s cadence if applicable
- Output: HS, DIR, SPR, DP, EF, TH1M, STH1M, TH2M, STH2M
- Output interval: 1 hour
- Depth: data_blob with input files regtests/ww3_tp2.2/input/2-D.depth

## Files
- regtests/ww3_tp2.2/rompy_ww3_tp2_2.yaml
- regtests/ww3_tp2.2/rompy_ww3_tp2_2.py

## Running the Test
### Generate Configuration
```bash
cd regtests/ww3_tp2.2
python rompy_ww3_tp2_2.py
```

### Run with WW3 (requires WW3 installation)
Follow your standard WW3 workflow with the generated namelist files.

## Physics Tested
- 2-D propagation with broad directional coverage; validates 2-D SPHE-grid handling.
