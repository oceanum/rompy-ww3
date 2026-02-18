# WW3 tp2.14: Boundary Conditions Test

## Overview

This test validates WAVEWATCH III's handling of boundary conditions using the Bound component to read and apply spectral boundary data to a regional domain.

## Test Purpose

- **Primary Goal**: Validate boundary condition preprocessing and application in WW3
- **Grid Type**: Rectangular (RECT)
- **Coordinate System**: Spherical (SPHE)
- **Domain Type**: Regional with boundary forcing
- **Physics**: Propagation with boundary conditions (no internal source terms)

## Key Configuration

### Grid Parameters
- **Type**: RECT (rectilinear)
- **Size**: 225 x 106 grid points
- **Coordinates**: Spherical
- **Closure**: NONE (regional, open boundaries)
- **Depth Limit**: ZLIM = -0.1 m
- **Minimum Depth**: DMIN = 7.5 m
- **Grid Increment**: 0.35457° (both directions)
- **Domain**: Western Pacific region (183.4°E - 263.0°E, 25.1°N - 62.6°N)

### Spectrum Configuration
- **Frequencies**: 3 (NK=3)
- **Directions**: 12 (NTH=12)
- **First Frequency**: 0.03679 Hz
- **Frequency Ratio**: XFR = 1.1

### Time Configuration
- **Start**: 2008-05-22 00:00:00
- **Stop**: 2008-05-22 03:00:00
- **Duration**: 3 hours
- **DTMAX**: 3300 s
- **DTXY**: 1100 s
- **DTKTH**: 1650 s

### Boundary Configuration
- **Component**: Bound (ww3_bound)
- **Mode**: READ (read boundary data from files)
- **Interpolation**: Linear (method 2)
- **Verbosity**: Standard (level 1)
- **Boundary File**: spec.nc (spectral boundary conditions)

### Input Files Required

Located in `input/` directory:
- `depth.225x106.IDLA1.dat` - Bathymetry data
- `spec.nc` - Spectral boundary condition data (netCDF)
- `points.list` - Point output locations
- `namelists_2-D.nml` - Additional physics namelists

### Output Configuration
- **Field Outputs**: DPT, HS, FP, DIR, SPR
- **Point Outputs**: Time series at specified locations
- **Interval**: 3600 seconds (1 hour)

## Boundary Conditions in WW3

### What are Boundary Conditions?
Boundary conditions provide wave spectral information at the edges of a regional model domain. This data is typically:
- Generated from a larger-scale model
- Read from observations or satellite data
- Interpolated to match the local grid

### ww3_bound Component
The Bound component handles:
- Reading spectral boundary data from netCDF files
- Interpolating boundary data to grid boundaries
- Temporal interpolation for model time steps
- Writing processed boundary data for ww3_shel to use

### Boundary Data Format
- **File Format**: NetCDF (spec.nc)
- **Content**: 2D spectra (frequency × direction) at boundary points
- **Time Coverage**: Must span the model run period
- **Spatial Coverage**: All open boundary points

## Running the Test

### Using Python Script
```bash
cd regtests/ww3_tp2.14
python rompy_ww3_tp2_14.py
```

### Using YAML Configuration
```bash
rompy run rompy_ww3_tp2_14.yaml
```

## Expected Results

- Model should run with boundary conditions for 3-hour simulation
- Waves propagate inward from boundaries
- No internal wave generation (no wind forcing)
- Boundary-driven wave field throughout domain
- Output files should contain DPT, HS, FP, DIR, SPR fields

## Physics Notes

### No Internal Source Terms
This test runs with:
- `FLSOU = False` (no source terms)
- No wind input
- Boundary conditions provide ALL wave forcing

This tests:
- Boundary data reading and interpolation
- Wave propagation from boundaries
- Regional model configuration

### Differences from tp2.4
- **tp2.4**: No forcing, pure propagation test
- **tp2.14**: Boundary forcing, wave propagation from edges

## Validation

Compare output files with official WW3 reference:
- NetCDF field output structure
- Point output format
- Boundary data application correctness
- Wave heights and directions near boundaries
- Log file messages from ww3_bound

## References

- Official WW3 Test: `NOAA-EMC/WW3/regtests/ww3_tp2.14`
- WW3 User Manual: Section on boundary conditions
- WW3 User Manual: ww3_bound program documentation

## Related Tests

- **tp2.4**: Same grid, no boundary conditions (pure propagation)
- **tp2.15**: Nested grids with boundary exchanges
- **mww3_test_01**: Multi-grid with internal boundary conditions

## Implementation Notes

This test demonstrates:
1. Bound component configuration with READ mode
2. Spectral boundary data integration
3. Regional model with open boundaries
4. Boundary condition preprocessing workflow
5. Integration of ww3_bound → ww3_grid → ww3_shel sequence

## Execution Sequence

The full workflow includes:
1. **ww3_bound**: Preprocess boundary data (spec.nc → nest.ww3)
2. **ww3_grid**: Generate grid preprocessing files
3. **ww3_shel**: Run main model with boundary forcing
4. **ww3_ounf**: Extract field outputs to NetCDF

The rompy framework orchestrates this sequence automatically.
