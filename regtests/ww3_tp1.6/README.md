# WW3 tp1.6 Regression Test

## Test Description

**Test ID**: ww3_tp1_6_regression
**Type**: 1-D propagation with wind forcing and basic output (no depth input changes).
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.6

This test exercises a basic 1-D propagation scenario with wind forcing enabled via the input_nml forcing section, validating the interaction of winds with wave growth in a 1-D spherical/Cartesian setup.

## Key Characteristics
- Duration: 12 hours
- Grid: 1-D Cartesian or spherical configuration as in the YAML; 3×? grid depending on the test; winds forcing enabled (forcing: currents: False, winds: T)
- Propagation: X-direction (flcx = true, flcy = false) depending on configuration
- Output: DPT, CUR, HS in the primary outputs
- Output interval: 15 minutes (900 seconds)
- Source terms: None beyond wind forcing

## Files
- regtests/ww3_tp1.6/rompy_ww3_tp1_6.yaml
- regtests/ww3_tp1.6/rompy_ww3_tp1_6.py  (if present)

## Running the Test
### Generate Configuration (if Python script is available)
```bash
cd regtests/ww3_tp1.6
python rompy_ww3_tp1_6.py
```

### Run with WW3 (requires WW3 installation)
Follow your standard WW3 workflow with the generated namelists.
```

## Physics Tested
- Wind-forced wave evolution in a 1-D setup; validates wind input integration and output fields.
