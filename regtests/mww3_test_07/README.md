# WW3 mww3_test_07 Multi-Grid Regression Test

## Test Description

**Test ID**: ww3_mww3_test_07_regression
**Type**: Multi-grid with rectangular parent grid and unstructured refug grid with an island.
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/mww3_test_07

This test exercises a parent grid and a refug (unstructured) grid with an island, validating multi-grid coupling and unstructured grid support in presence of topographic/bathymetric features.

## Key Characteristics
- Duration: 6 hours
- Grids: parent (rectangular, no island) and refug (unstructured with island)
- Output: HS FP DP DIR DPT
- Output date: 1/2-hour cadence (1800 seconds)
- Forcing: winds enabled; other forcing terms disabled

## Files
- regtests/mww3_test_07/rompy_ww3_mww3_test_07.yaml
- regtests/mww3_test_07/ (no dedicated Python script present)

## Running the Test
### Run with WW3 (requires WW3 installation)
Follow your standard multi-grid WW3 workflow using the generated namelist files.

## Physics Tested
- Coupling between a rectangular parent grid and an unstructured refug grid with an island; validates grid interaction in a 2-grid setup.
