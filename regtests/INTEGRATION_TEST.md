# WW3 Multi-Grid Integration Test Design Document

## Overview

This document defines the integration test design for the WAVEWATCH III (WW3) multi-grid functionality using the `ww3_multi` executable and rompy-ww3's `Multi` component. Integration tests validate the complete multi-grid workflow from configuration generation through model execution and output validation. These tests ensure that rompy-ww3 correctly configures and validates multi-grid WW3 simulations where multiple computational grids exchange boundary conditions and run in coupled mode.

Multi-grid modeling represents one of WW3's most sophisticated capabilities, enabling multiple grids to run simultaneously with coupling between them. This allows for nested modeling where a coarse-resolution outer grid provides boundary conditions to finer-resolution inner grids, enabling efficient high-resolution simulations over specific regions of interest. The integration tests documented here validate that rompy-ww3 correctly generates all required namelist configurations, that the generated configurations execute successfully in WW3, and that the outputs match expected reference results.

The multi-grid integration test suite builds progressively from basic two-grid configurations through complex three-grid hierarchies with differential forcing and non-uniform resource allocation. Each test level introduces additional complexity, validating progressively more sophisticated multi-grid capabilities. The design ensures that fundamental multi-grid functionality is validated first, with advanced features built upon validated foundations.

## Multi-Grid Architecture and Concepts

### Multi-Grid Fundamentals

WW3 multi-grid capability allows multiple computational grids to run in a single model execution, with coupling between grids defined through the `ww3_multi` executable. Unlike running separate single-grid simulations, multi-grid mode enables real-time boundary condition exchange between grids, where boundary conditions from a coarser grid can feed into a finer nested grid, and vice versa for wave radiation. This coupling requires careful configuration of grid indices, communication fractions, and boundary condition mappings.

The multi-grid architecture in WW3 uses a hierarchical approach where each grid is assigned a rank identifier and a communication fraction range. The communication fractions determine how MPI processes are allocated to each grid, with the total summing to 1.0 (representing 100% of available resources). For example, in a two-grid configuration with equal resources, the coarse grid might use communication fractions 0.0-0.5 (50% of processes) and the fine grid would use 0.5-1.0 (remaining 50%). This resource allocation allows each grid to operate on a dedicated subset of MPI processes while maintaining coupling through inter-process communication.

Boundary exchange between grids occurs at defined spatial locations where grids overlap or touch. The outer grid provides boundary conditions to inner nested grids, while wave energy radiating from inner grids can flow back to outer grids. This bidirectional coupling requires that grid geometries be properly defined with clear boundary relationships. The namelist configuration must specify which grids provide boundary conditions to which other grids, typically through the `BOUNDARY%` configuration section in the multi-grid namelist.

Rompy-ww3's `Multi` component abstracts this complexity through a Pythonic interface that separates grid configuration, resource allocation, and output management into distinct objects. The `ModelGrid` class configures individual grids including their forcing options and resource allocation, while the `Multi` component orchestrates the overall multi-grid configuration including domain-wide settings and output specifications. This design allows test configurations to clearly express multi-grid intent while delegating namelist generation details to the rompy-ww3 framework.

### Multi-Grid Configuration Elements

The multi-grid namelist (`ww3_multi.nml`) contains several key sections that must be correctly configured for successful multi-grid execution. The `DOMAIN_NML` section defines the overall simulation parameters including start and stop times, the number of input grids (`nrinp`), and the number of model grids (`nrgrd`). Input grids represent external data sources that provide forcing to the model grids, while model grids are the actual computational grids that simulate wave physics. The minimum valid configuration requires at least one input grid (`nrinp >= 1`) and one or more model grids (`nrgrd >= 1`).

The `MODEL_GRID_NML` section (repeated for each grid) defines parameters specific to individual model grids including the grid name, forcing options, and resource allocation. The grid name must match any corresponding grid depth file and is used in output file naming. Forcing options control which physical processes are active on each grid, including wind forcing, water level forcing, current forcing, ice concentration, atmospheric momentum, and air density. Each forcing option can be enabled (`"T"`) or disabled (`"F"`) independently per grid, enabling differential forcing where only specific grids have certain physics activated.

The `MODEL_GRID_RESOURCE_NML` section (also repeated per grid) controls MPI resource allocation through the `comm_frac_start` and `comm_frac_end` parameters. These define the fraction range for each grid's MPI communicator, where the start value of each grid must equal the end value of the previous grid (or 0.0 for the first grid), and the final grid's end value must equal 1.0. This creates contiguous, non-overlapping resource allocation across all grids. The `rank_id` parameter assigns a unique rank identifier to each grid's MPI communicator group, while the `group_id` parameter assigns grids to communication groups for collective operations.

Output configuration in multi-grid mode follows similar patterns to single-grid configurations but with per-grid output specifications. The `OUTPUT_TYPE_NML` section defines which output fields are generated (such as significant wave height `HS`, peak period `FP`, mean direction `DIR`), while `OUTPUT_DATE_NML` controls output timing including start time, stop time, and output stride (interval between outputs). In multi-grid configurations, outputs are generated for each model grid separately, with grid identifiers incorporated into output file names.

### Coupling and Boundary Exchange

The physical coupling between grids in WW3 multi-grid mode operates through shared boundary conditions where grids touch or overlap spatially. When a fine-resolution nested grid is placed within a coarser outer grid, the outer grid provides time-varying boundary conditions (wave spectra) to the inner grid at their shared boundary points. Conversely, waves generated or reflected within the inner grid that propagate outward provide boundary conditions back to the outer grid. This bidirectional coupling enables nested grids to capture high-resolution physics while maintaining consistency with the larger-scale wave field.

Boundary condition exchange requires that grid geometries be properly aligned and that the nesting relationships be correctly specified in the namelist configuration. The depth files for each grid must be present and correctly formatted, containing bathymetry information that WW3 uses for wave propagation calculations. Wind and other forcing fields must be available for each grid's domain at appropriate temporal resolution. The temporal resolution of forcing fields typically differs from output stride, with forcing often available at higher frequency than model output.

In WW3 multi-grid mode, boundary exchange occurs at each computational timestep according to the configured coupling frequency. The coupling frequency is controlled by the `dtcfl` parameter and must satisfy stability constraints relative to the grid's spatial and temporal resolution. Finer grids typically require more frequent coupling updates to maintain numerical stability and physical accuracy. The timestep configuration (`dtmax`, `dtxy`, `dtkth`) must be appropriate for each grid's resolution, with finer grids requiring smaller timesteps than coarser grids.

Rompy-ww3's validation approach for boundary exchange focuses on verifying that coupling-related features produce expected results. This includes checking that output files exist for all configured grids, that file naming conventions include grid identifiers, and (where reference data exists) that output values fall within expected ranges considering the coupling configuration. For regression testing, outputs from the rompy-ww3 configuration are compared against reference outputs from official WW3 test cases to verify numerical consistency.

## Test Scenario Design

### Test Scenario 1: Basic Two-Grid Configuration (mww3_test_01)

The first integration test validates fundamental multi-grid functionality using the simplest valid multi-grid configuration: two model grids with equal resource allocation. This test establishes baseline validation for multi-grid configuration generation, MPI resource allocation, and coupled grid execution. The test configuration uses a coarse outer grid and a finer inner grid to demonstrate the typical nesting pattern used in operational wave modeling.

The test scenario creates two model grids: a coarse grid named "coarse" and a fine grid named "fine". Both grids use identical forcing configuration with wind forcing enabled and water levels, currents, ice, and other forcing disabled. This simplified forcing focuses validation on the multi-grid coupling mechanism without complicating factors from multiple active forcing types. The wind forcing simulates typical atmospheric conditions that generate wave energy, providing a realistic wave field for validating coupling behavior.

Resource allocation in this test uses equal division of MPI processes between grids, with the coarse grid receiving communication fractions 0.00-0.50 (50% of resources) and the fine grid receiving 0.50-1.00 (remaining 50%). This equal division provides symmetric resource allocation that simplifies performance interpretation and ensures comparable computational cost between grids. The `rank_id` values (1 and 2 respectively) assign unique identifiers to each grid's MPI communicator.

The domain configuration spans one day (24 hours) from January 1, 2020, with unified point output (`iostyp=1`) enabled. Output frequency is hourly (3600-second stride) with four output fields: significant wave height (`HS`), peak frequency (`FP`), peak direction (`DP`), and mean direction (`DIR`). These four fields represent the most commonly used wave parameters and provide sufficient diagnostic information to validate coupling behavior without generating excessive output volume.

This test validates the following capabilities:
- Two-grid configuration generation with correct namelist structure
- Equal MPI resource allocation with proper communication fractions
- Identical forcing configuration applied to multiple grids
- Per-grid output specification and file generation
- Coupled execution with boundary exchange between grids

### Test Scenario 2: Three-Grid Hierarchy (mww3_test_02)

The second integration test extends multi-grid validation to a three-level hierarchical nesting configuration. This test introduces additional complexity through increased grid count, demonstrating rompy-ww3's capability to configure more sophisticated multi-grid hierarchies where a coarse outer grid nests an intermediate grid, which in turn nests a fine inner grid. The three-level hierarchy represents typical operational nesting strategies for capturing basin-scale wave patterns with high-resolution coastal resolution.

The test configuration creates three model grids with progressive refinement: a coarse outer grid named "coarse", an intermediate-resolution grid named "medium", and a fine inner grid named "fine". Each grid receives approximately one-third of available MPI resources through the communication fraction configuration: coarse grid 0.00-0.33, medium grid 0.33-0.67, and fine grid 0.67-1.00. This near-equal distribution provides balanced resource allocation across the grid hierarchy while accommodating different computational demands based on grid resolution.

Forcing configuration remains simplified relative to the most complex scenarios, with wind forcing enabled on all three grids and other forcing types disabled. The simplified forcing ensures that coupling validation focuses on the multi-grid mechanism itself rather than interactions between multiple active forcing types. In operational configurations, different grids might have different forcing configurations based on data availability and regional characteristics, but this test establishes the baseline case where all grids receive identical forcing.

Output configuration in this test expands beyond the basic four fields to include seven output variables: significant wave height (`HS`), peak frequency (`FP`), peak direction (`DP`), mean direction (`DIR`), directional spread (`SPR`), wind parameters (`WND`), and current parameters (`CUR`). The additional output fields validate that extended output configurations work correctly in multi-grid mode and provide more diagnostic information for coupling validation. Output frequency increases to 30-minute intervals (1800-second stride), testing that more frequent output generation works correctly alongside multi-grid execution.

This test validates the following additional capabilities:
- Three-level hierarchical grid nesting configuration
- Near-equal resource allocation across three grids
- Progressive grid refinement with appropriate timestep configuration
- Extended output field specification across multiple grids
- Higher-frequency output generation in multi-grid context

### Test Scenario 3: Advanced Multi-Grid Features (mww3_test_03)

The third integration test demonstrates advanced multi-grid capabilities including differential forcing per grid, non-uniform resource allocation, comprehensive output configurations, and extended simulation duration. This test validates the full flexibility of WW3 multi-grid modeling where grids can have different physics configurations, unequal resource allocation based on computational demand, and extensive output requirements. The scenario represents a realistic operational configuration where regional grid characteristics drive different configurations for each grid.

The differential forcing configuration activates water levels only on the fine grid while keeping them disabled on the coarse and medium grids. This pattern reflects typical operational requirements where water level forcing is critical for accurate nearshore wave modeling (requiring the fine grid resolution) but unnecessary or unavailable for larger-scale ocean grids. Currents and winds are enabled on all three grids, providing consistent forcing for wave generation and propagation across all domains. This selective activation demonstrates that rompy-ww3 correctly configures per-grid forcing options and that WW3 executes correctly with heterogeneous forcing configurations.

Resource allocation in this test uses non-uniform distribution based on expected computational demand: coarse grid receives 30% of resources (0.00-0.30 communication fractions), medium grid receives 35% (0.30-0.65), and fine grid receives 35% (0.65-1.00). The coarse grid receives proportionally fewer resources because its larger cell size means fewer computational points and lower per-timestep cost, while the finer grids receive more resources to accommodate their higher point counts. This allocation pattern demonstrates load balancing considerations in multi-grid configurations.

The output configuration in this test represents the most comprehensive in the multi-grid test suite, specifying over 20 output fields including wave parameters (`HS`, `FP`, `DP`, `DIR`, `SPR`), forcing parameters (`WND`, `CUR`), wave partition components (`WCC`, `WCF`, `WCH`, `WCM`), mean period definitions (`T02`, `T01`, `T0M1`), peak parameters (`FP0`, `THP0`, `THS`), and spectral moments (`EF`, `TH1M`, `TH2M`). Output frequency is the highest in the test suite at 15-minute intervals (900-second stride), and simulation duration extends to 36 hours (1.5 days) rather than the 24-hour duration of previous tests.

This test validates the following advanced capabilities:
- Differential forcing activation per grid (heterogeneous physics configuration)
- Non-uniform resource allocation based on computational demand
- Comprehensive output field specification across multiple grids
- High-frequency output generation (15-minute intervals)
- Extended-duration simulation validation (36 hours)

### Test Scenario 4: Grid Boundary Exchange Validation

The fourth integration test focuses specifically on validating boundary exchange between coupled grids. While the previous tests validate that multi-grid configurations execute successfully, this test explicitly validates the correctness of boundary exchange by comparing outputs at boundary points against known reference values. Boundary exchange validation requires careful selection of comparison locations and appropriate tolerance settings given the inherent variability in coupling calculations.

The boundary exchange test configuration uses a simplified two-grid setup optimized for validating coupling behavior. The grids are positioned to create clear boundary interfaces where known boundary conditions can be imposed and verified. Output locations include specific points along boundary interfaces where boundary condition transfer can be directly assessed. The test generates high-frequency output (10-minute stride) along boundaries to capture the temporal evolution of boundary condition exchange.

Validation of boundary exchange examines several aspects of the coupling behavior. First, boundary point outputs from the nested (inner) grid should show smooth transition from boundary conditions provided by the outer grid, with wave energy entering the nested domain through the boundary. Second, outputs from the outer grid near the nesting region should show appropriate modification from waves radiating outward from the nested grid. Third, the temporal evolution of boundary conditions should reflect the configured coupling frequency without artifacts from coupling frequency mismatches.

The test design includes explicit validation checks for boundary exchange correctness:
- Existence of boundary point outputs at configured locations
- Temporal continuity in boundary point time series
- Energy consistency between outer and nested grid outputs
- Appropriate wave direction and frequency characteristics at boundaries

### Test Scenario 5: Resource Allocation Verification

The fifth integration test validates that MPI resource allocation functions correctly in multi-grid configurations. This test verifies that the communication fraction configuration correctly distributes MPI processes among grids and that WW3 executes with the expected process layout. Resource allocation validation requires monitoring WW3 execution to confirm process distribution and checking that no grid starves for computational resources.

The resource allocation test creates configurations with varying resource distributions to validate the allocation mechanism across different scenarios. Test cases include equal distribution (50/50, 33/33/34), skewed distributions (80/20, 70/20/10), and nearly extreme distributions (90/5/5). Each configuration validates that the communication fractions sum to 1.0 and that individual grid fractions form contiguous ranges without gaps or overlaps.

Execution validation for resource allocation confirms that WW3 spawns the expected number of processes for each grid and that the MPI communicator topology matches the configured fractions. This validation requires either WW3 runtime output that reports process allocation or external monitoring tools that can observe the MPI process layout. The test passes when the configured resource allocation matches observed allocation within measurement tolerance.

Performance validation complements the allocation validation by confirming that the resource distribution produces the expected computational behavior. Faster grids should complete their work more quickly when receiving more resources, and computational load should balance approximately according to the configured fractions. This validation helps ensure that rompy-ww3's resource allocation configuration translates into actual computational behavior in WW3.

## Validation Approach

### Namelist Validation

The first validation layer examines the generated namelist files for correctness before WW3 execution begins. Namelist validation catches configuration errors early in the test process, preventing wasted computational time on invalid configurations. The validation checks that all required namelist sections are present, that parameter values fall within valid ranges, and that cross-sectional consistency constraints are satisfied.

The rompy-ww3 framework performs initial validation during namelist generation through its Pydantic model definitions. Field validators check that communication fractions fall between 0.0 and 1.0, that timestep values satisfy stability constraints (`dtmax` approximately 3 times `dtxy`, `dtkth` between `dtmax/10` and `dtmax/2`), and that grid names contain only valid characters. These validators prevent obviously incorrect configurations from being generated.

Additional namelist validation examines the generated WW3 namelist file against WW3's expected format and content requirements. This validation confirms that the rompy-ww3 Multi component produces correctly formatted FORTRAN namelist syntax, that all required sections are present with appropriate variable definitions, and that no obvious formatting errors exist. The validation parses the generated file and checks structure rather than relying solely on WW3's own error messages.

Specific namelist validation checks include:
- Communication fraction continuity (end of grid N equals start of grid N+1)
- Total resource fraction sums to 1.0 across all grids
- Unique rank_id assignments for each grid
- Valid forcing option values (`"T"` or `"F"` only)
- Output field names match WW3 expected variables
- Timestep configuration satisfies stability constraints

### Output File Validation

Output validation confirms that WW3 generates expected output files for each configured grid and that the outputs contain valid data. Output validation occurs after test execution and compares generated outputs against reference outputs when available, or performs sanity checks on output content when reference data is not available.

File existence validation confirms that output files are created for each configured grid with appropriate naming conventions. Multi-grid WW3 output files typically include grid identifiers in their names, distinguishing outputs from different grids. The validation confirms that expected files exist and that their sizes indicate valid content rather than empty files or error messages.

Variable validation examines the content of output files to confirm that all configured output fields are present and contain valid numerical data. Each expected variable should exist in the output with the correct dimensions (time, latitude, longitude for spatial outputs, time for point outputs). Invalid values (NaN, infinity) indicate problems with the simulation that require investigation.

Numerical validation compares output values against reference values to detect regressions in model behavior. The comparison uses appropriate tolerance levels given the floating-point nature of WW3 calculations. Relative tolerance of 1e-6 serves as the default comparison threshold, with field-specific tolerances applied where physics or numerics suggest different appropriate thresholds.

### Coupling Validation

Coupling validation specifically examines the boundary exchange behavior between coupled grids. This validation layer goes beyond basic output existence to assess whether coupling produces physically reasonable results consistent with expected nested grid behavior. Coupling validation requires analysis techniques tailored to multi-grid outputs.

Boundary point validation examines output time series at configured boundary locations. Valid boundary coupling produces smooth transitions where wave energy from the outer grid enters the nested domain, with no artificial discontinuities or oscillations that would indicate coupling problems. The validation examines boundary point time series for smoothness and physical reasonableness.

Grid comparison validation examines outputs from different grids at equivalent locations to assess coupling consistency. Where grids overlap or touch, their outputs should show consistent wave fields with appropriate differences due to resolution. Significant inconsistencies between grids at equivalent locations indicate coupling or configuration problems requiring investigation.

Temporal coupling validation examines the temporal evolution of coupled outputs. The coupling frequency should produce smooth temporal evolution in boundary conditions without artifacts from discrete coupling updates. High-frequency boundary output helps assess whether coupling updates occur at the expected frequency and produce smooth transitions.

### Performance Validation

Performance validation ensures that multi-grid configurations execute efficiently and that resource allocation produces expected computational behavior. Performance validation operates alongside functional validation to confirm that the multi-grid configuration achieves expected computational efficiency.

Execution time validation confirms that test executions complete within expected time bounds based on configuration complexity. Longer simulations or higher-resolution grids should proportionally increase execution time. Unexpectedly long or short execution times may indicate configuration problems, resource starvation, or numerical instability.

Resource utilization validation confirms that the allocated computational resources are effectively utilized. Each grid should utilize its allocated MPI processes without excessive idle time or process congestion. Resource utilization metrics from WW3 runtime output or external monitoring inform this validation.

Scaling validation examines how execution time scales with configuration changes. Adding grids, increasing output frequency, or enabling additional physics should proportionally increase computational cost. Deviations from expected scaling indicate configuration or execution problems.

## Pass/Fail Criteria

### Mandatory Pass Criteria

All integration tests must satisfy mandatory pass criteria regardless of test scenario or complexity level. These criteria represent fundamental requirements for any multi-grid WW3 configuration and execution. Tests failing mandatory criteria are classified as failed regardless of other results.

The first mandatory criterion requires successful namelist generation without errors. The rompy-ww3 configuration process must complete without raising exceptions, and the generated namelist file must pass structural validation checks. Namelist generation failures indicate configuration errors that prevent WW3 execution.

The second mandatory criterion requires successful WW3 execution without crashes. The WW3 model must complete the configured simulation without segmentation faults, floating point exceptions, or other fatal errors. Execution crashes indicate fundamental incompatibilities between the rompy-ww3 configuration and the WW3 executable.

The third mandatory criterion requires output file generation for all configured grids. Each model grid must produce at least one output file containing valid data. Missing output files from any grid indicate execution or coupling problems.

The fourth mandatory criterion requires output content validation. Each generated output file must contain the configured output fields with valid numerical values. Outputs containing only NaN, infinity, or zero values indicate simulation problems.

### Scenario-Specific Pass Criteria

Beyond mandatory criteria, each test scenario defines specific pass criteria based on its validation objectives. Tests failing scenario-specific criteria are classified as failed but may still provide useful information about partial functionality.

The two-grid test (mww3_test_01) requires validation that both grids execute with correct resource allocation. The test passes when both grids complete successfully and produce outputs, when the output files correctly distinguish between grids through naming conventions, and when output values are physically reasonable for the configured wind forcing.

The three-grid test (mww3_test_02) additionally requires validation of the hierarchical coupling structure. The test passes when all three grids complete successfully, when outputs show appropriate nested grid behavior (finer grids showing higher-resolution features within the coarse grid domain), and when the extended output field configuration works correctly.

The advanced features test (mww3_test_03) requires validation of differential forcing and non-uniform resource allocation. The test passes when the water level forcing is correctly applied only to the fine grid, when resource allocation matches the configured fractions, and when the comprehensive output configuration generates all expected fields.

The boundary exchange test requires explicit validation of coupling correctness. The test passes when boundary point outputs show smooth transitions between grids, when grid comparisons show consistent wave fields at equivalent locations, and when temporal evolution reflects the configured coupling frequency.

### Validation Thresholds

Numerical validation uses defined thresholds to accommodate acceptable variability in WW3 outputs. Values outside these thresholds indicate potential problems requiring investigation. The thresholds recognize that floating-point calculations may produce small differences between runs due to different computational environments, compiler versions, or numerical ordering.

The default relative tolerance is 1e-6 (0.0001%), requiring output values to match reference values within one part per million. This tight tolerance catches significant regressions while accommodating acceptable floating-point variation.

Field-specific tolerances adjust for physics where larger variations are acceptable. Wave heights (HS) use 1e-4 tolerance to accommodate small variations in integrated energy calculations. Period variables (FP, T01, T02) use 1e-3 tolerance given sensitivity of spectral peak detection. Direction variables (DP, DIR) use 1e-2 tolerance considering sensitivity of directional calculations.

Absolute tolerance applies to near-zero values where relative tolerance would be inappropriate. Values with magnitude below 1e-10 use absolute tolerance of 1e-12, ensuring meaningful comparison even when relative differences would be large.

### Failure Classification

Test failures are classified into categories to help diagnose problems and prioritize fixes. The classification distinguishes between configuration problems, execution problems, numerical problems, and acceptable variations.

Configuration failures indicate problems in the rompy-ww3 configuration that prevent valid namelist generation. These failures require fixes to the rompy-ww3 code or configuration. Examples include invalid parameter values, missing required fields, and schema violations.

Execution failures indicate that WW3 encountered problems during execution. These failures may indicate rompy-ww3 configuration problems, WW3 bugs, or environmental issues. Examples include segmentation faults, memory allocation failures, and numerical instability.

Numerical failures indicate that WW3 executed but produced results significantly different from reference values. These failures may indicate configuration problems, environmental differences, or WW3 bugs. Examples include values outside validation thresholds, unphysical output values, and missing expected features.

Acceptable variations fall within defined tolerance bounds but differ from reference values. These variations do not constitute test failures but should be documented and monitored for trend analysis. Examples include small floating-point differences and timing variations.

## Test Execution Workflow

### Pre-Execution Phase

Before test execution begins, the workflow validates the execution environment and prepares necessary inputs. This phase catches configuration problems early and ensures that tests run under appropriate conditions.

Environment validation confirms that required software is available and correctly configured. The validation checks for Python packages (rompy, rompy-ww3), WW3 executables (ww3_multi), and input data files. Missing dependencies cause immediate failure with clear error messages indicating what's missing.

Input data preparation copies or creates necessary input files for the test configuration. Depth files, wind forcing files, boundary condition files, and other required inputs must be available in the expected locations. The preparation phase confirms file existence and basic validity (correct format, expected dimensions).

Configuration generation runs rompy-ww3 to produce the WW3 namelist from the test's Python configuration. The generation phase validates the configuration against rompy-ww3's schema and reports any configuration errors. Successful generation produces a valid `ww3_multi.nml` file ready for WW3 execution.

### Execution Phase

The execution phase runs WW3 with the generated configuration and captures output for validation. The phase handles execution monitoring, output capture, and error detection.

Execution submission launches WW3 with appropriate parallelization and resource configuration. The submission specifies the number of MPI processes, working directory, and input namelist. Submission failures indicate configuration or environment problems.

Execution monitoring tracks the running WW3 process for progress and problems. Monitoring confirms that WW3 starts successfully, makes expected progress through the simulation, and completes within reasonable time bounds. Timeouts indicate problems requiring investigation.

Output capture collects WW3 standard output, error streams, and generated files. Captured output supports debugging when problems occur and provides information for validation. Incomplete capture indicates execution problems.

### Post-Execution Phase

After execution completes (successfully or otherwise), the post-execution phase performs validation and result processing. This phase generates the test result that determines pass/fail status.

Output collection gathers all generated files into the expected output directory structure. Collected files include NetCDF outputs, log files, restart files, and any other WW3-generated content. Collection failures indicate execution or filesystem problems.

Validation execution runs the configured validation checks against collected outputs. Validation includes file existence checks, content validation, and numerical comparison against reference values. Validation produces a detailed report of all checks and their results.

Result processing aggregates validation results into a test outcome. The outcome classification follows the pass/fail criteria defined for the test scenario. Result processing produces machine-readable results suitable for CI integration and human-readable reports for debugging.

## Expected Multi-Grid Behavior

### Grid Execution Behavior

Multi-grid WW3 executes all configured grids simultaneously using MPI parallelization. Each grid operates on its allocated subset of MPI processes, with the communicator configuration determined by the communication fractions. The grids advance through time synchronously, coupling their boundary conditions at each coupling timestep.

Successful multi-grid execution shows WW3 initializing all grids without errors, advancing through the configured timesteps with expected progress, and completing the full simulation duration. The WW3 log output shows messages for each grid's initialization, timestep advancement, and coupling operations. Abnormal termination of any grid causes test failure.

The execution produces separate output files for each configured grid. Output files follow WW3 naming conventions that include grid identifiers. For example, a test with grids "coarse" and "fine" produces outputs like `ww3_coarse.nc` and `ww3_fine.nc` (or similar based on output configuration). All configured grids must produce outputs for test success.

### Coupling Behavior

Boundary coupling between grids occurs at each coupling timestep defined by the `dtcfl` parameter. The coupling exchanges wave spectra at grid boundaries, with the outer grid providing boundary conditions to nested grids and receiving radiated energy from nested grids. Correct coupling produces smooth wave field evolution across the nested domain structure.

Validation of coupling behavior examines outputs at boundary points and overlapping regions. Valid coupling shows consistent wave fields between grids at equivalent locations, with differences attributable to resolution rather than coupling errors. Boundary point time series should show smooth transitions without artificial oscillations or discontinuities.

The temporal evolution of coupled outputs reflects the coupling frequency. Higher coupling frequencies produce smoother boundary transitions but require more frequent inter-grid communication. The configured coupling frequency should balance smoothness requirements against computational efficiency.

### Resource Utilization

MPI resource utilization in multi-grid mode depends on the configured communication fractions and the computational load of each grid. Properly configured allocations should keep all grid processes busy without significant idle time waiting for coupling synchronization. Under-utilization indicates configuration problems or WW3 bugs.

The total number of MPI processes used equals the configured parallelization level. For example, a test configured with 4 MPI total processes and 50/50 resource allocation would spawn 2 processes for each grid. Resource allocation must sum to 1.0, and individual allocations must be contiguous.

Load balancing considerations suggest that resource allocation should roughly correspond to computational demand. Finer-resolution grids with more computational points typically need proportionally more resources than coarser grids. Unbalanced allocations may cause some grids to finish faster than others, with idle processes waiting for slower grids.

## Test Output Reference

### Output File Structure

Multi-grid test outputs follow a defined structure that supports validation and analysis. The structure separates outputs by grid while maintaining clear provenance for each file.

Output files reside in the test's output directory with subdirectories optionally organizing by grid. The recommended structure places all outputs directly in the test output directory with grid identifiers embedded in filenames: `{test_id}_{grid_name}_output.nc`. Alternative structures may use subdirectories: `{grid_name}/{test_id}_output.nc`.

Output file naming conventions encode important metadata including test identifier, grid name, output type, and timestamp. Consistent naming supports automated validation and manual analysis. The naming convention should match WW3's expected output format and rompy-ww3's configured file patterns.

Log files capture WW3 standard output and error streams for debugging and monitoring. Log files should preserve the original WW3 output including timestep counts, coupling messages, and any warning or error messages. Log files support troubleshooting when validation fails.

### Validation Output Structure

Validation results follow a structured format suitable for both human review and automated processing. The structure includes summary statistics, detailed comparison results, and diagnostic information for failures.

The validation summary presents high-level results: total files compared, files passing validation, files failing, and overall pass/fail status. The summary enables quick assessment of test outcomes and identifies whether failures occurred.

Detailed results for each compared file include file name, comparison status (pass/fail), numerical differences (where applicable), and diagnostic information for failures. The detailed results support debugging when validation fails by identifying exactly which files and variables have problems.

Failure diagnostics for failed tests include specific information about what went wrong: which files failed, which variables exceeded tolerances, and what the actual differences were. The diagnostics help distinguish between configuration problems, execution problems, and acceptable numerical variations.

## Implementation Notes

### Configuration Pattern

Multi-grid tests follow a consistent configuration pattern that enables reuse across test scenarios and provides clear documentation of tested capabilities. The pattern separates configuration into logical sections: domain configuration, per-grid configuration, resource allocation, and output configuration.

The domain configuration defines simulation-wide parameters including start time, stop time, number of grids, and I/O settings. The domain section establishes the temporal extent and grid count that all subsequent configurations build upon.

Per-grid configurations define individual grids through the ModelGrid class. Each grid receives a unique name, forcing configuration, and grid-specific parameters. The per-grid pattern enables differential configurations where different grids have different physics or resource allocations.

Resource allocation links per-grid configurations to MPI resource distribution through the ModelGridResource class. The allocation defines communication fractions, rank identifiers, and group identifiers. The allocation pattern ensures proper MPI configuration while maintaining flexibility.

Output configuration specifies output fields and timing through the OutputType and OutputDate classes. Output configuration applies across all grids while allowing for grid-specific overrides if needed.

### Test Isolation

Each multi-grid test operates in isolation with its own output directory and working environment. Isolation prevents interference between tests and ensures that failures in one test don't affect others. The isolation pattern supports parallel test execution and clean result attribution.

Temporary directories created for each test execution are cleaned up after completion (successful or failed). Cleanup removes temporary files while preserving validation outputs for debugging. The cleanup pattern maintains filesystem hygiene while supporting post-failure investigation.

Input data dependencies are explicitly declared and managed through the test framework. Tests specify required input files, and the framework ensures availability before execution. The dependency pattern prevents tests from failing due to missing data when the data should be available.

### Error Handling

Test execution includes comprehensive error handling to capture problems at appropriate levels and provide useful diagnostics. Error handling distinguishes between expected failures (which don't indicate problems) and unexpected failures (which require investigation).

Configuration errors during rompy-ww3 execution are caught and reported with context about what configuration element caused the problem. The error handling provides sufficient information to identify and fix configuration problems without requiring detailed debugging.

WW3 execution errors are captured through output stream monitoring and process status checking. The error handling distinguishes between WW3 crashes (fail-fast errors) and WW3 completion with problems (completion with errors). Different error types receive appropriate treatment in result classification.

Validation failures produce detailed diagnostics about what failed and why. The diagnostic information supports rapid identification of whether failures indicate real problems or acceptable variations. Detailed diagnostics reduce time spent investigating false positives.

## References

The multi-grid integration test design draws from several sources documenting WW3 multi-grid capabilities and rompy-ww3 configuration patterns.

The official WW3 documentation provides authoritative information on multi-grid configuration syntax and behavior. The WW3 User Manual section on multi-grid modeling describes the physical and numerical basis for coupled grid simulations. WW3 test case documentation (available in the WW3 repository) provides reference configurations and expected behaviors.

The rompy-ww3 codebase provides implementation details for the Multi component and related classes. Source code documentation in `src/rompy_ww3/components/multi.py` describes the programmatic interface for multi-grid configuration. Pydantic model definitions in the namelists modules define validation rules and configuration constraints.

Regression test infrastructure documentation in `regtests/runner/README.md` describes the test runner architecture and validation framework. The Validator class documentation provides details on comparison modes and tolerance configurations. The TestRunner documentation describes the execution workflow and result processing.

Previous test implementations in `regtests/mww3_test_01/`, `mww3_test_02/`, and `mww3_test_03/` provide concrete examples of multi-grid configurations following the patterns described in this document. These implementations serve as reference templates for additional test scenarios.

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-11 | Initial integration test design document |

## Appendices

### Appendix A: Complete Test Matrix

| Test | Grids | Forcing | Resources | Output Fields | Duration | Validates |
|------|-------|---------|-----------|--------------|----------|-----------|
| mww3_test_01 | 2 | Winds only | Equal (50/50) | 4 basic | 24h | Basic multi-grid |
| mww3_test_02 | 3 | Winds only | Equal (33/33/34) | 7 extended | 24h | 3-level hierarchy |
| mww3_test_03 | 3 | Differential | Unequal (30/35/35) | 20+ comprehensive | 36h | Advanced features |
| Boundary Exchange | 2 | Winds only | Equal (50/50) | Boundary pts | 24h | Coupling correctness |
| Resource Allocation | 3 | Winds only | Various | Minimal | 12h | Resource distribution |

### Appendix B: Output Variable Reference

| Variable | Description | Typical Tolerance |
|----------|-------------|-------------------|
| HS | Significant wave height | 1e-4 |
| FP | Peak frequency | 1e-3 |
| DP | Peak direction | 1e-2 |
| DIR | Mean direction | 1e-2 |
| SPR | Directional spread | 1e-3 |
| WND | Wind parameters | 1e-3 |
| CUR | Current parameters | 1e-3 |
| T01 | Mean period (m0/m1) | 1e-3 |
| T02 | Mean period (sqrt(m0/m2)) | 1e-3 |
| T0M1 | Inverse mean period | 1e-3 |

### Appendix C: Communication Fraction Specification

Communication fractions define MPI resource allocation across grids. The specification follows a consistent pattern where each grid receives a contiguous range of the total resource fraction.

**Valid configurations:**

- Two grids, equal: Grid1 (0.00-0.50), Grid2 (0.50-1.00)
- Two grids, skewed: Grid1 (0.00-0.25), Grid2 (0.25-1.00)
- Three grids, equal: Grid1 (0.00-0.33), Grid2 (0.33-0.67), Grid3 (0.67-1.00)
- Three grids, unequal: Grid1 (0.00-0.30), Grid2 (0.30-0.65), Grid3 (0.65-1.00)

**Invalid configurations:**

- Gaps: Grid1 (0.00-0.40), Grid2 (0.50-1.00) — gap between 0.40-0.50
- Overlaps: Grid1 (0.00-0.60), Grid2 (0.50-1.00) — overlap 0.50-0.60
- Incomplete: Grid1 (0.00-0.70), Grid2 (0.70-0.90) — doesn't reach 1.00
