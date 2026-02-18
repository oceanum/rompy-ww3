# WW3 mww3_test_04 Regression Test

## Test Description

**Test ID**: mww3_test_04  
**Type**: Multi-grid with static nesting and lateral boundary data  
**Purpose**: Validate propagation with boundary conditions and inner grid with shallow water

**Official Reference**: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/mww3_test_04

## Test Configuration

This test validates multi-grid capabilities with static nesting:

1. **Boundary Grid** (bound):
   - 1-D propagation with preset boundary data at left boundary
   - Dynamic lateral boundaries at top and bottom
   - Spatial: 55×57 rectilinear Cartesian grid
   - Resolution: dx=10km, dy=10km
   - Extent: X=-270:270 km, Y=-280:280 km

2. **Outer Grid** (outer):
   - Full 2-D propagation
   - Constant depth: d=250m
   - Larger extent covering boundary grid

3. **Inner Grid** (inner):
   - Higher resolution nested domain
   - Spatial: 51×51 rectilinear Cartesian grid
   - Resolution: dx=5km, dy=5km
   - Extent: X=-125:125 km, Y=-125:125 km
   - Circular mask with flat bottom

## Key Characteristics

- **Physics**: Propagation only (no source terms)
- **Forcing**: None (FLXn, LN0, ST0, NL0, BT0, DB0, TR0, BS0)
- **Duration**: 12 hours
- **Output Fields**: HS, FP, DP, DIR
- **Output Interval**: 1 hour
- **Grids**: 3 model grids (nrgrd=3)
- **I/O Type**: 1 (unified point output)

## Files

- `rompy_ww3_mww3_test_04.yaml` - YAML configuration
- `rompy_ww3_mww3_test_04.py` - Python configuration script
- `input/` - Input directory (grid and boundary files)

## Running the Test

### Using YAML Configuration (Recommended)

```bash
# Local backend
cd regtests/mww3_test_04
rompy run rompy_ww3_mww3_test_04.yaml --backend-config ../backends/local_backend.yml

# Docker backend
rompy run rompy_ww3_mww3_test_04.yaml --backend-config ../backends/docker_backend.yml
```

### Using Python Script

```bash
cd regtests/mww3_test_04
python rompy_ww3_mww3_test_04.py
```

## Validation

This test validates:
- Static nesting with lateral boundary data from file
- 1-D boundary propagation feeding 2-D inner grids
- Grid coupling between nested domains
- Boundary exchange at lateral boundaries
- Shallow water physics in inner grid

## Notes

- No source terms required (pure propagation test)
- Supports multiple propagation schemes (PR1, PR2, PR3)
- Tests grid masking and boundary conditions
