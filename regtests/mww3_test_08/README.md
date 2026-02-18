# WW3 mww3_test_08 Multi-Grid Regression Test

## Test Description

**Test ID**: ww3_mww3_test_08_regression
**Type**: Multi-grid with wind and ice input.
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/mww3_test_08

This test validates multi-grid coupling under wind and ice forcing, ensuring proper data exchange and forcing application across grids.

## Key Characteristics
- Duration: 24 hours
- Grids: input_grid (wind/ice forcing) and two model grids grd_a (outer) and grd_b (inner)
- Output: HS FP DP DIR ICE WND
- Output date: 1 hour cadence
- Forcing: wind and ice forcing enabled; currents disabled

## Files
- regtests/mww3_test_08/rompy_ww3_mww3_test_08.yaml
- regtests/mww3_test_08/ (no dedicated Python script present)

## Running the Test
### Run with WW3 (requires WW3 installation)
Follow your standard multi-grid WW3 workflow using the generated namelist files.

## Physics Tested
- Wind and ice forcing interaction in a multi-grid framework; validates mechanism for forcing propagation across grids.
