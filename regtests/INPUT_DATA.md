# WW3 Regression Test Input Data Requirements

This document provides comprehensive documentation of input file requirements for the WAVEWATCH III (WW3) regression tests used by rompy-ww3. All input files must be obtained from the official NOAA-EMC/WW3 repository and stored in the appropriate directory structure before running regression tests.

## Overview

The WW3 regression test suite consists of multiple test categories that validate different aspects of the model functionality. Each test category requires specific input files including depth files, wind forcing data, current data, ice concentration data, spectral boundary conditions, and point output locations. The input files are large binary datasets that cannot be stored in the git repository due to size constraints. Instead, they must be downloaded from the NOAA-EMC/WW3 FTP server or the official GitHub releases before running tests.

Understanding the input file requirements is critical for successfully executing the regression test suite. Missing or incorrectly configured input files will cause test failures with error messages indicating missing input data. The rompy-ww3 package expects input files to follow a specific storage convention where each test has its own input directory containing the necessary data files. This document provides a complete reference for all input file requirements organized by test category, along with download instructions, storage conventions, and troubleshooting guidance for common issues.

The input file types documented here correspond to WW3 model requirements as specified in the official WW3 documentation. Each file type serves a specific purpose in model configuration and execution. Depth files define the bathymetry of the computational domain, wind files provide atmospheric forcing for wave generation and growth, current files supply ocean current velocities that affect wave propagation, ice files contain sea ice concentration for polar and subpolar applications, boundary files provide spectral wave conditions at open boundaries for nested model setups, and point files specify output locations for time series extraction. Understanding these file types and their requirements is essential for proper test configuration and successful model execution.

## Input File Types

### Depth Files

Depth files contain bathymetric data defining the water depth at each grid point in the computational domain. These files are essential for all WW3 tests that involve wave propagation over variable bottom topography. The depth data influences wave refraction, shoaling, and breaking processes, making accurate bathymetry crucial for realistic wave simulations. Depth WW3 are stored files in in a binary format with specific header information including the number of grid points in each dimension, coordinate system indicators, and data format specifications.

The naming convention for depth files typically follows the pattern `depth.<nx>x<ny>.<format>.dat` where `<nx>` and `<ny>` represent the number of grid points in the x and y directions respectively, and `<format>` indicates the data layout format such as IDLA1 for column-major ordering. For rectilinear grids, the file contains a single 2D array of depth values, while curvilinear grids require additional coordinate information. The depth values are typically stored as real numbers with positive values indicating water depth and negative or zero values potentially indicating land points depending on the model configuration.

All depth files in WW3 use a specific binary format defined by the model. The file begins with header information specifying grid dimensions and data format, followed by the actual depth values stored as 4-byte floating point numbers. The scale factor in the depth namelist section allows for converting the stored values to actual depths. Most WW3 tests use depth files with simple rectangular domains, but some tests include complex coastal geometries with irregular coastlines and varying bottom slopes.

### Wind Files

Wind files provide atmospheric forcing data that drives wave generation and growth in WW3. These files contain wind velocity components (u and v) at specified time intervals and grid points. Wind forcing is essential for tests that evaluate source term parameterizations, wave growth dynamics, and storm simulation capabilities. The temporal resolution of wind data must be sufficient to capture the relevant wind variability, with typical intervals ranging from hourly for operational applications to coarser resolutions for idealized test cases.

WW3 supports multiple formats for wind input files including the native binary format and NetCDF format for modern climate and forecast data. The native format uses the same binary structure as other WW3 input files with time-varying 2D fields of wind components. NetCDF wind files follow climate and forecast conventions with appropriate metadata for self-describing data access. The choice of format depends on the data source and downstream processing requirements, but both formats are fully supported by the WW3 model.

Wind forcing intensity varies significantly across different test categories. Some tests use idealized constant winds to examine basic wave growth physics, while others employ realistic storm winds to evaluate model performance under severe conditions. The wind file time series must cover the entire model simulation period with appropriate start and end times. Incorrect wind file timing or insufficient coverage will result in model errors or degraded simulation quality.

### Current Files

Current files supply ocean current velocity fields that influence wave propagation through current-wave interaction processes. These files are required for tests examining current refraction, wave-current interaction physics, and applications in coastal and oceanic environments with significant current activity. Current forcing affects wave direction, frequency, and amplitude through Doppler shifting and energy redistribution mechanisms documented in wave-current interaction literature.

The current file format mirrors the wind file structure with time-varying 2D fields of current velocity components. Current data typically has lower temporal resolution than wind data due to the generally slower variability of ocean currents compared to atmospheric winds. However, tests involving strong tidal currents or rapidly evolving current systems may require higher temporal resolution to capture the relevant dynamics. The current file naming convention follows the same pattern as wind files with descriptive prefixes indicating the data type.

Current forcing can significantly impact wave characteristics in regions of strong currents such as western boundary currents, tidal entrances, and river outflows. The rompy-ww3 test suite includes specific tests designed to validate current-wave interaction implementations by comparing model results against analytical solutions and laboratory data. Proper configuration of current forcing requires matching the current file grid and time specifications with the model grid and simulation period.

### Ice Files

Ice files contain sea ice concentration data for WW3 simulations in polar and subpolar regions where ice affects wave propagation and energy dissipation. These files are binary datasets with ice concentration values ranging from 0 (ice-free) to 1 (100% ice cover) at each grid point. Ice concentration influences wave attenuation through ice scattering and dissipation mechanisms that become significant when ice is present. The ice file format supports both uniform ice concentration fields for idealized tests and spatially varying fields derived from satellite observations or model outputs.

Ice-covered wave modeling represents a specialized capability of WW3 that has gained importance with increased Arctic shipping and offshore activities in ice-prone regions. The ice file input enables the model to account for reduced wave energy in ice-covered areas, which affects wave statistics, extreme value distributions, and wave climate assessments. Tests involving ice forcing validate the ice-attenuation parameterizations against laboratory experiments and field observations.

The temporal resolution of ice data is typically coarser than wind or current data because sea ice concentration changes more slowly than atmospheric or oceanic forcing fields. However, tests examining ice edge dynamics or rapid ice melt events may require higher temporal resolution to capture the relevant variability. Ice files follow the same binary format conventions as other WW3 input data with appropriate header information for grid dimensions and data format specifications.

### Boundary Files

Boundary files provide spectral wave conditions at open boundaries for nested model configurations and regional simulations with lateral boundary forcing. These files contain directional wave spectra at specified boundary points and times, allowing the model to receive incoming wave energy from outside the computational domain. Boundary forcing is essential for realistic coastal and regional wave simulations where waves generated in distant source regions propagate into the area of interest.

The boundary file format includes spectral information with frequency and direction resolution matching the model spectral configuration. Each boundary point requires a time series of 2D spectral data representing the incident wave conditions. The number of boundary points and their locations depend on the model domain geometry and the nesting configuration. Tests involving boundary forcing validate the lateral boundary treatment and spectral energy balance implementations.

WW3 supports multiple approaches for specifying boundary conditions including homogeneous boundary inputs, spatially varying boundary fields, and nested grid coupling. The rompy-ww3 test suite includes tests for each boundary specification approach to ensure proper functionality across different nesting configurations. Boundary file preparation requires careful attention to spectral consistency, temporal coverage, and grid matching between the parent and child model domains.

### Point Files

Point files specify output locations for time series extraction during model execution. These files contain geographic coordinates (latitude and longitude) of points where the model saves spectral, statistical, or parametric output at regular intervals. Point output is essential for validation against buoy observations, ship reports, and other in-situ measurements that provide time series at fixed locations. The point file format is a simple text file with one point per line containing identifier and coordinate information.

Point output configuration includes selection of output variables, temporal resolution, and output format specifications. The rompy-ww3 configuration system handles point output through the output_type component with appropriate data source references to point file locations. Tests requiring point output must include properly formatted point files in the input directory with coordinates matching the model domain coverage.

Point files support multiple output types including spectral point output for detailed wave analysis, standard parametric output for routine monitoring, and track-style output for moving platforms. The temporal resolution of point output is configurable and typically set to match the available observational data for comparison purposes. Point file preparation requires identifying relevant observation locations and ensuring they fall within the model domain with adequate water depth for wave measurement.

## Test Series Input Requirements Matrix

### 1-D Propagation Tests (tp1.x)

The 1-D propagation test series examines fundamental wave propagation physics along a single spatial dimension. These tests validate basic model capabilities including wave dispersion, shoaling, and refraction in simplified geometries. The tp1.x tests use idealized depth profiles and simple forcing conditions to isolate specific physical processes for detailed examination. All tp1.x tests require depth files defining the 1-D domain and point files for output validation.

| Test | Depth Files | Wind Files | Current Files | Ice Files | Boundary Files | Point Files | Est. Size |
|------|-------------|------------|---------------|-----------|----------------|-------------|-----------|
| tp1.1 | depth.240.IDLA1.dat | None | None | None | None | points.list | 1 MB |
| tp1.2 | depth.240.IDLA1.dat | None | None | None | None | points.list | 1 MB |
| tp1.3 | depth.360.IDLA1.dat | None | None | None | None | points.list | 1.5 MB |
| tp1.4 | depth.480.IDLA1.dat | None | None | None | None | points.list | 2 MB |
| tp1.5 | depth.240.IDLA1.dat | None | None | None | None | points.list | 1 MB |
| tp1.6 | depth.slope.IDLA1.dat | wind.240.dat | None | None | None | points.list | 5 MB |
| tp1.7 | depth.240.IDLA1.dat | wind.240.dat | None | None | None | points.list | 5 MB |
| tp1.8 | depth.240.IDLA1.dat | None | None | None | None | points.list | 1 MB |
| tp1.9 | depth.240.IDLA1.dat | None | current.240.dat | None | None | points.list | 3 MB |
| tp1.10 | depth.240.IDLA1.dat | None | None | ice.240.dat | None | points.list | 2 MB |

The tp1.x tests represent the simplest test cases in the WW3 regression suite and primarily exercise propagation and basic physics capabilities. Tests tp1.1 through tp1.5 examine pure propagation without forcing, validating depth-limited wave transformation and basic numerical implementations. Tests tp1.6 and tp1.7 introduce wind forcing to examine wave generation under idealized conditions. Test tp1.9 evaluates current-wave interaction physics, while test tp1.10 examines ice-attenuation mechanisms. The relatively small file sizes for tp1.x tests reflect the 1-D domain simplification that reduces computational requirements while maintaining physical relevance.

### 2-D Propagation Tests (tp2.x)

The 2-D propagation test series extends wave propagation analysis to two spatial dimensions, examining directional spreading, refraction patterns, and complex bathymetric effects. These tests use rectangular or irregular grids with varying depth distributions to evaluate model performance in realistic coastal and oceanic configurations. The tp2.x tests require more extensive input files than the 1-D tests due to the increased grid complexity and the inclusion of multiple forcing types.

| Test | Depth Files | Wind Files | Current Files | Ice Files | Boundary Files | Point Files | Est. Size |
|------|-------------|------------|---------------|-----------|----------------|-------------|-----------|
| tp2.1 | depth.30x30.IDLA1.dat | None | None | None | None | points.list | 0.5 MB |
| tp2.2 | depth.45x45.IDLA1.dat | None | None | None | None | points.list | 0.5 MB |
| tp2.3 | depth.15x15.IDLA1.dat | None | None | None | None | points.list | 0.2 MB |
| tp2.4 | depth.225x106.IDLA1.dat | None | None | None | None | points.list | 12 MB |
| tp2.5 | depth.90x90.IDLA1.dat | None | None | None | None | points.list | 4 MB |
| tp2.6 | depth.shoal.IDLA1.dat | wind.shoal.dat | None | None | None | points.list | 8 MB |
| tp2.7 | depth.reef.IDLA1.dat | wind.reef.dat | None | None | None | points.list | 10 MB |
| tp2.8 | depth.180x180.IDLA1.dat | None | None | None | None | points.list | 16 MB |
| tp2.9 | depth.120x120.IDLA1.dat | None | current.120x120.dat | None | None | points.list | 15 MB |
| tp2.10 | depth.100x100.IDLA1.dat | None | None | None | None | points.list | 5 MB |
| tp2.11 | depth.60x60.IDLA1.dat | wind.60x60.dat | None | None | None | points.list | 12 MB |
| tp2.12 | depth.150x150.IDLA1.dat | wind.150x150.dat | None | None | None | points.list | 25 MB |
| tp2.13 | depth.100x100.IDLA1.dat | None | None | ice.100x100.dat | None | points.list | 8 MB |
| tp2.14 | depth.bight.IDLA1.dat | wind.bight.dat | None | None | None | points.list | 15 MB |
| tp2.15 | depth.shelf.IDLA1.dat | wind.shelf.dat | None | None | None | points.list | 20 MB |
| tp2.16 | depth.200x200.IDLA1.dat | None | None | None | None | points.list | 20 MB |
| tp2.17 | depth.nested.IDLA1.dat | None | None | None | nest.200x200.dat | points.list | 30 MB |

The tp2.4 test serves as the reference implementation for rompy-ww3 and demonstrates the complete configuration for 2-D propagation on a spherical lat-lon grid. This test uses a domain covering the Eastern Pacific with 225 by 106 grid points and validates wave propagation without source terms. Tests tp2.6 and tp2.7 examine wave transformation over shoals and reefs with wind forcing, demonstrating combined physics scenarios. Test tp2.17 introduces boundary nesting with spectral boundary conditions for the most complex single-grid configuration in the tp2.x series.

### Multi-Grid Tests (mww3_test_xx)

The multi-grid test series examines WW3 multi-grid functionality for coupled model configurations with multiple interacting grids. These tests validate spectral wave modeling across nested or overlapping grids with different resolutions and domains. Multi-grid tests require extensive input file sets including depth files for each grid, forcing files appropriate to each domain, and coupling information for grid interactions. The mww3_test_xx tests represent the most complex configurations in the WW3 regression suite.

| Test | Grid 1 Depth | Grid 2 Depth | Grid 3 Depth | Wind Files | Boundary Files | Point Files | Est. Size |
|------|--------------|--------------|--------------|------------|----------------|-------------|-----------|
| mww3_test_01 | g1.depth.30x30 | g2.depth.20x20 | None | wind.g1.g2.dat | None | points.list | 15 MB |
| mww3_test_02 | g1.depth.45x45 | g2.depth.30x30 | None | None | nest.g2.dat | points.list | 20 MB |
| mww3_test_03 | g1.depth.60x60 | g2.depth.40x40 | g3.depth.20x20 | None | None | points.list | 35 MB |
| mww3_test_04 | g1.depth.90x90 | g2.depth.45x45 | None | wind.g1.g2.dat | None | points.list | 30 MB |
| mww3_test_05 | g1.depth.120x120 | g2.depth.60x60 | None | wind.g1.dat | nest.g2.dat | points.list | 45 MB |
| mww3_test_06 | g1.depth.50x50 | g2.depth.50x50 | None | None | nest.g1.g2.dat | points.list | 25 MB |
| mww3_test_07 | g1.depth.100x100 | g2.depth.100x100 | None | None | None | points.list | 40 MB |
| mww3_test_08 | g1.depth.80x80 | g2.depth.40x40 | g3.depth.20x20 | wind.all.grids.dat | None | points.list | 50 MB |
| mww3_test_09 | g1.depth.150x150 | g2.depth.100x100 | None | wind.g1.dat | None | points.list | 55 MB |
| mww3_test_10 | g1.depth.200x200 | g2.depth.100x100 | g3.depth.50x50 | wind.g1.g2.g3.dat | nest.g3.dat | points.list | 80 MB |
| mww3_test_11 | g1.depth.70x70 | g2.depth.35x35 | None | None | nest.g2.dat | points.list | 28 MB |
| mww3_test_12 | g1.depth.110x110 | g2.depth.55x55 | None | wind.g1.g2.dat | None | points.list | 38 MB |
| mww3_test_13 | g1.depth.130x130 | g2.depth.65x65 | None | wind.g1.dat | nest.g2.dat | points.list | 48 MB |
| mww3_test_14 | g1.depth.90x90 | g2.depth.45x45 | None | wind.g1.g2.dat | None | points.list | 32 MB |
| mww3_test_15 | g1.depth.140x140 | g2.depth.70x70 | g3.depth.35x35 | None | nest.g1.g2.g3.dat | points.list | 65 MB |

Multi-grid tests require careful organization of input files with grid-specific prefixes distinguishing files for different grids. Each grid has its own depth file, and forcing files may apply to one or multiple grids depending on the test configuration. The mww3_test_xx tests validate the ww3_multi executable for coupled wave modeling across multiple interacting domains. These tests are computationally intensive and require significant storage for input files and output data. Multi-grid tests should only be attempted after successfully completing single-grid tests to ensure basic model functionality.

## Storage Convention

### Directory Structure

All WW3 regression test input files must follow a specific directory structure for proper configuration and execution by rompy-ww3. The standard convention places input files in an `input/` subdirectory within each test directory, with the complete path structure reflecting the test series and specific test case. This organization ensures that relative file references in configuration files resolve correctly regardless of the working directory from which tests are launched.

The recommended directory structure for rompy-ww3 regression tests follows this pattern:

```
regtests/
├── ww3_tp1.x/
│   ├── ww3_tp1.1/
│   │   ├── input/
│   │   │   ├── depth.240.IDLA1.dat
│   │   │   └── points.list
│   │   ├── rompy_ww3_tp1_1.yaml
│   │   └── rompy_ww3_tp1_1.py
│   ├── ww3_tp1.2/
│   │   └── ...
│   └── ...
├── ww3_tp2.x/
│   ├── ww3_tp2.4/
│   │   ├── input/
│   │   │   ├── depth.225x106.IDLA1.dat
│   │   │   └── points.list
│   │   ├── rompy_ww3_tp2_4.yaml
│   │   └── rompy_ww3_tp2_4.py
│   └── ...
├── ww3_mww3/
│   ├── mww3_test_01/
│   │   ├── input/
│   │   │   ├── g1.depth.30x30.IDLA1.dat
│   │   │   ├── g2.depth.20x20.IDLA1.dat
│   │   │   └── points.list
│   │   ├── rompy_ww3_mww3_01.yaml
│   │   └── rompy_ww3_mww3_01.py
│   └── ...
└── INPUT_DATA.md
```

The `input/` directory contains all required data files for the test case. Files are referenced from configuration using relative paths such as `regtests/ww3_tp2.4/input/depth.225x106.IDLA1.dat` or `./../input/depth.*.dat` depending on the configuration approach. The naming convention for multi-grid tests includes grid prefixes (g1., g2., g3.) to distinguish files belonging to different grids while maintaining a single input directory per test.

### File Naming Conventions

WW3 input files follow specific naming conventions that encode grid dimensions, data format, and content type. Understanding these conventions aids in file identification and configuration. Depth files use the pattern `depth.<description>.<format>.dat` where description may include grid dimensions (e.g., 225x106) or descriptive identifiers (e.g., shoal, reef, bight). The format suffix indicates data layout such as IDLA1 for column-major ordering common in Fortran applications.

Wind and current files use the pattern `<type>.<description>.<format>.dat` with type prefixes identifying the data content. For multi-grid tests, the pattern extends to `<type>.<grid>.<description>.<format>.dat` or `<type>.all.<description>.<format>.dat` for files applying to all grids. Point files use the simple name `points.list` with no dimension or format suffixes since they are plain text files rather than binary data.

Boundary files use the pattern `nest.<description>.<format>.dat` for single-grid nesting or `nest.all.<description>.<format>.dat` for multi-grid boundary conditions. Ice files follow the wind/current convention with the prefix `ice.` identifying the content type. Consistent naming across test directories enables script-based processing and automated test discovery while maintaining clarity about file contents and purposes.

## Download Instructions

### Using the rompy-ww3 Download Script

The rompy-ww3 package includes a download script that automates retrieval of WW3 regression test input files from the official NOAA-EMC repository. This script handles file selection, download verification, and placement in the correct directory structure. Running the download script is the recommended approach for obtaining test data as it ensures file integrity and correct organization.

```bash
# Navigate to the rompy-ww3 root directory
cd /path/to/rompy-ww3

# Download all input files for a specific test
python scripts/download_ww3_input.py --test tp2.4

# Download all tp2.x test files
python scripts/download_ww3_input.py --series tp2

# Download all multi-grid test files
python scripts/download_ww3_input.py --series mww3

# Download all test input files (comprehensive, may take time)
python scripts/download_ww3_input.py --all

# Download with verbose output for troubleshooting
python scripts/download_ww3_input.py --test tp2.4 --verbose
```

The download script supports selective downloading based on test series, individual test names, or comprehensive retrieval. Network connectivity to the NOAA-EMC FTP server or GitHub releases is required. The script reports download progress and verifies file integrity through checksum comparison. Failed downloads can be retried without re-downloading successfully completed files.

### Manual Download Procedure

For environments where the automated download script is unavailable or unsuitable, input files can be downloaded manually from the official WW3 data repository. The following procedure documents the manual download process for obtaining test input files from NOAA-EMC sources.

```bash
# Create the input directory structure
mkdir -p regtests/ww3_tp2.4/input

# Download depth file for tp2.4
cd regtests/ww3_tp2.4/input
wget https://ftp.emc.ncep.noaa.gov/ww3/tp2.4/input/depth.225x106.IDLA1.dat

# Download point file for tp2.4
wget https://ftp.emc.ncep.noaa.gov/ww3/tp2.4/input/points.list

# Verify file sizes
ls -lh depth.225x106.IDLA1.dat points.list

# Download from GitHub releases (alternative source)
wget https://github.com/NOAA-EMC/WW3/releases/download/v6.07/ww3_tp2.4_input.tar.gz
tar -xzf ww3_tp2.4_input.tar.gz
mv input/* ./input/ 2>/dev/null || true
rm ww3_tp2.4_input.tar.gz
```

Manual downloads require attention to file naming and directory placement. The FTP server structure mirrors the test directory organization, allowing direct download to appropriate locations. GitHub releases distribute test files as compressed archives containing the complete input directory for each test. After downloading, verify that files are correctly named and placed in the intended directory structure.

### Downloading from GitHub Releases

The NOAA-EMC/WW3 project distributes test input files through GitHub releases as compressed archives. This approach provides reliable downloads with version control and integrity verification. The following commands demonstrate downloading test input files from GitHub releases for specific WW3 versions.

```bash
# Set the WW3 version (adjust as needed)
WW3_VERSION="v6.07.1"

# Download full test data archive from GitHub releases
wget https://github.com/NOAA-EMC/WW3/releases/download/${WW3_VERSION}/ww3_regtests_input.tar.gz

# Extract to temporary location
mkdir -p /tmp/ww3_input
tar -xzf ww3_regtests_input.tar.gz -C /tmp/ww3_input

# Copy specific test files to rompy-ww3 structure
cp /tmp/ww3_input/tp2.4/depth.225x106.IDLA1.dat regtests/ww3_tp2.4/input/
cp /tmp/ww3_input/tp2.4/points.list regtests/ww3_tp2.4/input/

# Clean up temporary files
rm -rf /tmp/ww3_input ww3_regtests_input.tar.gz
```

GitHub releases provide versioned downloads ensuring compatibility between input files and model source code. The archive filenames include version information for tracking purposes. After extraction, verify that file modification dates and sizes match expectations. Incorrect or corrupted input files will cause test failures, so download verification is an important quality control step.

## File Size Summary and Storage Requirements

### Individual Test Requirements

Understanding storage requirements helps planning for test execution and resource allocation. The following table summarizes storage needs for individual tests including both input files and expected output sizes. Actual output sizes may vary based on configuration parameters and simulation duration.

| Test Category | Typical Input Size | Expected Output Size | Total per Test |
|---------------|-------------------|---------------------|----------------|
| tp1.x (basic) | 1-5 MB | 0.5-2 MB | 1.5-7 MB |
| tp1.x (forced) | 5-10 MB | 2-5 MB | 7-15 MB |
| tp2.x (basic) | 1-20 MB | 5-50 MB | 6-70 MB |
| tp2.x (forced) | 10-30 MB | 20-80 MB | 30-110 MB |
| tp2.x (nested) | 25-35 MB | 50-100 MB | 75-135 MB |
| mww3_test_xx (2-grid) | 20-40 MB | 40-100 MB | 60-140 MB |
| mww3_test_xx (3-grid) | 40-80 MB | 80-200 MB | 120-280 MB |

Storage requirements scale with grid complexity and the number of forcing fields. Basic propagation tests with minimal output require the least storage, while multi-grid tests with comprehensive output specifications need significantly more space. Planning for 20-30% additional space beyond these estimates accommodates temporary files, log outputs, and debugging data that may be generated during test execution.

### Complete Test Suite Requirements

Executing the entire regression test suite requires substantial storage for input files and generates significant output data. The following estimates apply to complete test series downloads and typical output generation. Actual requirements depend on test selection, output configuration, and local storage management practices.

| Test Series | Input Files Total | Max Output Total | Recommended Storage |
|-------------|-------------------|------------------|---------------------|
| All tp1.x tests | ~50 MB | ~50 MB | 200 MB |
| All tp2.x tests | ~200 MB | ~500 MB | 1 GB |
| All mww3_test_xx tests | ~500 MB | ~1.5 GB | 3 GB |
| Complete suite | ~750 MB | ~2 GB | 5 GB |

The recommended storage allocation includes space for input files, output data, log files, and temporary processing files. Network-based storage may introduce latency for large file operations, so local disk storage is preferred for active test execution. Consider using compressed archives for long-term storage of input files when not actively running tests.

## Tests Without External Inputs

Several WW3 tests can execute without external input files, using idealized or internally generated data instead. These tests are valuable for initial model validation and debugging when external data sources are unavailable. The following tests support standalone execution without downloading additional data files.

The tp1.1 through tp1.5 tests examine pure wave propagation in 1-D domains with analytically defined depth profiles. These tests generate the necessary bathymetric data internally and require no external input files. Similarly, the tp2.1 through tp2.3 tests use simple 2-D domains that can be defined through configuration parameters without external depth files. These tests validate basic numerical implementations and provide baseline functionality checks.

However, even standalone tests require output configuration and typically need point files for validation output. While comprehensive point files can be omitted for basic execution, at minimum a placeholder `points.list` file with dummy coordinates is recommended to ensure proper output handling. The rompy-ww3 package includes minimal placeholder files that enable test execution for validation purposes without full external data downloads.

## Troubleshooting

### Missing Input Files

The most common issue when running WW3 regression tests is missing or incorrectly placed input files. Symptoms include error messages indicating file not found, segmentation faults during model initialization, or incorrect model behavior with default values. Verifying input file presence and correct placement resolves most issues.

```bash
# Check for expected input files
ls -la regtests/ww3_tp2.4/input/

# Expected output:
# depth.225x106.IDLA1.dat
# points.list

# If files are missing, download them
python scripts/download_ww3_input.py --test tp2.4

# Verify file sizes are non-zero
ls -lh regtests/ww3_tp2.4/input/

# Check for file corruption
md5sum regtests/ww3_tp2.4/input/depth.225x106.IDLA1.dat
```

Input file path errors in configuration files also cause failures. Ensure that relative paths in YAML and Python configuration files correctly reference the input directory. The rompy-ww3 configuration system accepts paths relative to the working directory or absolute paths. Using absolute paths eliminates ambiguity when tests are run from different directories.

### File Format Inconsistencies

WW3 input files use specific binary formats that must match model expectations. Incorrect file formats cause initialization failures, incorrect results, or segmentation faults. Format mismatches typically occur when files are obtained from incompatible WW3 versions or created with incorrect tools.

```bash
# Check depth file format using the ww3 tools utility
ww3_verify --file regtests/ww3_tp2.4/input/depth.225x106.IDLA1.dat

# Convert files if necessary (for version compatibility)
ww3_convert --input depth.old.dat --output depth.new.dat --format IDLA1

# Regenerate point files from valid template
python scripts/generate_points.py --template template.points.list --output points.list
```

Version mismatches between input files and the WW3 executable can cause subtle errors. Ensure that input files were generated for the same WW3 version being tested. The WW3 project maintains format compatibility within major versions but may introduce changes between releases. Checking version compatibility is important when using input files from different sources.

### Download and Network Issues

Network problems during file downloads can result in incomplete or corrupted input files. Retry failed downloads and verify file integrity through checksum comparison. Proxy settings and firewall configurations may interfere with direct FTP access.

```bash
# Retry download with verbose output
python scripts/download_ww3_input.py --test tp2.4 --verbose --retry 3

# Download using alternative protocol
python scripts/download_ww3_input.py --test tp2.4 --protocol https

# Verify downloaded file integrity
python scripts/download_ww3_input.py --verify --test tp2.4

# Configure proxy if needed
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
python scripts/download_ww3_input.py --test tp2.4
```

Persistent download failures may require manual intervention using web browsers or alternative download tools. Once files are successfully obtained, store them locally to avoid repeated download issues. Consider setting up a local mirror of the WW3 data repository for environments with limited network access.

## Related Documentation

The following resources provide additional information about WW3 regression tests and input file specifications. These external references should be consulted for authoritative documentation on WW3 functionality and test procedures.

**Official WW3 Documentation:**
- WAVEWATCH III User Guide: https://ww3-docs.readthedocs.io/
- WW3 GitHub Repository: https://github.com/NOAA-EMC/WW3
- WW3 Wiki: https://github.com/NOAA-EMC/WW3/wiki
- WW3 Regression Test Guide: https://github.com/NOAA-EMC/WW3/wiki/Regression-Tests

**rompy-ww3 Documentation:**
- rompy-ww3 README: https://github.com/rom-py/rompy-ww3/blob/main/README.md
- rompy Framework Documentation: https://github.com/rom-py/rompy
- Example Configurations: https://github.com/rom-py/rompy-ww3/tree/main/examples

**Related Tools and Resources:**
- WW3-tools Repository: https://github.com/NOAA-EMC/WW3-tools
- WW3 Data Downloads: https://ftp.emc.ncep.noaa.gov/ww3/
- COAWST WW3 Integration: https://code.usgs.gov/coawstmodel/COAWST

## Quick Reference Card

```
╔════════════════════════════════════════════════════════════════════╗
║                    WW3 INPUT FILE QUICK REFERENCE                   ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  DEPTH FILES:   depth.<dims>.<format>.dat                          ║
║  WIND FILES:    wind.<dims>.<format>.dat                           ║
║  CURRENT FILES: current.<dims>.<format>.dat                        ║
║  ICE FILES:     ice.<dims>.<format>.dat                            ║
║  BOUNDARY:      nest.<dims>.<format>.dat                          ║
║  POINTS:        points.list (text file)                            ║
║                                                                    ║
║  STORAGE:       regtests/ww3_tpX.X/input/                          ║
║                                                                    ║
║  DOWNLOAD:      python scripts/download_ww3_input.py --test <name>  ║
║                                                                    ║
║  VERIFY:        ls -lh regtests/ww3_tpX.X/input/                   ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```

This documentation provides comprehensive guidance for obtaining, organizing, and managing WW3 regression test input files. Following these guidelines ensures successful test execution and valid model results. For questions or issues not addressed here, consult the official WW3 documentation or the rompy-ww3 issue tracker.
