# WW3 tp2.11 Regression Test

**Test Name:** ww3_tp2.11 - Curvilinear Grid with Full Physics (ST4)

## Overview

This regression test validates WAVEWATCH III's ability to run the full ST4 physics package on a curvilinear grid. It combines the spatial complexity of curvilinear coordinates with complete wave physics simulation.

## Test Configuration

### Grid Setup
- **Grid Type:** CURV (curvilinear)
- **Coordinates:** SPHE (spherical)
- **Grid Dimensions:** 121×121 points
- **Grid Shape:** Quarter annulus (borrowed from ww3_tp2.9)
- **Features:** Includes mask and obstruction files

### Physics Package
- **Source Terms:** ST4 package (full physics enabled with `flsou=True`)
- **Wind Input:** SIN4 (ST4 wind input physics)
- **Nonlinear Interactions:** SNL4 (ST4 nonlinear interactions)
- **Whitecapping:** SDS4 (ST4 whitecapping dissipation)
- **Bottom Friction:** SBT (bottom friction parameterization)

### Forcing
- **Wind:** Homogeneous wind forcing (20 m/s from 270°)
- **Duration:** 1 day (19680606 - 19680607)
- **Output Interval:** 3 hours

### Spectral Configuration
- **Frequencies:** 25 (starting at 0.035 Hz)
- **Directions:** 24 bins
- **Frequency Ratio:** 1.1

### Timesteps
- **dtmax:** 900 seconds (15 minutes)
- **dtxy:** 300 seconds (5 minutes)
- **dtkth:** 450 seconds (7.5 minutes)
- **dtmin:** 10 seconds

## Purpose

This test validates:
1. **Curvilinear Grid Handling:** Proper handling of non-regular grid structures
2. **Full Physics Integration:** Complete ST4 physics package on curvilinear grids
3. **Wind-Driven Generation:** Wave generation from homogeneous wind forcing
4. **Obstruction Physics:** Interaction with grid obstructions and masks

## Data Sources

Grid data files are shared with ww3_tp2.9:
- `curv_2d.lon` - Longitude coordinates
- `curv_2d.lat` - Latitude coordinates
- `curv_2d.bot` - Bathymetry
- `curv_2d.mask` - Land/water mask
- `curv_2d.obs` - Obstruction data

## Running the Test

### Generate Configuration
```bash
cd regtests/ww3_tp2.11
python rompy_ww3_tp2_11.py
```

### Expected Output
- `ww3_grid.nml` - Grid preprocessing configuration
- `ww3_shel.nml` - Shell component configuration
- `namelists.nml` - Physics parameters (ST4 package)
- `ww3_ounf.nml` - Field output configuration

### Output Fields
- `HS` - Significant wave height
- `T01` - Mean period (m₁/m₀)
- `FP` - Peak frequency
- `DIR` - Mean wave direction
- `SPR` - Directional spreading
- `WND` - Wind speed

## Test Hierarchy

This test combines patterns from:
- **ww3_tp2.9:** Curvilinear grid setup with obstructions
- **ww3_tp2.6:** Full physics package configuration (ST4)

## Notes

- This test demonstrates the flexibility of rompy-ww3's component-based architecture
- The combination of CURV grid + full physics represents realistic operational scenarios
- Homogeneous wind forcing provides controlled test conditions for physics validation
