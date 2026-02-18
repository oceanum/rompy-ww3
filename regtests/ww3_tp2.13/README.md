# WW3 tp2.13: Regional Configuration Test

## Overview

This test validates WAVEWATCH III's handling of regional domain configurations using curvilinear grids with NONE closure (no periodic wrapping).

## Test Purpose

- **Primary Goal**: Validate regional boundary handling in WW3
- **Grid Type**: Curvilinear (CURV)
- **Coordinate System**: Spherical (SPHE)
- **Domain Type**: Regional with NONE closure
- **Physics**: Pure propagation (no source terms)

## Key Configuration

### Grid Parameters
- **Type**: CURV (curvilinear)
- **Size**: 1500 x 200 grid points
- **Coordinates**: Spherical
- **Closure**: NONE (regional, no wrapping)
- **Depth Limit**: ZLIM = -0.1 m
- **Minimum Depth**: DMIN = 7.5 m

### Spectrum Configuration
- **Frequencies**: 3 (NK=3)
- **Directions**: 72 (NTH=72)
- **First Frequency**: 0.03679 Hz
- **Frequency Ratio**: XFR = 1.1

### Time Configuration
- **Start**: 2008-05-22 00:00:00
- **Stop**: 2008-05-22 09:00:00
- **Duration**: 9 hours
- **DTMAX**: 600 s
- **DTXY**: 300 s
- **DTKTH**: 600 s

### Input Files Required

Located in `input/` directory:
- `lon.1500x200` - Longitude coordinate grid (curvilinear)
- `lat.1500x200` - Latitude coordinate grid (curvilinear)
- `depth.1500x200` - Bathymetry data
- `mask1.1500x200` - Land-sea mask
- `namelists_2-D.nml` - Additional physics namelists
- `points.list` - Point output locations

### Output Configuration
- **Field Outputs**: DPT, HS, FP, DIR, SPR
- **Point Outputs**: Time series at specified locations
- **Interval**: 3600 seconds (1 hour)

## Regional vs Global Differences

### NONE Closure (Regional)
- No periodic wrapping at domain boundaries
- Boundary conditions must be explicitly specified or left open
- Used for limited-area domains (coastal, regional seas)
- This test uses open boundaries (no forcing)

### Alternative Closures
- **SMPL**: Simple closure with one open boundary
- **GLOBL**: Global closure with periodic wrapping (longitude)
- **TRPL**: Tripole grid closure (Arctic applications)

## Running the Test

### Using Python Script
```bash
cd regtests/ww3_tp2.13
python rompy_ww3_tp2_13.py
```

### Using rompy CLI
```bash
rompy run rompy_ww3_tp2_13.py
```

## Expected Results

- Model should run without errors for 9-hour simulation
- No waves generated (no forcing input)
- Pure grid initialization and boundary handling test
- Output files should contain DPT, HS, FP, DIR, SPR fields

## Physics Notes

### No Source Terms
This test runs with:
- `FLSOU = False` (no source terms)
- No wind input
- No boundary conditions

This is a pure propagation test focused on:
- Grid geometry handling
- Regional boundary treatment
- Curvilinear coordinate system

## Validation

Compare output files with official WW3 reference:
- NetCDF field output structure
- Point output format
- Grid preprocessing results
- Log file messages

## References

- Official WW3 Test: `NOAA-EMC/WW3/regtests/ww3_tp2.13`
- WW3 User Manual: Section on curvilinear grids
- WW3 User Manual: Section on domain closure types

## Related Tests

- **tp2.10**: SMC grid (also regional with NONE closure)
- **tp2.12**: Tripole grid (TRPL closure for Arctic)
- **tp2.2**: Cartesian regional grid
- **tp2.7**: Unstructured regional grid

## Implementation Notes

This test demonstrates:
1. Curvilinear grid configuration with external coordinate files
2. Regional domain setup (NONE closure)
3. Mask file usage for land-sea boundaries
4. Proper file path references for curvilinear inputs
