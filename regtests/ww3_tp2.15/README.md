# WW3 tp2.15: Space-Time Extremes Parameters Test

## Overview

This test validates WAVEWATCH III's space-time extremes (STE) parameter formulations using wind-driven wave growth in the Adriatic Sea near the ISMAR research platform Acqua Alta.

## Test Purpose

- **Primary Goal**: Validate space-time extremes parameter calculations
- **Grid Type**: Curvilinear (CURV) with Lambert conformal projection
- **Coordinate System**: Spherical (SPHE)
- **Domain Type**: Regional wind-driven wave growth
- **Physics**: Full source terms with wind input (ST4/ST6)

## Key Configuration

### Grid Parameters
- **Type**: CURV (curvilinear)
- **Size**: 43 × 42 grid points
- **Resolution**: 15 km spacing
- **Projection**: Lambert conformal
- **Coordinates**: Spherical
- **Closure**: NONE (regional domain)
- **Region**: Adriatic Sea near Acqua Alta platform
- **Depth Limit**: ZLIM = -0.10 m
- **Minimum Depth**: DMIN = 2.50 m

### Spectrum Configuration
- **Frequencies**: 40 (NK=40)
- **Directions**: 36 (NTH=36)
- **First Frequency**: 0.05 Hz
- **Frequency Ratio**: XFR = 1.1
- **Direction Offset**: THOFF = 0.5

### Time Configuration
- **Start**: 2014-03-10 00:00:00
- **Stop**: 2014-03-10 06:00:00
- **Duration**: 6 hours
- **DTMAX**: 900 s (15 minutes)
- **DTXY**: 450 s (7.5 minutes)
- **DTKTH**: 450 s (7.5 minutes)

### Space-Time Extremes Parameters

The test outputs the following STE parameters:

| Output Code | Full Name | Description |
|-------------|-----------|-------------|
| MXE | STMAXE | Maximum surface elevation |
| MXES | STMAXD | Standard deviation of max surface elevation |
| MXH | HMAXE | Maximum wave height |
| MXHC | HCMAXE | Maximum wave height from crest |
| SDMH | HMAXD | Standard deviation of max wave height |
| SDMHC | HCMAXD | Standard deviation of max height from crest |

### Forcing Configuration
- **Wind Input**: Enabled (WINDS='T')
- **Wind Source**: COSMO-ME model data (Italian meteorological service)
- **Source Terms**: ST4 or ST6 physics package
- **Other Forcing**: None (wind-driven only)

### Input Files Required

Located in `input/` directory:
- `lon_ste_adri_15km.dat` - Longitude coordinate data for curvilinear grid
- `lat_ste_adri_15km.dat` - Latitude coordinate data for curvilinear grid
- `ste_adri_15km_etopo1.depth` - Bathymetry data from ETOPO1
- `ste_adri_15km_etopo1.mask` - Land-sea mask
- `points.list` - Point output locations
- `namelists_ADRIATIC.nml` - Physics parameter namelists
- Wind forcing files from COSMO-ME model

### Output Configuration
- **Field Outputs**: HS, WND, T02, DP, DIR, FP, MXE, MXES, MXH, MXHC, SDMH, SDMHC
- **Field Interval**: 900 seconds (15 minutes)
- **Point Interval**: 3600 seconds (1 hour)

## Space-Time Extremes Theory

### What are Space-Time Extremes?

Space-time extremes (STE) describe the statistical properties of maximum wave characteristics within a specified spatial and temporal window. These parameters are crucial for:
- Extreme event prediction
- Coastal engineering design
- Wave climate assessment
- Risk analysis

### STE Parameter Definitions

**STMAXE (MXE)**: Maximum surface elevation within the space-time window. Represents the highest water surface displacement.

**STMAXD (MXES)**: Standard deviation of maximum surface elevation. Quantifies the variability in maximum elevations.

**HMAXE (MXH)**: Maximum wave height (trough to crest) within the window. Critical for structural design.

**HCMAXE (MXHC)**: Maximum wave height measured from crest only. Important for wave impact calculations.

**HMAXD (SDMH)**: Standard deviation of maximum wave heights. Measures extreme wave variability.

**HCMAXD (SDMHC)**: Standard deviation of crest-only maximum heights. Crest-specific variability measure.

## Running the Test

### Using Python Script
```bash
cd regtests/ww3_tp2.15
python rompy_ww3_tp2_15.py
```

### Using YAML Configuration
```bash
rompy run rompy_ww3_tp2_15.yaml
```

## Expected Results

- 6-hour wind-driven wave simulation
- Space-time extremes parameters computed at 15-minute intervals
- Wave growth from wind forcing in Adriatic Sea
- Output includes standard wave parameters plus STE metrics
- NetCDF4 output files with field data
- Point output time series at specified locations

## Physics Notes

### Curvilinear Grid Advantages
This test uses a curvilinear grid with Lambert conformal projection:
- Better representation of complex coastlines
- Reduced grid distortion for regional domains
- More accurate wave propagation near boundaries
- Efficient resolution distribution

### Wind-Driven Wave Growth
The COSMO-ME wind data drives wave generation and growth:
- Full source term physics (ST4 or ST6)
- Wind input parameterization
- Wave dissipation and nonlinear interactions
- Local wind-wave generation

### STE Calculation
Space-time extremes are computed by:
1. Tracking maximum values within sliding windows
2. Computing statistical moments (mean, std dev)
3. Distinguishing between trough-crest and crest-only measures
4. Outputting at regular intervals for time evolution

## Validation

Compare output files with official WW3 reference:
- NetCDF field output structure and variable names
- STE parameter values and distributions
- Spatial patterns in Adriatic Sea
- Temporal evolution of extremes
- Point output time series

## References

- Official WW3 Test: `NOAA-EMC/WW3/regtests/ww3_tp2.15`
- WW3 User Manual: Section on space-time extremes
- COSMO-ME: Italian meteorological model documentation
- ISMAR Acqua Alta Platform: <https://www.ismar.cnr.it/>

## Related Tests

- **tp2.4**: Pure propagation on spherical grid (no forcing)
- **tp2.10**: SMC grid with multi-resolution
- **tp2.14**: Boundary condition test (spectral boundaries)

## Implementation Notes

This test demonstrates:
1. Curvilinear grid configuration with coordinate files
2. Lambert conformal projection for regional domains
3. Space-time extremes parameter output
4. Wind forcing from external model data
5. Full physics source terms (ST4/ST6)
6. NetCDF4 output with extended variable list

## Differences from Other Tests

### vs tp2.4 (Pure Propagation)
- **tp2.4**: No forcing, pure propagation test
- **tp2.15**: Wind-driven with full source terms and STE output

### vs tp2.10 (SMC Grid)
- **tp2.10**: SMC multi-resolution grid, Lake Erie
- **tp2.15**: Curvilinear Lambert projection, Adriatic Sea

### vs tp2.14 (Boundary Conditions)
- **tp2.14**: Boundary forcing only, no internal sources
- **tp2.15**: Wind forcing with internal wave generation

## Scientific Context

The Adriatic Sea provides an ideal test case for STE parameters:
- Semi-enclosed basin with complex bathymetry
- Strong wind events (Bora, Sirocco winds)
- Well-instrumented with Acqua Alta platform
- Available model data from Italian meteorological service
- Historical extreme wave observations for validation

The 15km resolution balances computational efficiency with adequate representation of mesoscale features driving wave extremes.
