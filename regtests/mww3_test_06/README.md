# WW3 mww3_test_06 Multi-Grid Regression Test

## Test Description

**Test ID**: ww3_mww3_test_06_regression
**Type**: Multi-grid with irregular/curvilinear grids including SCRIP regridding.
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/mww3_test_06

This test validates multi-grid interactions when using irregular/curvilinear grids and SCRIP-based regridding, ensuring stable coupling and appropriate information transfer across grids.

## Key Characteristics
- Duration: 6 hours
- Grids: gband360 (global regular grid subset) and arcticsub (arctic curvilinear grid)
- Output: HS FP DP DIR
- Output date: 1 hour cadence
- Forcing: wind forcing enabled on both grids, other forcing terms disabled

## Files
- regtests/mww3_test_06/rompy_ww3_mww3_test_06.yaml
- regtests/mww3_test_06/ (no dedicated Python script present)

## Running the Test
### Run with WW3 (requires WW3 installation)
Follow your standard multi-grid WW3 workflow using the generated namelist files.

## Physics Tested
- Multi-grid interaction with irregular/curvilinear grids and SCRIP regridding.
