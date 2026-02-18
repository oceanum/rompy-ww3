# WW3 mww3_test_05 Multi-Grid Regression Test

## Test Description

**Test ID**: ww3_mww3_test_05_regression
**Type**: Multi-grid telescoping nests over hurricane with moving grids.
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/mww3_test_05

This test validates a three-grid multi-grid configuration with telescoping nests, ensuring proper information exchange between grids during a hurricane-like forcing scenario with moving grids.

## Key Characteristics
- Duration: 24 hours
- Grids: grd1 (outer, coarse), grd2 (middle), grd3 (inner, high resolution). Nested multi-grid setup with different forcing and resource sharing
- Output: HS FP DP DIR SPR WND CUR (significant wave height, depth, direction, spectral properties, wind, current)
- Output date: 1-hour cadence
- Forcing: winds and currents enabled on outer and inner grids per YAML configuration
- Termination: end of 24h window

## Files
- regtests/mww3_test_05/rompy_ww3_mww3_test_05.yaml
- regtests/mww3_test_05/ (no dedicated Python script present in this repository snapshot)

## Running the Test
### Generate Configuration (if Python script is available)
If a driver script is provided in your checkout, run it here. Otherwise, use the YAML directly within your rompy/WW3 workflow.

### Run with WW3 (requires WW3 installation)
Follow your standard multi-grid WW3 workflow using the generated namelist files.

## Physics Tested
- Multi-grid interaction with telescoping nests and moving grids under hurricane-like forcing.
