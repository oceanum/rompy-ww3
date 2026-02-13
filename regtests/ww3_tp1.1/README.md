# WW3 tp1.1 Regression Test

## Test Description

**Test ID**: ww3_tp1_1_regression
**Type**: 1-D propagation on spherical grid with no source terms (pure propagation).
**Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.1

This test validates pure wave propagation along a spherical meridian on a 1-D cartesian grid mapped to spherical coordinates, with no wind, current, or wave-source terms.

## Key Characteristics
- Duration: 24 days
- Grid: Rectilinear grid on a spherical surface (SPHE), 360 points in the longitudinal direction and 3 points in latitude (nx×ny = 360×3). Grid name: MONOCHROMATIC SHOALING EQUATOR (equatorial configuration)
- Propagation: X-direction (flcx = true, flcy = false) on a spherical grid; no meridional (Y) propagation
- Output: Field output HS (significant wave height); Point output defined by input points file
- Output interval: 1 day (86400 seconds)
- Source terms: NONE (homog_input empty, n_wnd/n_lev/n_cur/n_ice all zero)
- Depth input: Provided via input blob named in the YAML depth configuration
- Boundary/closure: NONE (for this 1-D propagation test on a sphere)

## Files
- regtests/ww3_tp1.1/rompy_ww3_tp1_1.yaml
- regtests/ww3_tp1.1/rompy_ww3_tp1_1.py  (Python configuration generator; if present)
- regtests/ww3_tp1.1/input/ (input data, e.g. 1-D.depth and points.list)

## Running the Test
### Generate Configuration (if Python script is available)
```bash
cd regtests/ww3_tp1.1
python rompy_ww3_tp1_1.py
```

### Run with WW3 (requires WW3 installation)
This will generate WW3 namelists from the YAML and write outputs under rompy_runs/ww3_tp1_1_regression/ by default.
```
# The exact command to run WW3 depends on your backend (local/docker/etc.). Use the backend of your choice and point it at the generated configuration.
```

## Physics Tested
- Pure 1-D propagation on a spherical surface (equator) with no source terms.
- Validation of spherical grid handling, propagation direction, and output timing for a simple travelling wave scenario.
