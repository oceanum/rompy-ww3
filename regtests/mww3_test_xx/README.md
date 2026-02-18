# WW3 Multi-Grid Test Series Documentation

## Overview

The WW3 mww3_test_xx test series constitutes the multi-grid validation suite for WAVEWATCH III (WW3), systematically validating the coupled multi-grid capabilities that enable nested model configurations with hierarchical resolution. This comprehensive collection of three regression tests progressively validates multi-grid functionality from basic two-grid coupling through advanced configurations with differential forcing and complex resource allocation.

Multi-grid modeling represents a fundamental capability for operational wave forecasting, where regional high-resolution simulations must be forced by larger-scale lower-resolution models while maintaining two-way communication for consistent wave physics. The mww3_test_xx series establishes confidence in WW3's multi-grid implementation by exercising grid coupling, boundary exchange, resource allocation, and differential forcing across increasingly complex scenarios.

The rompy-ww3 plugin provides complete configuration support for all multi-grid tests through its dedicated Multi component, which generates the ww3_multi.nml file that controls multi-grid execution. Unlike single-grid tests that use the Shel component, multi-grid configurations require the specialized Multi component to handle MODEL(n)% indexing, per-grid resource allocation, and differential forcing configurations.

### Multi-Grid Architecture

WAVEWATCH III supports multi-grid configurations where multiple computational grids operate simultaneously with boundary communication. This architecture enables nested modeling where a coarse-resolution parent grid provides boundary conditions to higher-resolution child grids. The key components of multi-grid architecture include:

**Grid Hierarchy**: Multiple grids organized in parent-child relationships where boundary information flows from parent to child. In WW3, this relationship is implicit in grid numbering and boundary file assignments rather than explicit parent-child declarations. Grid 1 typically serves as the outermost domain, with subsequent grids nested within.

**MPI Parallelization**: Each grid operates on its own MPI rank with dedicated computational resources. The communication fraction parameters (comm_frac_start and comm_frac_end) allocate available processor resources across grids, enabling load balancing based on grid computational demands.

**Boundary Exchange**: Grids communicate through boundary conditions, where inner grids receive forcing from outer grids. The nrinp parameter specifies the number of input grids providing boundary conditions, while model grids receive and process these inputs according to their forcing configurations.

**Differential Forcing**: Different grids can enable different forcing types based on their domain characteristics. A coastal fine-resolution grid might require water level forcing while an offshore coarse grid does not. This selective activation reduces computational cost while ensuring all grids have appropriate forcing.

### Test Series Objectives

The mww3_test_xx series accomplishes several critical objectives for WW3 multi-grid validation. First, it verifies correct multi-grid namelist generation including MODEL(n)% structure and per-grid parameterization. Second, it validates MPI resource allocation and load balancing across multiple grids. Third, it exercises boundary exchange and coupling between nested grids. Fourth, it demonstrates differential forcing configurations where grids have independent forcing selections. Finally, it provides reference configurations that enable developers to implement new multi-grid scenarios.

Each test builds upon previous tests, introducing additional complexity and capabilities. This progressive approach ensures that fundamental multi-grid functionality works before testing advanced features, simplifying debugging when issues arise.

## Test Matrix

The following matrix provides a consolidated overview of all three multi-grid tests, including their configuration complexity, grid hierarchy, resource allocation, and feature coverage.

### Quick Reference Table

| Feature | mww3_test_01 | mww3_test_02 | mww3_test_03 |
|---------|--------------|--------------|--------------|
| Number of grids | 2 | 3 | 3 |
| Grid hierarchy | 2-level | 3-level | 3-level |
| MPI ranks | 2 | 3 | 3 |
| Simulation duration | 1 day | 1 day | 1.5 days |
| Output frequency | 3600s (hourly) | 1800s (30 min) | 900s (15 min) |
| Output fields | 4 | 7 | 20+ |
| Resource split | 50/50 | 33/33/34 | 30/35/35 |
| Differential forcing | No | No | Yes |
| Water levels | No | No | Fine grid only |
| Currents | No | No | All grids |
| Complexity level | Basic | Intermediate | Advanced |

### Grid Configuration Summary

| Test | Grid 1 | Grid 2 | Grid 3 |
|------|--------|--------|--------|
| mww3_test_01 | coarse (50%) | fine (50%) | — |
| mww3_test_02 | coarse (33%) | medium (34%) | fine (33%) |
| mww3_test_03 | coarse (30%) | medium (35%) | fine (35%) |

### Forcing Configuration Comparison

| Test | Grid 1 | Grid 2 | Grid 3 |
|------|--------|--------|--------|
| mww3_test_01 | winds only | winds only | — |
| mww3_test_02 | winds only | winds only | winds only |
| mww3_test_03 | winds + currents | winds + currents | winds + currents + water levels |

### Output Variables by Test

| Variable | Description | mww3_test_01 | mww3_test_02 | mww3_test_03 |
|----------|-------------|--------------|--------------|--------------|
| HS | Significant wave height | ✓ | ✓ | ✓ |
| FP | Peak frequency | ✓ | ✓ | ✓ |
| DP | Peak direction | ✓ | ✓ | ✓ |
| DIR | Mean direction | ✓ | ✓ | ✓ |
| SPR | Directional spreading | — | ✓ | ✓ |
| WND | Wind speed/direction | — | ✓ | ✓ |
| CUR | Current speed/direction | — | ✓ | ✓ |
| WCC | Wave component (cumulative) | — | — | ✓ |
| WCF | Wave component (frequency) | — | — | ✓ |
| WCH | Wave component (high) | — | — | ✓ |
| WCM | Wave component (mean) | — | — | ✓ |
| T02 | Mean period (second moment) | — | — | ✓ |
| T01 | Mean period (first moment) | — | — | ✓ |
| T0M1 | Inverse mean period | — | — | ✓ |
| FP0 | Peak frequency (alternative) | — | — | ✓ |
| THP0 | Peak direction (alternative) | — | — | ✓ |
| THS | Significant wave height direction | — | — | ✓ |
| EF | Mean frequency | — | — | ✓ |
| TH1M | First directional moment | — | — | ✓ |
| TH2M | Second directional moment | — | — | ✓ |

## Test Details

### mww3_test_01: Basic Two-Grid Configuration

**Location:** `regtests/mww3_test_01/`  
**Reference:** [NOAA-EMC/WW3 mww3_test_01](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/mww3_test_01)  
**Duration:** 1 day  
**Complexity:** Basic

The mww3_test_01 test establishes the foundation for multi-grid WW3 modeling by validating the fundamental two-grid configuration. This test demonstrates the essential elements of multi-grid modeling including proper MODEL(n)% indexing, basic MPI resource allocation, and the core coupling between nested grids.

The configuration consists of two model grids: a coarse outer domain covering the largest spatial extent at lower resolution, and a fine nested domain providing higher resolution for a smaller area of interest. Both grids use identical spectral configurations and forcing selections, isolating the multi-grid coupling from differential physics effects.

The coarse grid occupies MPI ranks 1 with communication fraction 0.00-0.50, receiving 50% of available computational resources. The fine grid occupies MPI rank 2 with communication fraction 0.50-1.00, receiving the remaining 50%. This equal distribution assumes similar computational demands per timestep, which holds when grid resolutions are comparable and forcing configurations match.

Forcing configuration keeps both grids identical with winds enabled and all other forcing types (water levels, currents, ice) disabled. This simplification focuses validation on grid coupling rather than complex forcing interactions. Output configuration generates four standard variables (HS, FP, DP, DIR) at hourly intervals, providing sufficient temporal resolution to observe wave evolution while minimizing I/O overhead.

Key parameters for mww3_test_01 include domain.nrgrd=2 specifying two model grids, domain.nrinp=1 specifying one input grid (minimum required), and output stride of 3600 seconds for hourly output. The output type list="HS FP DP DIR" specifies the four output variables.

Validation criteria for mww3_test_01 focus on correct multi-grid namelist generation with proper MODEL(1)% and MODEL(2)% structure, successful MPI resource allocation across two ranks, proper boundary communication between grids, and output file generation for both grids.

### mww3_test_02: Three-Grid Hierarchy

**Location:** `regtests/mww3_test_02/`  
**Reference:** [NOAA-EMC/WW3 mww3_test_02](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/mww3_test_02)  
**Duration:** 1 day  
**Complexity:** Intermediate

The mww3_test_02 test extends multi-grid validation to three coupled grids, establishing confidence in hierarchical nesting with intermediate resolution domains. This test validates that the multi-grid system scales correctly to additional grids and exercises boundary exchange between all three nesting levels.

The configuration consists of three model grids: a coarse outer domain, a medium-resolution intermediate domain, and a fine inner domain. The three-grid hierarchy enables testing of multi-level coupling where the coarse grid provides boundaries for the medium grid, which in turn provides boundaries for the fine grid. This cascading relationship represents the typical structure of operational nested wave modeling.

Resource allocation distributes available computational resources equally across three grids with approximately 33% per grid. Grid 1 (coarse) receives MPI rank 1 with communication fraction 0.00-0.33. Grid 2 (medium) receives MPI rank 2 with communication fraction 0.33-0.67. Grid 3 (fine) receives MPI rank 3 with communication fraction 0.67-1.00. The slight variation (33%, 34%, 33%) ensures the fractions sum exactly to 1.0.

Forcing configuration maintains simplicity with wind forcing enabled on all three grids and all other forcing types disabled. This consistency ensures that any differences between grids reflect grid hierarchy rather than forcing differences. Output configuration expands to seven variables including directional spreading (SPR), wind (WND), and current (CUR) variables, testing additional output field types.

Output frequency increases to 30-minute intervals (stride=1800 seconds), doubling the temporal resolution compared to mww3_test_01. This higher frequency tests the I/O system's capability to handle more frequent output across multiple grids simultaneously.

Key parameters include domain.nrgrd=3 for three model grids, output stride of 1800 seconds, and output type list expanded to "HS FP DP DIR SPR WND CUR".

Validation criteria extend those of mww3_test_01 to include three-grid coupling, balanced resource allocation across three ranks, more frequent output generation, and extended output variable capture.

### mww3_test_03: Advanced Multi-Grid Configuration

**Location:** `regtests/mww3_test_03/`  
**Reference:** [NOAA-EMC/WW3 mww3_test_03](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/mww3_test_03)  
**Duration:** 1.5 days (36 hours)  
**Complexity:** Advanced

The mww3_test_03 test represents the most comprehensive multi-grid validation, exercising advanced capabilities including differential forcing, non-uniform resource allocation, and extensive output configurations. This test demonstrates WW3's full multi-grid flexibility and validates configurations suitable for production operational forecasting.

The configuration maintains three model grids (coarse, medium, fine) but introduces differential forcing where different grids have different forcing configurations. The coarse and medium grids enable winds and currents but not water levels, while the fine grid enables all three forcing types (winds, currents, water levels). This selective activation reflects realistic scenarios where water level forcing is only necessary near coastlines where fine grids typically operate.

Resource allocation shifts from equal distribution to workload-optimized allocation. The coarse grid receives 30% of resources (less computational work per timestep), while medium and fine grids each receive 35%. This non-uniform allocation reflects typical load balancing where finer-resolution grids require more computational effort per timestep due to smaller timesteps required by CFL constraints.

Output configuration expands dramatically to over 20 variables including wave components (WCC, WCF, WCH, WCM), multiple mean period definitions (T02, T01, T0M1), peak parameters (FP0, THP0, THS), and spectral moments (EF, TH1M, TH2M). This comprehensive output tests the full range of WW3 field output capabilities.

Output frequency increases to 15-minute intervals (stride=900 seconds), providing high temporal resolution for detailed wave evolution analysis. The simulation duration extends to 36 hours (1.5 days), testing model stability over extended periods.

Key parameters include domain.nrgrd=3, output stride of 900 seconds, output type list containing 20+ variables, simulation stop at "20200102 120000" for 36-hour duration, and per-grid forcing configurations with water levels enabled only on grid 3.

Validation criteria include all previous criteria plus verification of differential forcing implementation, non-uniform resource allocation (30%/35%/35% summing to 100%), comprehensive output capture across all variable types, and stable operation over the extended 36-hour simulation.

## Multi Component Usage

### Component Architecture

The rompy-ww3 Multi component provides specialized handling for multi-grid WW3 configurations. Unlike single-grid configurations that use the Shel component, multi-grid configurations require the Multi component to generate the ww3_multi.nml file that controls multi-grid execution.

The Multi component inherits from WW3ComponentBaseModel and provides the following key capabilities:

**Domain Configuration**: The Domain namelist within Multi specifies nrinp (number of input grids) and nrgrd (number of model grids). The nrinp parameter must be at least 1 even when all grids are model grids, as WW3 requires at least one input source.

**Model Grid Management**: The model_grids parameter accepts a list of ModelGrid objects, each specifying per-grid configuration including forcing, resource allocation, and grid-specific parameters. The order in this list determines MODEL(n)% indexing.

**Output Configuration**: The Multi component supports both output_type and output_date parameters for specifying output variables and timing. These apply across all grids by default but can be customized per grid through more advanced configurations.

### Basic Multi Component Configuration

```python
from rompy_ww3.components import Multi
from rompy_ww3.namelists import Domain, Spectrum, Run, Timesteps
from rompy_ww3.namelists.input import ModelGrid, ModelGridForcing, ModelGridResource
from rompy_ww3.namelists.output_date import OutputDate, OutputDateField
from rompy_ww3.namelists.output_type import OutputType, OutputTypeField

# Domain configuration for multi-grid run
domain = Domain(
    start="20200101 000000",
    stop="20200102 000000",
    iostyp=1,
    nrinp=1,  # Minimum 1 input grid required
    nrgrd=2,  # Two model grids
)

# First model grid configuration
model_grid1 = ModelGrid(
    name="coarse",
    forcing=ModelGridForcing(
        water_levels="no",
        currents="no",
        winds="T",
        ice_conc="no",
        air_density="no",
        atm_momentum="no",
    ),
    resource=ModelGridResource(
        rank_id=1,
        group_id=1,
        comm_frac_start=0.00,
        comm_frac_end=0.50,
    ),
)

# Second model grid configuration
model_grid2 = ModelGrid(
    name="fine",
    forcing=ModelGridForcing(
        water_levels="no",
        currents="no",
        winds="T",
        ice_conc="no",
        air_density="no",
        atm_momentum="no",
    ),
    resource=ModelGridResource(
        rank_id=2,
        group_id=1,
        comm_frac_start=0.50,
        comm_frac_end=1.00,
    ),
)

# Output configuration
output_type = OutputType(
    field=OutputTypeField(list="HS FP DP DIR"),
)

output_date = OutputDate(
    field=OutputDateField(
        start="20200101 000000",
        stride="3600",
        stop="20200102 000000",
    ),
)

# Create Multi component
multi_component = Multi(
    domain=domain,
    model_grids=[model_grid1, model_grid2],
    output_type=output_type,
    output_date=output_date,
)
```

### Differential Forcing Configuration

Differential forcing enables different grids to have different forcing configurations, reducing computational cost where forcing types are unnecessary:

```python
# Grid 1: Coarse grid (no water levels needed offshore)
model_grid1 = ModelGrid(
    name="coarse",
    forcing=ModelGridForcing(
        water_levels="no",
        currents="T",
        winds="T",
        ice_conc="no",
        air_density="no",
        atm_momentum="no",
    ),
    resource=ModelGridResource(
        rank_id=1,
        group_id=1,
        comm_frac_start=0.00,
        comm_frac_end=0.30,
    ),
)

# Grid 2: Medium grid
model_grid2 = ModelGrid(
    name="medium",
    forcing=ModelGridForcing(
        water_levels="no",
        currents="T",
        winds="T",
        ice_conc="no",
        air_density="no",
        atm_momentum="no",
    ),
    resource=ModelGridResource(
        rank_id=2,
        group_id=1,
        comm_frac_start=0.30,
        comm_frac_end=0.65,
    ),
)

# Grid 3: Fine grid (water levels needed near coast)
model_grid3 = ModelGrid(
    name="fine",
    forcing=ModelGridForcing(
        water_levels="T",  # Enabled for coastal grid
        currents="T",
        winds="T",
        ice_conc="no",
        air_density="no",
        atm_momentum="no",
    ),
    resource=ModelGridResource(
        rank_id=3,
        group_id=1,
        comm_frac_start=0.65,
        comm_frac_end=1.00,
    ),
)
```

### Resource Allocation Configuration

Resource allocation must sum to exactly 1.0 across all grids:

```python
# Uniform allocation for equal computational demand
model_grid1 = ModelGrid(
    name="coarse",
    resource=ModelGridResource(
        rank_id=1,
        group_id=1,
        comm_frac_start=0.00,
        comm_frac_end=0.33,  # 33%
    ),
)

model_grid2 = ModelGrid(
    name="medium",
    resource=ModelGridResource(
        rank_id=2,
        group_id=1,
        comm_frac_start=0.33,
        comm_frac_end=0.67,  # 34%
    ),
)

model_grid3 = ModelGrid(
    name="fine",
    resource=ModelGridResource(
        rank_id=3,
        group_id=1,
        comm_frac_start=0.67,
        comm_frac_end=1.00,  # 33%
    ),
)

# Non-uniform allocation for workload optimization
model_grid1 = ModelGrid(
    name="coarse",
    resource=ModelGridResource(
        rank_id=1,
        group_id=1,
        comm_frac_start=0.00,
        comm_frac_end=0.30,  # 30% - less work
    ),
)

model_grid2 = ModelGrid(
    name="medium",
    resource=ModelGridResource(
        rank_id=2,
        group_id=1,
        comm_frac_start=0.30,
        comm_frac_end=0.65,  # 35%
    ),
)

model_grid3 = ModelGrid(
    name="fine",
    resource=ModelGridResource(
        rank_id=3,
        group_id=1,
        comm_frac_start=0.65,
        comm_frac_end=1.00,  # 35% - more work
    ),
)
```

### Complete Configuration with NMLConfig

```python
from rompy.model import ModelRun
from rompy.core.time import TimeRange
from rompy_ww3.config import NMLConfig

# Create Multi component
multi_component = create_ww3_mww3_test_01_component()

# Wrap in NMLConfig
config = NMLConfig(multi_component=multi_component)

# Create model run
period = TimeRange(start="2020-01-01T00:00:00", duration="1D", interval="1H")

model_run = ModelRun(
    run_id="ww3_mww3_test_01_regression",
    config=config,
    period=period,
    output_dir="rompy_runs",
)

# Generate namelists
model_run.generate()
```

## Grid Configuration Examples

### Two-Grid Configuration Pattern

The following pattern demonstrates the fundamental two-grid configuration used in mww3_test_01:

```python
# Domain with 2 model grids
domain = Domain(
    start="20200101 000000",
    stop="20200102 000000",
    iostyp=1,
    nrinp=1,
    nrgrd=2,
)

# Equal resource split
model_grid1 = ModelGrid(
    name="outer",
    forcing=ModelGridForcing(winds="T", water_levels="no", currents="no"),
    resource=ModelGridResource(rank_id=1, group_id=1, comm_frac_start=0.0, comm_frac_end=0.5),
)

model_grid2 = ModelGrid(
    name="inner",
    forcing=ModelGridForcing(winds="T", water_levels="no", currents="no"),
    resource=ModelGridResource(rank_id=2, group_id=1, comm_frac_start=0.5, comm_frac_end=1.0),
)

multi_component = Multi(
    domain=domain,
    model_grids=[model_grid1, model_grid2],
)
```

### Three-Grid Hierarchy Pattern

The following pattern demonstrates the three-grid hierarchy used in mww3_test_02 and mww3_test_03:

```python
# Domain with 3 model grids
domain = Domain(
    start="20200101 000000",
    stop="20200102 000000",
    iostyp=1,
    nrinp=1,
    nrgrd=3,
)

# Cascading resource allocation
model_grid1 = ModelGrid(
    name="coarse",
    forcing=ModelGridForcing(winds="T", currents="T", water_levels="no"),
    resource=ModelGridResource(rank_id=1, group_id=1, comm_frac_start=0.0, comm_frac_end=0.33),
)

model_grid2 = ModelGrid(
    name="medium",
    forcing=ModelGridForcing(winds="T", currents="T", water_levels="no"),
    resource=ModelGridResource(rank_id=2, group_id=1, comm_frac_start=0.33, comm_frac_end=0.67),
)

model_grid3 = ModelGrid(
    name="fine",
    forcing=ModelGridForcing(winds="T", currents="T", water_levels="T"),
    resource=ModelGridResource(rank_id=3, group_id=1, comm_frac_start=0.67, comm_frac_end=1.0),
)

multi_component = Multi(
    domain=domain,
    model_grids=[model_grid1, model_grid2, model_grid3],
)
```

### Extended Output Configuration Pattern

The following pattern demonstrates the comprehensive output configuration used in mww3_test_03:

```python
# Extended output variable list
output_type = OutputType(
    field=OutputTypeField(
        list="HS FP DP DIR SPR WND CUR WCC WCF WCH WCM T02 T01 T0M1 FP0 THP0 THS EF TH1M TH2M"
    ),
)

# High-frequency output
output_date = OutputDate(
    field=OutputDateField(
        start="20200101 000000",
        stride="900",  # Every 15 minutes
        stop="20200102 120000",  # 36-hour simulation
    ),
)
```

## Parameter Reference

### Domain Parameters for Multi-Grid

| Parameter | Description | Typical Values | Notes |
|-----------|-------------|----------------|-------|
| nrinp | Number of input grids | 1 | Minimum 1 required |
| nrgrd | Number of model grids | 2-3 | Test dependent |
| iostyp | I/O type | 1 | Unified point output |
| start | Simulation start | YYYYMMDD HHMMSS | Test dependent |
| stop | Simulation stop | YYYYMMDD HHMMSS | Test dependent |

### ModelGrid Parameters

| Parameter | Description | Typical Values | Notes |
|-----------|-------------|----------------|-------|
| name | Grid identifier | "coarse", "medium", "fine" | Descriptive name |
| forcing | Per-grid forcing | ModelGridForcing | Differential per grid |
| resource | MPI resource allocation | ModelGridResource | Must sum to 1.0 |

### ModelGridForcing Parameters

| Parameter | Description | Values | Test Usage |
|-----------|-------------|--------|------------|
| water_levels | Water level forcing | "T" or "no" | mww3_test_03 fine grid |
| currents | Current forcing | "T" or "no" | mww3_test_03 |
| winds | Wind forcing | "T" or "no" | All tests |
| ice_conc | Ice concentration | "T" or "no" | Not used |
| air_density | Air density | "T" or "no" | Not used |
| atm_momentum | Atmospheric momentum | "T" or "no" | Not used |

### ModelGridResource Parameters

| Parameter | Description | Typical Values | Notes |
|-----------|-------------|----------------|-------|
| rank_id | MPI rank number | 1-nrgrd | Unique per grid |
| group_id | MPI group number | 1 | Default value |
| comm_frac_start | Resource start fraction | 0.0-1.0 | Cumulative |
| comm_frac_end | Resource end fraction | 0.0-1.0 | Must sum to 1.0 |

### Output Configuration Parameters

| Parameter | Description | Typical Values | Notes |
|-----------|-------------|----------------|-------|
| field.list | Output variables | Space-separated list | Test dependent |
| field.stride | Output interval | 900-3600 seconds | Test dependent |
| field.start | Output start | Domain start | Usually matches |
| field.stop | Output stop | Domain stop | Usually matches |

### Common Output Variables

| Variable | Description | Units | Category |
|----------|-------------|-------|----------|
| HS | Significant wave height | m | Basic |
| FP | Peak frequency | Hz | Basic |
| DP | Peak direction | degrees | Basic |
| DIR | Mean direction | degrees | Basic |
| SPR | Directional spreading | degrees | Extended |
| WND | Wind speed/direction | m/s, degrees | Forcing |
| CUR | Current speed/direction | m/s, degrees | Forcing |
| T01 | Mean period (1st moment) | s | Period |
| T02 | Mean period (2nd moment) | s | Period |
| T0M1 | Inverse mean period | s | Period |

## Usage

### Running Individual Tests

Each mww3_test_xx test can be executed independently using the provided Python configuration scripts:

```bash
# Navigate to the test directory
cd regtests/mww3_test_01

# Generate configuration files
python rompy_ww3_mww3_test_01.py

# Generated files are placed in rompy_runs/
ls -la rompy_runs/ww3_mww3_test_01_regression/
```

### Download Input Data

Multi-grid tests require input data files including grid depth files, wind forcing, current forcing, and water level files. Use the download script to retrieve required files:

```bash
# Download input data for a specific test
python regtests/download_input_data.py --test mww3_test_01

# Download input data for all multi-grid tests
python regtests/download_input_data.py --test mww3

# Download all regression test input data
python regtests/download_input_data.py --all
```

### Configuration Overview

Each test generates the following files:

| File | Purpose | Contents |
|------|---------|----------|
| ww3_multi.nml | Multi-grid configuration | Domain, grid definitions, coupling |
| ww3_shel.nml | Shell configuration | I/O and runtime settings |
| ww3_grid.nml | Grid preprocessing | Grid parameters |
| namelists.nml | Physics parameters | Source term configurations |

### Running with WW3

After generating configurations, execute the WW3 multi-grid model:

```bash
# Navigate to the test output directory
cd rompy_runs/ww3_mww3_test_01_regression

# Execute multi-grid WW3 (requires compiled WW3 binaries)
mpirun -n <num_ranks> ww3_multi ww3_multi.nml

# For 2-grid test: mpirun -n 2 ww3_multi ww3_multi.nml
# For 3-grid test: mpirun -n 3 ww3_multi ww3_multi.nml
```

### Docker-Based Execution

For environments without WW3 binaries, Docker-based execution is available:

```bash
# Configure backend in rompy_ww3.yaml
backend: docker

# Run with Docker
python rompy_ww3_mww3_test_01.py --backend docker
```

### Validation Approach

Multi-grid tests validate WW3 multi-grid implementations through configuration generation and comparison against expected outputs:

```python
import numpy as np
import xarray as xr

# Load expected and generated outputs for each grid
for grid_num in range(1, 4):
    expected = xr.open_dataset(f"expected_grid{grid_num}.nc")
    generated = xr.open_dataset(f"generated_grid{grid_num}.nc")
    
    # Calculate error metrics
    hs_error = np.sqrt(np.mean((generated.HS - expected.HS)**2))
    print(f"Grid {grid_num} HS RMSE: {hs_error:.4f} m")
```

## Troubleshooting

### Common Issues

**Resource Allocation Sum Not Equal to 1.0**

Error: "Communication fractions must sum to 1.0 across all grids"

This error occurs when the comm_frac_end values do not sum to exactly 1.0. For three grids with equal allocation, use 0.33, 0.67, 1.00 rather than 0.33, 0.66, 1.00.

```python
# Incorrect (sums to 0.99)
comm_frac_end=[0.33, 0.66, 1.00]  # Error!

# Correct (sums to 1.00)
comm_frac_end=[0.33, 0.67, 1.00]  # OK
```

**MPI Rank Duplication**

Error: "Each grid must have a unique rank_id"

This error occurs when two grids share the same rank_id. Ensure each grid in model_grids has a unique rank_id starting from 1.

```python
# Incorrect (duplicate rank 2)
model_grids=[
    ModelGrid(name="g1", resource=ModelGridResource(rank_id=2)),
    ModelGrid(name="g2", resource=ModelGridResource(rank_id=2)),  # Duplicate!
]

# Correct (unique ranks)
model_grids=[
    ModelGrid(name="g1", resource=ModelGridResource(rank_id=1)),
    ModelGrid(name="g2", resource=ModelGridResource(rank_id=2)),
]
```

**Missing Input Grids Error**

Error: "nrinp must be at least 1 for multi-grid configurations"

This error occurs when nrinp is set to 0. WW3 requires at least one input grid even when all grids are model grids.

```python
# Incorrect
domain = Domain(nrinp=0, nrgrd=2)  # Error!

# Correct
domain = Domain(nrinp=1, nrgrd=2)  # OK
```

**Boundary Communication Failures**

If grids fail to communicate boundaries correctly:

1. Verify grid extents are properly nested (inner grids within outer grids)
2. Check that boundary condition files exist for nested grids
3. Ensure temporal alignment of forcing files across grids
4. Verify output timesteps match forcing file time intervals

**Differential Forcing Configuration Issues**

When differential forcing does not work as expected:

1. Verify water_levels="T" only on grids requiring water level forcing
2. Ensure forcing files exist for all enabled forcing types
3. Check that forcing file paths are correctly specified
4. Verify temporal coverage of forcing files matches simulation period

### Performance Optimization

**Resource Allocation Tuning**

For optimal performance, allocate resources based on computational demand:

- Coarser grids: Less work per timestep, can use fewer resources
- Finer grids: More work per timestep (smaller timesteps), need more resources
- I/O heavy grids: May benefit from dedicated I/O ranks

```python
# Example: Fine grid needs more resources due to smaller timesteps
model_grid_coarse = ModelGrid(
    name="coarse",
    resource=ModelGridResource(rank_id=1, comm_frac_start=0.0, comm_frac_end=0.25),
)

model_grid_fine = ModelGrid(
    name="fine",
    resource=ModelGridResource(rank_id=2, comm_frac_start=0.25, comm_frac_end=1.0),
)
```

**Output Frequency Optimization**

Reduce output frequency to improve performance when high-frequency output is not required:

```python
# Hourly output (lower I/O overhead)
output_date = OutputDate(field=OutputDateField(stride="3600"))

# Every 6 hours (even lower overhead)
output_date = OutputDate(field=OutputDateField(stride="21600"))
```

### Diagnostic Commands

```bash
# Check generated ww3_multi.nml structure
grep -A 50 "MODEL(1)%" ww3_multi.nml

# Verify MPI rank configuration
grep -E "(rank_id|comm_frac)" ww3_multi.nml

# Check output variable configuration
grep "field.list" ww3_multi.nml

# Verify forcing configuration per grid
grep -A 5 "FORCE" ww3_multi.nml
```

## References

### Primary WW3 Documentation

- WAVEWATCH III User Guide: https://ww3-docs.readthedocs.io/
- WW3 GitHub Repository: https://github.com/NOAA-EMC/WW3
- WW3 Regression Tests: https://github.com/NOAA-EMC/WW3/tree/develop/regtests

### Multi-Grid Configuration

- WW3 Multi-Grid Section: User Manual Section 3.4
- MPI Parallel Implementation: WW3 documentation on parallel execution
- Boundary Condition Configuration: WW3 User Manual Section 2.5

### rompy-ww3 Documentation

- rompy-ww3 README: https://github.com/rom-py/rompy-ww3
- rompy Framework: https://github.com/rom-py/rompy
- Multi Component Source: `src/rompy_ww3/components/multi.py`
- Examples: `examples/multi_grid_example.py`

## Appendix A: Test Directory Structure

```
regtests/
├── mww3_test_xx/                  # This documentation
│   ├── README.md                  # This file
│   ├── mww3_test_01/
│   │   ├── rompy_ww3_mww3_test_01.py  # Configuration script
│   │   ├── rompy_runs/                # Generated outputs
│   │   │   └── ww3_mww3_test_01_regression/
│   │   │       ├── ww3_multi.nml      # Multi-grid namelist
│   │   │       └── ...
│   │   └── input/                      # Input data
│   │       ├── g1.depth.60x60
│   │       ├── g2.depth.40x40
│   │       └── points.list
│   ├── mww3_test_02/
│   │   └── ...
│   └── mww3_test_03/
│       └── ...
├── download_input_data.py            # Data download script
└── INPUT_DATA.md                     # Input file documentation
```

## Appendix B: Evolution of Test Complexity

### Test Progression

The three multi-grid tests demonstrate progressive complexity building toward production-ready configurations:

**mww3_test_01 - Foundation**
- Two grids with equal resource allocation
- Identical forcing across grids
- Basic output configuration
- 1-day simulation
- Establishes correct multi-grid namelist structure

**mww3_test_02 - Scaling**
- Three grids with equal resource allocation
- Increased output frequency (30 min vs 1 hour)
- Extended output variables (7 vs 4)
- Tests scaling to additional grids
- Validates three-level nesting hierarchy

**mww3_test_03 - Production Ready**
- Differential forcing per grid
- Non-uniform resource allocation (30/35/35)
- Comprehensive output (20+ variables)
- High-frequency output (15 min)
- Extended simulation (36 hours)
- Demonstrates full multi-grid flexibility

### Recommended Learning Path

1. Run mww3_test_01 to understand basic multi-grid structure
2. Examine generated ww3_multi.nml to see MODEL(n)% organization
3. Run mww3_test_02 to see three-grid coupling
4. Compare configuration differences between tests
5. Run mww3_test_03 for advanced features
6. Use mww3_test_03 patterns as templates for new configurations

---

*Documentation generated for rompy-ww3 v0.1.0*  
*Compatible with WAVEWATCH III v6.07.1*
