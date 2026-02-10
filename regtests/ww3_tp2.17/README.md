# WW3 tp2.17: Output Post-Processing Test

## Overview

This test validates WAVEWATCH III's output post-processing capabilities using both field output (Ounf) and point output (Ounp) components. It demonstrates comprehensive output configuration with multiple parameters, formats, and temporal resolutions.

## Test Purpose

- **Primary Goal**: Validate output post-processing components
- **Grid Type**: RECT (rectangular, spherical coordinates)
- **Coordinate System**: Spherical (SPHE)
- **Domain Type**: Nested domain for output testing
- **Physics**: Basic propagation with wind forcing and source terms

## Key Configuration

### Grid Parameters
- **Type**: RECT (rectangular)
- **Size**: 200 × 200 grid points
- **Resolution**: 0.5 degree lat-lon spacing
- **Coordinates**: Spherical
- **Closure**: NONE (regional domain)
- **Region**: Nested test domain (-10°E to 90°E, 30°N to 130°N)
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
- **Stop**: 2010-01-03 00:00:00
- **Duration**: 48 hours
- **DTMAX**: 900 s (15 minutes)
- **DTXY**: 300 s (5 minutes)
- **DTKTH**: 300 s (5 minutes)

### Forcing Configuration
- **Wind Input**: Enabled (WINDS='T')
- **Wind Speed**: 10 m/s homogeneous
- **Wind Direction**: 270° (from west)
- **Source Terms**: Enabled (FLSOU=True)
- **Other Forcing**: Ice, current, water level all disabled

### Output Post-Processing Components

#### Field Output (Ounf Component)

The Ounf component configures field output post-processing via ww3_ounf.nml:

| Parameter | Value | Description |
|-----------|-------|-------------|
| Interval | 3600 s (1 hour) | Field output frequency |
| Format | NetCDF4 | Modern NetCDF format with compression |
| Variables | HS, T02, T01, FP, DIR, SPR, DP, PHS, PTP, PDIR, WND, CUR | All wave parameters |
| Partitions | 0, 1, 2, 3 | Total, wind sea, primary swell, secondary swell |
| File Organization | Single file | All variables in one NetCDF file |

**Output Fields:**
- **HS**: Significant wave height (m)
- **T02**: Mean wave period (s)
- **T01**: Mean wave period from inverse frequency (s)
- **FP**: Peak frequency (Hz)
- **DIR**: Mean wave direction (degrees)
- **SPR**: Directional spread (degrees)
- **DP**: Peak wave direction (degrees)
- **PHS**: Partitioned significant wave height (m)
- **PTP**: Partitioned peak period (s)
- **PDIR**: Partitioned mean direction (degrees)
- **WND**: Wind speed (m/s)
- **CUR**: Current speed (m/s)

#### Point Output (Ounp Component)

The Ounp component configures point output post-processing via ww3_ounp.nml:

| Parameter | Value | Description |
|-----------|-------|-------------|
| Interval | 1800 s (30 minutes) | Point output frequency |
| Format | NetCDF4 | Modern NetCDF format |
| Output Type | Type 2 (mean parameters) | Wave statistics at points |
| Points | All from points.list | All defined point locations |
| File Organization | Single file | All points in one NetCDF file |
| Buffer Size | 100 points/pass | Memory management parameter |

**Point Output Types:**
- **Type 0**: Inventory (basic point information)
- **Type 1**: Spectra (full 2D wave spectra)
- **Type 2**: Mean parameters (bulk wave statistics) ✓ **Used in this test**
- **Type 3**: Source terms (physics breakdown)

### Input Files Required

Located in `input/` directory:
- `depth.nested.IDLA1.dat` - Bathymetry data in IDLA format 1
- `points.list` - Point output locations (lon, lat, name format)

### Output Configuration Summary

| Output Type | Component | Executable | Interval | Format | Variables |
|-------------|-----------|------------|----------|--------|-----------|
| Field | Ounf | ww3_ounf | 1 hour | NetCDF4 | 12 wave parameters + partitions |
| Point | Ounp | ww3_ounp | 30 minutes | NetCDF4 | Mean parameters (type 2) |

## Output Post-Processing Theory

### Field vs. Point Output

**Field Output (Ounf):**
- **Purpose**: Gridded spatial fields of wave parameters
- **Format**: 2D or 3D NetCDF arrays (lon, lat, time, [partition])
- **Use Cases**: Spatial visualization, regional analysis, model validation
- **File Size**: Large (full grid at each output time)
- **Processing**: ww3_ounf executable reads restart files and generates field output

**Point Output (Ounp):**
- **Purpose**: Time series at specific locations (virtual buoys)
- **Format**: 1D or 2D NetCDF arrays (point, time, [frequency, direction])
- **Use Cases**: Buoy validation, station forecasts, time series analysis
- **File Size**: Small (few points, high temporal resolution possible)
- **Processing**: ww3_ounp executable reads restart files and extracts point data

### NetCDF Format Options

| Version | Compression | Large Files | CF-Compliant | Recommended |
|---------|-------------|-------------|--------------|-------------|
| NetCDF3 | No | <2 GB | Partial | Legacy only |
| NetCDF4 | Yes | Unlimited | Full | Modern use ✓ |

This test uses NetCDF4 for:
- **Compression**: Reduced file size (10-50% savings)
- **Large File Support**: No 2 GB limit
- **CF Conventions**: Full climate/forecast metadata
- **Modern Tools**: Better tool support (xarray, ncview, Panoply)

### Output Partitioning

WW3 can partition wave fields into components:

| Partition | Index | Description |
|-----------|-------|-------------|
| Total | 0 | All wave energy combined |
| Wind Sea | 1 | Locally generated waves |
| Primary Swell | 2 | Dominant swell system |
| Secondary Swell | 3 | Secondary swell system |

**Partition Algorithm:**
- Separates wind sea from swell based on wave age criteria
- Identifies distinct swell systems by spectral peak separation
- Critical for applications distinguishing local vs. remote wave sources

## Running the Test

### Using Python Script
```bash
cd regtests/ww3_tp2.17
python rompy_ww3_tp2_17.py
```

### Using YAML Configuration
```bash
rompy run rompy_ww3_tp2_17.yaml
```

## Expected Results

- 48-hour simulation with comprehensive output generation
- Field output files: `ww3.YYYYMMDD_hhmmss.nc` (1-hour intervals)
- Point output files: `ww3_points.YYYYMMDD_hhmmss.nc` (30-minute intervals)
- NetCDF4 format with compression and CF metadata
- Partitioned wave parameters (wind sea, swells)
- Time series at point locations
- Gridded spatial fields

## Physics Notes

### Source Term Configuration

This test enables basic source terms for realistic wave evolution:
- **Wind Input**: 10 m/s westerly wind drives wave growth
- **Dissipation**: Whitecapping and bottom friction
- **Nonlinear Interactions**: Wave-wave energy transfer
- **Focus**: Output generation rather than physics complexity

### Wind Forcing

Homogeneous wind field:
- **Speed**: 10 m/s (moderate wind, fetch-limited conditions)
- **Direction**: 270° (from west, eastward wave propagation)
- **Duration**: Constant for 48 hours (steady-state development)
- **Purpose**: Simple forcing for output validation

### Expected Wave Development

- Initial growth phase: 0-12 hours (waves develop under wind forcing)
- Quasi-steady state: 12-48 hours (fetch-limited equilibrium)
- Spatial patterns: Wave height increases along wind fetch
- Temporal evolution: Smooth growth to equilibrium
- Partition development: Wind sea dominates, minimal swell

## Validation

Compare output files with official WW3 reference:
- NetCDF file structure (dimensions, variables, attributes)
- Field output variables and units (verify CF compliance)
- Point output time series (check interpolation accuracy)
- Partition separation (wind sea vs. swell distinction)
- Temporal consistency (no gaps, correct intervals)
- Spatial coverage (full grid, correct geographic bounds)

### NetCDF Verification

Use standard NetCDF tools:

```bash
# Check file structure
ncdump -h ww3.20100101_000000.nc

# View field output
ncview ww3.20100101_000000.nc

# Check point output
ncdump -v hs ww3_points.20100101_000000.nc
```

### Python Verification

```python
import xarray as xr

# Load field output
ds_field = xr.open_dataset("ww3.20100101_000000.nc")
print(ds_field)

# Load point output
ds_point = xr.open_dataset("ww3_points.20100101_000000.nc")
print(ds_point)

# Plot time series
ds_point.hs.plot()
```

## References

- Official WW3 Test: `NOAA-EMC/WW3/regtests/ww3_tp2.17`
- WW3 User Manual: Sections on output post-processing
- NetCDF Climate and Forecast (CF) Conventions

## Related Tests

- **tp2.4**: Basic 2-D propagation (field output only)
- **tp2.15**: Space-time extremes (specialized output)
- **tp2.16**: Data assimilation (input pre-processing)

## Implementation Notes

This test demonstrates:
1. Ounf component configuration for field output post-processing
2. Ounp component configuration for point output post-processing
3. NetCDF4 format for modern output files
4. Multiple output intervals (field vs. point)
5. Output partitioning (wind sea, swells)
6. Comprehensive parameter selection (12+ variables)
7. Memory management (buffer size for point processing)

## Differences from Other Tests

### vs tp2.4 (Basic Field Output)
- **tp2.4**: Field output only, basic parameters
- **tp2.17**: Both field and point output, comprehensive parameters

### vs tp2.15 (STE Output)
- **tp2.15**: Specialized space-time extremes output
- **tp2.17**: Standard output with full parameter set

### vs tp2.16 (Assimilation)
- **tp2.16**: Focus on input pre-processing (assimilation data)
- **tp2.17**: Focus on output post-processing (field and point)

## Scientific Context

Output post-processing is critical for:
- **Model Validation**: Comparing model results to observations
- **Forecast Delivery**: Generating products for end users
- **Data Archiving**: Creating analysis-ready datasets
- **Visualization**: Preparing data for mapping and plotting
- **Time Series Analysis**: Extracting station-specific forecasts

This test validates the infrastructure that enables operational wave forecasting systems to deliver products to mariners, coastal engineers, and climate researchers.

## Technical Details

### Ounf Executable (ww3_ounf)

The ww3_ounf executable:
- Reads model restart files (out_grd.ww3)
- Extracts requested variables at specified times
- Writes gridded NetCDF files with CF metadata
- Supports spatial subsetting and variable selection
- Handles partitioned output (wind sea, swells)

### Ounp Executable (ww3_ounp)

The ww3_ounp executable:
- Reads model restart files (out_pnt.ww3)
- Extracts data at point locations via interpolation
- Writes point-based NetCDF files
- Supports multiple output types (spectra, parameters, sources)
- Optimizes memory usage via buffer parameter

### NetCDF Conventions

Output files follow CF conventions:
- **Standard Names**: CF-compliant variable names
- **Units**: Standard units (m, s, degrees)
- **Coordinates**: Explicit lon/lat coordinate variables
- **Time**: CF time encoding (units since reference)
- **Metadata**: Comprehensive attributes (long_name, standard_name, units)

## Troubleshooting

### Common Issues

**Missing Output Files:**
- Check ww3_shel completed successfully (creates restart files)
- Verify output times match simulation period
- Ensure sufficient disk space for output files

**NetCDF Read Errors:**
- Verify NetCDF4 library installation
- Check file permissions
- Confirm file not corrupted (use ncdump -h)

**Incorrect Variable Values:**
- Check unit conversion (model uses SI units)
- Verify scale factors in configuration
- Compare with reference test output

### Debug Output

Enable detailed logging:
- Check ww3_ounf.log for field output processing
- Check ww3_ounp.log for point output processing
- Monitor disk space during output generation
- Verify restart file availability (out_grd.ww3, out_pnt.ww3)

## Performance Notes

### Output File Sizes

Expected file sizes with NetCDF4 compression:
- Field output: ~50 MB per timestep (200×200 grid, 12+ variables)
- Point output: ~1 MB per timestep (few points, mean parameters)
- Total for 48h: ~2.5 GB field + 100 MB point output

### Processing Time

Typical processing times:
- Field output generation: ~10 seconds per timestep
- Point output generation: <1 second per timestep
- Total post-processing: ~10 minutes for full test

### Memory Requirements

Memory usage:
- Field processing: ~500 MB (grid held in memory)
- Point processing: ~100 MB (buffer size controls memory)
- NetCDF compression: Minimal overhead, significant space savings
