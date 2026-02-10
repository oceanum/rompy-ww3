# WW3 tp2.12 Regression Test

**Test Name:** ww3_tp2.12 - Global 30-minute Grid with Simple Closure

## Overview

This regression test validates WAVEWATCH III's ability to run on a global 30-minute resolution grid with simple periodic closure. It represents a realistic operational configuration commonly used for global wave forecasting systems.

## Test Configuration

### Grid Setup
- **Grid Type:** RECT (rectilinear)
- **Coordinates:** SPHE (spherical)
- **Closure:** SMPL (simple periodic closure at i=NX+1)
- **Grid Dimensions:** 720×311 points (0.5° resolution)
- **Grid Coverage:** Global (latitude: -77.5° to 77.5°)
- **Features:** Global mask and obstruction files

### Physics Package
- **Source Terms:** ST4 package (Ardhuin et al. 2010)
- **Wind Input:** SIN4 with BETAMAX=1.33 and TAUWSHELTER=1.2
- **Sea Ice:** CICE0=0.25, CICEN=0.75

### Forcing
- **Wind:** GFS 30-minute wind forcing (test assumes homogeneous input)
- **Duration:** TBD (based on reference test)
- **Output Interval:** TBD

### Spectral Configuration
- **Frequencies:** 50 (starting at 0.035 Hz)
- **Directions:** 36 bins
- **Frequency Ratio:** 1.07
- **Direction Offset:** 0.5°

### Timesteps
- **dtmax:** 3600 seconds (1 hour)
- **dtxy:** 480 seconds (8 minutes)
- **dtkth:** 1800 seconds (30 minutes)
- **dtmin:** 30 seconds

## Purpose

This test validates:
1. **Global Grid Handling:** Proper handling of global spherical grids with periodic closure
2. **Simple Closure:** Grid wraps at i=NX+1 (longitude wrapping)
3. **Realistic Resolution:** 30-minute (0.5°) operational grid resolution
4. **Complex Bathymetry:** Global bathymetry with realistic coastal features
5. **Obstruction Physics:** Interaction with sub-grid-scale obstructions

## Data Sources

Grid data files (from NOAA-EMC/WW3):
- `glo_30m.bot` - Global bathymetry (1.75 MB)
- `glo_30m.mask` - Land/water mask (672 KB)
- `glo_30m.obst` - Sub-grid obstructions (1.35 MB)
- `namelists_Global.nml` - ST4 physics parameters

## Running the Test

### Generate Configuration
```bash
cd regtests/ww3_tp2.12
python rompy_ww3_tp2_12.py
```

### Expected Output
- `ww3_grid.nml` - Grid preprocessing configuration
- `ww3_shel.nml` - Shell component configuration (if running full model)
- `namelists.nml` - Physics parameters (ST4 package)

### Grid Characteristics
- **Total Points:** 223,920 (720×311)
- **Longitude Range:** 0° to 360° (wraps with SMPL closure)
- **Latitude Range:** -77.5° to 77.5° (311 points at 0.5° spacing)
- **Resolution:** 0.5° (~55 km at equator)

## Closure Type: SMPL vs TRPL

**Why SMPL (Simple) instead of TRPL (Tripole)?**

This test uses **SMPL closure**, not TRPL (tripole), because:

1. **Standard Global Grid:** This is a standard latitude-longitude grid extending from -77.5° to +77.5°
2. **No Arctic Singularity:** The grid does not extend to the North Pole, so no tripole fold is needed
3. **Periodic in Longitude:** Only east-west periodicity required: (NX+1,J) => (1,J)

**When to use TRPL:**
- Grids extending to the Arctic that include the North Pole
- Requires curvilinear grid to handle the pole singularity
- NX must be even for tripole fold at j=NY+1

**When to use SMPL:**
- Standard lat-lon grids that don't reach the poles
- Any grid requiring only longitude periodicity
- Works with RECT or CURV grids

## Test Hierarchy

This test represents:
- **Grid Type:** Global operational configuration
- **Resolution:** Coarse (30-minute) suitable for global forecasts
- **Physics:** Full ST4 package with realistic parameterizations

## Notes

- This test demonstrates rompy-ww3's ability to handle realistic operational grid configurations
- The 0.5° resolution is typical for global wave forecasting systems
- Obstruction file provides sub-grid-scale coastal features
- Simple closure is appropriate for grids that don't extend to the poles
- Configuration follows NOAA-EMC/WW3 reference test ww3_tp2.12
