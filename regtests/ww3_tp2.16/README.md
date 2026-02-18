# WW3 tp2.16: Data Assimilation Test

## Overview

This test validates WAVEWATCH III's data assimilation capabilities, focusing on mean wave parameter updates from external observation data. Data assimilation allows the model to incorporate real observations to improve forecast accuracy.

## Test Purpose

- **Primary Goal**: Validate data assimilation functionality
- **Grid Type**: RECT (rectangular, spherical coordinates)
- **Coordinate System**: Spherical (SPHE)
- **Domain Type**: Regional test domain for assimilation validation
- **Physics**: Minimal source terms (focus on assimilation updates)

## Key Configuration

### Grid Parameters
- **Type**: RECT (rectangular)
- **Size**: 200 × 200 grid points
- **Resolution**: 1 degree lat-lon spacing
- **Coordinates**: Spherical
- **Closure**: NONE (regional domain)
- **Region**: Generic test domain
- **Depth Limit**: ZLIM = -0.10 m
- **Minimum Depth**: DMIN = 2.50 m

### Spectrum Configuration
- **Frequencies**: 25 (NK=25)
- **Directions**: 24 (NTH=24)
- **First Frequency**: 0.04 Hz
- **Frequency Ratio**: XFR = 1.1
- **Direction Offset**: THOFF = 0.0

### Time Configuration
- **Start**: 2010-01-01 00:00:00
- **Stop**: 2010-01-02 00:00:00
- **Duration**: 24 hours
- **DTMAX**: 900 s (15 minutes)
- **DTXY**: 300 s (5 minutes)
- **DTKTH**: 300 s (5 minutes)

### Data Assimilation Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| MEAN | T | Enable mean wave parameter assimilation |
| SPEC1D | F | Disable 1D spectrum assimilation |
| SPEC2D | F | Disable 2D spectrum assimilation |

**What is Assimilated:**
- **Mean Wave Parameters**: Significant wave height (HS), mean period (T02), mean direction (DIR)
- **Update Frequency**: At model timesteps when observations available
- **Data Format**: External observation files with spatially distributed measurements

### Forcing Configuration
- **Wind Input**: Disabled (WINDS='F')
- **Source Terms**: Disabled (FLSOU=False)
- **Focus**: Pure assimilation test without physics complexity

### Input Files Required

Located in `input/` directory:
- `depth.200x200.IDLA1.dat` - Bathymetry data in IDLA format 1
- `points.list` - Point output locations for validation
- Assimilation data files (mean wave observations) - format depends on WW3 version

### Output Configuration
- **Field Outputs**: HS, T02, DP, DIR, FP, WND
- **Field Interval**: 3600 seconds (1 hour)
- **Point Interval**: 3600 seconds (1 hour)
- **Format**: NetCDF4

## Data Assimilation Theory

### What is Data Assimilation?

Data assimilation combines model forecasts with real observations to produce improved state estimates. In wave modeling, assimilation corrects the wave field using measurements from:
- Buoys
- Satellite altimeters
- HF radar
- Ship observations

### WW3 Assimilation Capabilities

**Mean Wave Assimilation (MEAN='T'):**
- Updates significant wave height, mean period, and mean direction
- Spatially distributes corrections across the wave field
- Most commonly used method for operational forecasting

**1D Spectrum Assimilation (SPEC1D='T'):**
- Assimilates frequency-integrated directional spectra
- More detailed than mean parameters
- Requires directional spectrum observations

**2D Spectrum Assimilation (SPEC2D='T'):**
- Assimilates full 2D frequency-direction spectra
- Most complete assimilation method
- Requires high-quality spectral observations (rare)

### How Assimilation Works in WW3

1. **Model Forecast**: WW3 propagates wave field forward in time
2. **Observation Input**: External files provide measurements at specific locations/times
3. **Analysis Step**: Model state updated by blending forecast with observations
4. **Updated Forecast**: Assimilated state becomes new initial condition
5. **Iteration**: Process repeats at each assimilation time

## Running the Test

### Using Python Script
```bash
cd regtests/ww3_tp2.16
python rompy_ww3_tp2_16.py
```

### Using YAML Configuration
```bash
rompy run rompy_ww3_tp2_16.yaml
```

## Expected Results

- 24-hour simulation with mean wave assimilation
- Model state updates at observation times
- Output fields show assimilated wave parameters
- Verification: Compare assimilated vs. free-running results
- NetCDF4 output files with field data
- Point output time series showing assimilation impact

## Physics Notes

### Assimilation vs. Source Terms

This test intentionally disables source terms (wind input, dissipation, nonlinear interactions):
- **Purpose**: Isolate assimilation functionality
- **Benefit**: Verify assimilation works independently of physics
- **Real Applications**: Combine assimilation with full physics

### Observation Requirements

For data assimilation to work effectively:
- **Spatial Coverage**: Observations should cover key areas of the domain
- **Temporal Coverage**: Regular observation intervals preferred
- **Quality Control**: Bad observations can degrade the solution
- **Error Specification**: Observation uncertainty must be specified

### Assimilation Impact

Expected improvements from assimilation:
- **Reduced Forecast Error**: Initial conditions closer to reality
- **Faster Spin-Up**: Model reaches realistic state quicker
- **Bias Correction**: Systematic model errors partially corrected
- **Skill Improvement**: Better forecast metrics (RMSE, correlation)

## Validation

Compare output files with official WW3 reference:
- NetCDF field output structure and variable names
- Assimilated wave height patterns
- Temporal evolution showing observation impacts
- Point output time series verification
- Compare free-running vs. assimilated solutions

## References

- Official WW3 Test: `NOAA-EMC/WW3/regtests/ww3_tp2.16`
- WW3 User Manual: Section on data assimilation methods
- Operational wave forecasting systems using assimilation

## Related Tests

- **tp2.4**: Pure propagation without assimilation (baseline)
- **tp2.15**: Space-time extremes (STE) parameters
- **tp2.17**: Output post-processing (OUNF/OUNP)

## Implementation Notes

This test demonstrates:
1. Data assimilation configuration in INPUT_NML
2. InputAssim namelist with MEAN/SPEC1D/SPEC2D flags
3. Minimal physics setup for assimilation testing
4. Observation data file references
5. NetCDF4 output with assimilated fields
6. Verification workflow for assimilation impact

## Differences from Other Tests

### vs tp2.4 (Pure Propagation)
- **tp2.4**: No assimilation, pure propagation test
- **tp2.16**: Mean wave assimilation from observations

### vs tp2.15 (Space-Time Extremes)
- **tp2.15**: Full physics with wind forcing and STE output
- **tp2.16**: No physics, focus on assimilation updates

### vs Operational Systems
- **Test**: Simplified domain and minimal physics
- **Operations**: Full physics, real-time observations, complex domains

## Scientific Context

Data assimilation is critical for operational wave forecasting:
- **NOAA WaveWatch III**: Global wave forecasts with satellite assimilation
- **ECMWF WAM**: European wave model with altimeter assimilation
- **Copernicus Marine Service**: Multi-model ensemble with assimilation
- **Regional Systems**: High-resolution forecasts with buoy assimilation

This test validates the core assimilation infrastructure that enables these operational systems to provide accurate wave forecasts for maritime safety, coastal engineering, and climate applications.

## Technical Details

### Observation File Format

WW3 expects observation files in specific formats:
- **ASCII Format**: Space-separated columns (time, lon, lat, HS, T02, DIR)
- **NetCDF Format**: Structured with time/space dimensions
- **Units**: SI units (m for HS, s for periods, degrees for DIR)

### Assimilation Algorithms

WW3 supports multiple assimilation methods:
- **Optimal Interpolation (OI)**: Simple, computationally efficient
- **Ensemble Methods**: More sophisticated, higher cost
- **Variational Methods**: Advanced techniques for research applications

This test typically uses OI for computational efficiency and robustness.

## Troubleshooting

### Common Issues

**No Assimilation Updates:**
- Check observation file paths and formats
- Verify observation times overlap model run period
- Ensure MEAN='T' in INPUT_NML

**Model Instability:**
- Bad observations can cause blow-up
- Check observation quality control
- Verify observation error specification

**Incorrect Results:**
- Compare with free-running case (no assimilation)
- Verify observation values are reasonable
- Check assimilation time windows

### Debug Output

Enable assimilation diagnostics:
- Check log files for assimilation messages
- Monitor number of observations assimilated
- Review analysis increments (differences from forecast)
