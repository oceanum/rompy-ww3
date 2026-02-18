# WW3 mww3_test_09 Multi-Grid Regression Test

## Test Description

**Test ID**: ww3_mww3_test_09_regression
**Type**: Multi-grid regression for Great Lakes using SMC (Spherical Multi-Cell) grids.
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/mww3_test_09

This test validates multi-grid Great Lakes configurations on SMC grids, including lake-specific grids and boundaries, under wind forcing only.

## Key Characteristics
- Duration: 12 hours
- Grids: MICHIGAN, HURON, SUPER (as three lakes in a three-grid SMC layout)
- Output: HS FP DP DIR
- Output date: 1 hour cadence
- Forcing: no wind/ice forcing beyond default; wind forcing is turned off in the YAML for this configuration (uses static forcing setup)

## Files
- regtests/mww3_test_09/rompy_ww3_mww3_test_09.yaml
- regtests/mww3_test_09/ (no dedicated Python script present)

## Running the Test
### Run with WW3 (requires WW3 installation)
Follow your standard multi-grid WW3 workflow using the generated namelist files.

## Physics Tested
- Multi-grid propagation in the Great Lakes region with SMC grids; validates cross-grid information exchange and lake-specific boundary handling.
