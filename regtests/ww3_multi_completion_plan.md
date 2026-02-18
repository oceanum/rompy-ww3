# ww3_multi Completion Plan

## Executive Summary

**Status: COMPLETE** ✓

The `ww3_multi` component is fully implemented and ready for multi-grid (mww3) regression tests. All core functionality is in place with a working example demonstrating multi-grid configuration patterns.

---

## 1. Component Status

### 1.1 Implementation Complete

The `ww3_multi` component located at `src/rompy_ww3/components/multi.py` provides complete support for:

- **DOMAIN_NML**: Multi-grid model parameters including start/stop times, I/O settings, and multi-grid specific parameters (nrinp, nrgrd)
- **INPUT_GRID_NML**: Input grid specification for multi-grid models with forcing parameters
- **MODEL_GRID_NML**: Model grid specifications with resource allocation (rank_id, group_id, comm_frac)
- **OUTPUT_TYPE_NML**: Output configuration for field lists, point outputs, and track formats
- **OUTPUT_DATE_NML**: Output timing for fields, points, and restarts
- **HOMOG_COUNT_NML**: Homogeneous input count configuration

### 1.2 Verification

| Feature | Status | Evidence |
|---------|--------|----------|
| Multi-grid configuration | ✓ Working | `examples/multi_grid_example.py` runs successfully |
| Namelist generation | ✓ Correct | `render()` method produces valid ww3_multi.nml format |
| Multiple model grids | ✓ Supported | `model_grids: List[ModelGrid]` field |
| Input grid handling | ✓ Supported | `input_grid: InputGrid` field |
| Output configuration | ✓ Complete | Full OUTPUT_TYPE_NML and OUTPUT_DATE_NML support |
| Index formatting | ✓ Correct | MODEL(1)%, INPUT(1)% indexed format generated |

---

## 2. What's Implemented

### 2.1 Core Component (`multi.py`)

```python
class Multi(WW3ComponentBaseModel):
    """Component for ww3_multi.nml containing multi-grid configuration."""
    
    domain: Optional[Domain]           # DOMAIN_NML
    input_grid: Optional[InputGrid]    # INPUT_GRID_NML
    model_grid: Optional[ModelGrid]     # Single MODEL_GRID_NML
    model_grids: Optional[List[ModelGrid]]  # Multiple MODEL_GRID_NML
    output_type: Optional[OutputType]   # OUTPUT_TYPE_NML
    output_date: Optional[OutputDate]   # OUTPUT_DATE_NML
    homog_count: Optional[HomogCount]  # HOMOG_COUNT_NML
```

### 2.2 Rendering Pipeline

The `render()` method produces correctly formatted namelist content:

1. DOMAIN_NML - Multi-grid model parameters
2. INPUT_GRID_NML - Input grid specification
3. MODEL_GRID_NML - Model grid specifications (indexed format)
4. OUTPUT_TYPE_NML - Multi-grid output types
5. OUTPUT_DATE_NML - Multi-grid output dates
6. HOMOG_COUNT_NML - Multi-grid homogeneous input counts

### 2.3 Index Field Conversion

The component correctly converts MODEL% fields to MODEL(N)% indexed format for multi-grid compatibility:

```fortran
! Generated output example:
&MODEL_GRID_NML
  MODEL(1)%NAME = 'region1'
  MODEL(1)%PROP = 1
  MODEL(1)%RNK = 0
  MODEL(1)%GRP = 0
  MODEL(1)%CFRACSTART = 0.0
  MODEL(1)%CFRACEND = 1.0
/
```

---

## 3. Usage Patterns for mww3 Tests

### 3.1 Basic Multi-Grid Configuration

```python
from rompy_ww3.components import Multi
from rompy_ww3.namelists import Domain, InputGrid, ModelGrid

multi = Multi(
    domain=Domain(
        start="20230101 000000",
        stop="20230102 000000",
        iostyp=1,
        ngrd=2,     # 2 model grids
        nrinp=1,    # 1 input grid
    ),
    input_grid=InputGrid(
        name="global",
        forcing={"winds": "T"}
    ),
    model_grids=[
        ModelGrid(
            name="region1",
            forcing={"winds": "T"},
            resource={
                "rank_id": 0,
                "group_id": 0,
                "comm_frac_start": 0.0,
                "comm_frac_end": 1.0,
            }
        ),
        ModelGrid(
            name="region2",
            forcing={"winds": "T"},
            resource={
                "rank_id": 1,
                "group_id": 0,
                "comm_frac_start": 0.0,
                "comm_frac_end": 1.0,
            }
        ),
    ],
    output_type=OutputType(field={"list": "HSIGN TMM10"}),
    output_date=OutputDate(
        field={"start": "20230101 000000", "stride": "3600"}
    ),
)
```

### 3.2 Full Integration with Config

The `Config` class integrates with Multi component for complete WW3 configuration:

```python
from rompy_ww3.config import Config

config = Config(
    domain=domain,
    input_grid=input_grid,
    model_grid=model_grid1,
    model_grids=[model_grid1, model_grid2],
    output_type=output_type,
    output_date=output_date,
    spectrum=spectrum,
    run=run,
    timesteps=timesteps,
    grids=[grid1, grid2],
)
```

See `examples/multi_grid_example.py` for complete working example.

---

## 4. Minor Gaps (Enhancements, Not Blockers)

### 4.1 Unit Tests

**Status**: Not implemented
**Impact**: None (functionality verified via example)
**Effort**: 2-3 hours

Recommended additions:
- `tests/test_component_multi.py`: Multi component-specific tests
- Test rendering with multiple model grids
- Test index formatting correctness

### 4.2 Enhanced Validation

**Status**: Basic validation exists
**Impact**: None
**Effort**: 1-2 hours

Could add:
- Cross-grid consistency checks (matching dimensions, compatible resolutions)
- Communication fraction validation (0.0 <= start < end <= 1.0)

### 4.3 Documentation

**Status**: Inline docstrings present
**Impact**: None
**Effort**: 1 hour

Could enhance:
- API documentation in docs/
- Multi-grid usage tutorial
- Example variations (different grid counts, coupling patterns)

---

## 5. Completion Checklist

### 5.1 Core Implementation

| Item | Status | Notes |
|------|--------|-------|
| Multi component class | ✓ | `src/rompy_ww3/components/multi.py` |
| render() method | ✓ | Produces valid ww3_multi.nml |
| write_nml() support | ✓ | Inherited from WW3ComponentBaseModel |
| run_cmd support | ✓ | Inherited from WW3ComponentBaseModel |

### 5.2 Namelist Coverage

| Namelist | Status | Notes |
|----------|--------|-------|
| DOMAIN_NML | ✓ | Full multi-grid parameters |
| INPUT_GRID_NML | ✓ | Input grid specification |
| MODEL_GRID_NML | ✓ | Model grid with indexed fields |
| OUTPUT_TYPE_NML | ✓ | Field, point, track outputs |
| OUTPUT_DATE_NML | ✓ | Timing for all outputs |
| HOMOG_COUNT_NML | ✓ | Homogeneous input counts |

### 5.3 Testing & Examples

| Item | Status | Location |
|------|--------|----------|
| Working example | ✓ | `examples/multi_grid_example.py` |
| Integration test | ⚠ | Limited (example serves as integration test) |
| Unit tests | ❌ | Not implemented |
| Docker backend test | ⚠ | Requires ww3_multi Docker image |

### 5.4 mww3 Test Readiness

| Requirement | Status | Notes |
|------------|--------|-------|
| Multi-grid config generation | ✓ | All namelists supported |
| Multiple grids | ✓ | 2+ grids supported |
| Grid coupling | ✓ | Via Domain parameters |
| Input grid handling | ✓ | INPUT_GRID_NML |
| Output aggregation | ✓ | OUTPUT_TYPE_NML + OUTPUT_DATE_NML |

**Overall mww3 Readiness: READY** ✓

---

## 6. Recommendations for mww3 Tests

### 6.1 Test Priority

Based on ww3_multi capability, mww3 tests can proceed in this order:

1. **mww3_test_01**: Basic two-grid configuration
   - 1 input grid, 2 model grids
   - Simple boundary exchange
   - Basic input/output

2. **mww3_test_02**: Three-grid configuration
   - 1 input grid, 3 model grids
   - Regional nesting pattern
   - Multiple output types

3. **mww3_test_03**: Advanced multi-grid
   - 3+ grids with coupling
   - Complex boundary conditions
   - Full physics configuration

### 6.2 Prerequisites for mww3 Tests

| Prerequisite | Status | Action |
|--------------|--------|--------|
| ww3_multi component | ✓ Ready | No action needed |
| ww3_multi Docker image | ❌ | May need Docker image with ww3_multi binary |
| Multi-grid input data | ❌ | Download from NOAA-EMC/WW3 |
| Test configurations | ❌ | Create per Task 4.3-4.5 |

### 6.3 Data Requirements

Multi-grid tests require:
- Depth files for each grid
- Wind/current forcing files (if enabled)
- Nest boundary files for grid coupling
- Points file for point output (if enabled)

Download from: `https://github.com/NOAA-EMC/WW3/tree/develop/regtests/mww3_test_xx/input/`

---

## 7. Summary

### 7.1 Conclusion

**ww3_multi is complete and ready for mww3 regression tests.**

- All core namelist components implemented
- Working example demonstrates multi-grid patterns
- No blockers for mww3 test implementation
- Minor gaps are enhancements, not requirements

### 7.2 Next Steps

1. **Immediate**: Proceed with mww3_test_01 configuration (Task 4.3)
2. **Parallel**: Ensure ww3_multi Docker image is available
3. **Follow-up**: Download multi-grid input data from NOAA-EMC/WW3

### 7.3 Contact

For questions about ww3_multi implementation:
- Review: `src/rompy_ww3/components/multi.py`
- Example: `examples/multi_grid_example.py`
- Namelists: `src/rompy_ww3/namelists/`

---

*Document generated: 2026-02-11*
*Task: 4.2 - ww3_multi Completion Plan*
*Status: CONFIRMED COMPLETE*
