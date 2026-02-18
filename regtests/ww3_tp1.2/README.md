# WW3 tp1.2 Regression Test

## Test Description

**Test ID**: ww3_tp1.2  
**Type**: 1-D propagation on spherical grid along meridian  
**Source Terms**: None (pure propagation)  
**Purpose**: Validates pure wave propagation physics along a meridian (N-S direction)

**Official Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.2

## Key Characteristics

- **Grid**: 3×123 rectilinear spherical grid (narrow in longitude, extended in latitude)
- **Extent**: -1° to 1° longitude, -61° to 61° latitude
- **Resolution**: 1 degree × 1 degree
- **Propagation**: Meridional only (flcy=T, flcx=F)
- **Closure**: NONE (no periodic boundary)
- **Duration**: 6 days
- **Output Interval**: 12 hours

## Difference from tp1.1

| Parameter | tp1.1 (Equatorial) | tp1.2 (Meridional) |
|-----------|-------------------|-------------------|
| Grid (nx×ny) | 360×3 | 3×123 |
| Longitude extent | -180° to 180° | -1° to 1° |
| Latitude extent | -1° to 2° | -61° to 61° |
| Propagation direction | X (zonal) | Y (meridional) |
| Closure | SMPL | NONE |
| Duration | 24 days | 6 days |
| Output interval | 24 hours | 12 hours |

## Files

- `rompy_ww3_tp1_2.yaml` - YAML configuration
- `rompy_ww3_tp1_2.py` - Python configuration
- `input/` - Downloaded input files (16 files)

## Running the Test

### Download Input Files

```bash
python regtests/download_input_data.py tp1.2
```

### Generate Configuration

```bash
cd regtests/ww3_tp1.2
python rompy_ww3_tp1_2.py
```

### Run with WW3 (requires WW3 installation)

```bash
# Use appropriate backend (local or Docker)
# Configuration files generated in rompy_runs/ww3_tp1_2_regression/
```

## Physics Tested

This test validates:
- Meridional propagation physics (N-S direction)
- Spherical geometry handling in latitude direction
- Grid metric terms in spherical coordinates
- Pure advection without source/sink terms

Together with tp1.1, this test validates 1-D propagation in both principal directions (E-W and N-S) on a sphere.
