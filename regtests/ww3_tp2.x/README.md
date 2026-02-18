# WW3 tp2.x Test Series Documentation

## Overview

The WW3 tp2.x test series constitutes the comprehensive validation suite for WAVEWATCH III (WW3) two-dimensional wave propagation physics. This extensive collection of seventeen regression tests systematically validates the core numerical and physical processes that govern wave behavior in oceanic and coastal environments across diverse grid configurations. Each test isolates specific physical mechanisms—including spherical propagation, curvilinear grids, unstructured meshes, SMC multi-resolution grids, complex bathymetry, wave-current interactions, and advanced source term formulations—to ensure accurate wave simulation across diverse conditions.

The tp2.x series serves as the advanced validation suite following the foundational tp1.x one-dimensional tests, establishing confidence in two-dimensional wave propagation and spatial complexity handling. These tests employ increasingly sophisticated grid configurations—from simple Cartesian rectangles through global spherical grids with tripole closures—while maintaining computational efficiency appropriate for regression testing. The rompy-ww3 plugin provides complete configuration support for all tp2.x tests through its component-based architecture, enabling reproducible generation of WW3 namelist files and seamless integration with automated testing frameworks.

### Test Series Objectives

The tp2.x test series accomplishes several critical objectives for WW3 model validation. First, it validates two-dimensional wave propagation on multiple grid types, ensuring numerical accuracy in both horizontal dimensions simultaneously. Second, it exercises the full range of supported grid configurations including rectilinear Cartesian, rectilinear spherical, curvilinear, unstructured triangular, and Spherical Multi-Cell (SMC) grids. Third, it validates complex physical processes including spherical geometry effects, garden sprinkler effects, wave-current interactions, reflection physics, and bottom interaction effects. Fourth, it validates boundary condition handling for regional nested models and data assimilation capabilities. Finally, it provides comprehensive reference outputs that enable detection of regressions during model development and maintenance.

Each test targets a specific combination of grid configuration and physical process, allowing developers to pinpoint the source of discrepancies when model behavior deviates from expectations. The progressive complexity of tests—from simple Cartesian propagation through global grids with full physics—enables systematic validation of increasing model sophistication. This modular validation approach has proven essential for maintaining WW3 code quality across the wide range of applications from local coastal to global wave forecasting.

### Physical Processes and Grid Types Covered

The seventeen tests in the tp2.x series comprehensively cover the essential physical processes and grid configurations governing wave evolution in the global ocean. Two-dimensional propagation tests establish baseline numerical accuracy with both Cartesian and spherical coordinate systems, validating the independent handling of X and Y propagation components. Spherical propagation tests validate the metric terms and coordinate transformations required for global and regional models using latitude-longitude grids. Curvilinear grid tests validate the arbitrary grid spacing and coordinate transformations used in regional models with complex coastlines. Unstructured grid tests validate the finite element approach for arbitrary mesh geometries including harbors and complex coastal features. SMC grid tests validate the multi-resolution nested cell approach for efficient global-to-coastal modeling.

Advanced physical processes include the garden sprinkler effect validation for numerical artifacts in long-duration spherical propagations, wave-current interaction physics for tidal and current environments, reflection physics for harbor and coastal applications, bottom interaction and obstruction physics for complex bathymetry, and full physics packages including ST4 source term formulations. Additionally, the series validates infrastructure capabilities including boundary condition processing for nested models, data assimilation for forecast improvement, and comprehensive output post-processing for field and point outputs.

## Test Matrix

The following matrix provides a consolidated overview of all seventeen tp2.x tests, including their primary physics focus, grid configuration, spectral resolution, and computational parameters.

### Quick Reference Table

| Test | Grid Type | Grid Size | Resolution | Spectrum | dtxy (s) | Duration | Primary Physics |
|------|----------|-----------|------------|----------|----------|----------|-----------------|
| tp2.1 | RECT/CART | 43×43 | 10 km | 3×24 | 300 | 5 hours | 2-D Cartesian propagation |
| tp2.2 | RECT/SPHE | 360×180 | 1° × 1° | 3×4 | 3600 | 20 days | Half-globe spherical |
| tp2.2 | RECT/SPHE | 360×180 | 1° × 1° | 3×4 | 3600 | 20 days | Half-globe spherical |
| tp2.3 | RECT/SPHE | 360×180 | 1° × 1° | 30×24 | 3600 | 15 days | Garden Sprinkler Effect |
| tp2.4 | RECT/SPHE | 225×106 | 0.35° | 3×12 | 1100 | 48 hours | Spherical propagation |
| tp2.5 | CURV/SPHE | 361×361 | Variable | 3×12 | 550 | 12 hours | Arctic curvilinear |
| tp2.6 | UNST/SPHE | 111 nodes | Variable | 36×36 | 1 | 10 minutes | Unstructured + wind |
| tp2.7 | UNST/SPHE | 111 nodes | Variable | 32×24 | 200 | 12 hours | Unstructured + reflection |
| tp2.8 | RECT/SPHE | 103×119 | 1.5 km | 32×24 | 45 | 80 minutes | Brest with currents |
| tp2.9 | CURV/SPHE | 141×142 | Variable | 25×24 | 300 | 24 hours | Curvilinear + obstructions |
| tp2.10 | SMC/SPHE | 256×128 base | Variable | 25×24 | 60 | 6 hours | SMC multi-resolution grid |
| tp2.11 | CURV/SPHE | 121×121 | Variable | 25×24 | 300 | 24 hours | Curvilinear + ST4 physics |
| tp2.12 | RECT/SPHE | 720×311 | 0.5° | 50×36 | 1200 | 24 hours | Global 30-min + SMPL |
| tp2.13 | RECT/SPHE | Variable | Variable | 25×24 | TBD | TBD | Regional configuration |
| tp2.14 | RECT/SPHE | 225×106 | 0.35° | 3×12 | 1100 | 3 hours | Boundary conditions |
| tp2.15 | CURV/SPHE | 43×42 | 15 km | 40×36 | 450 | 6 hours | Space-time extremes |
| tp2.16 | RECT/SPHE | 200×200 | 1° | 25×24 | 300 | 24 hours | Data assimilation |
| tp2.17 | RECT/SPHE | 200×200 | 0.5° | 25×24 | 300 | 48 hours | Output post-processing |

### Grid Type Comparison Table

| Grid Type | Code | Tests | Description | Key Parameters |
|-----------|------|-------|-------------|-----------------|
| Rectilinear Cartesian | RECT/CART | tp2.1 | Regular X-Y grid in meters | sx, sy in meters |
| Rectilinear Spherical | RECT/SPHE | tp2.2, tp2.3, tp2.4, tp2.8, tp2.12, tp2.13, tp2.14, tp2.16, tp2.17 | Regular lat-lon grid | sx, sy in degrees |
| Curvilinear | CURV/SPHE | tp2.5, tp2.9, tp2.11, tp2.15 | Arbitrary curvilinear coordinates | Coordinate files (lon, lat) |
| Unstructured | UNST/SPHE | tp2.6, tp2.7 | Triangular finite element mesh | Mesh file (.msh) |
| Spherical Multi-Cell | SMC/SPHE | tp2.10 | Multi-resolution nested cells | Cell files |

### Closure Type Comparison

| Closure Type | Code | Tests | Application | Behavior |
|--------------|------|-------|-------------|----------|
| None | NONE | Most tests | Regional domains | Open boundaries |
| Simple | SMPL | tp2.2, tp2.12 | Global without poles | Periodic longitude |
| Tripole | TRPL | (not in tp2.x) | Global to poles | Fold at north pole |

### Component Usage Matrix

| Test | Shel | Grid | Bound | Namelists | Ounf | Ounp |
|------|------|------|-------|-----------|------|------|
| tp2.1 | ✓ | ✓ | - | ✓ | ✓ | - |
| tp2.2 | ✓ | ✓ | - | ✓ | ✓ | - |
| tp2.3 | ✓ | ✓ | - | ✓ | ✓ | - |
| tp2.4 | ✓ | ✓ | - | ✓ | ✓ | - |
| tp2.5 | ✓ | ✓ | - | ✓ | ✓ | - |
| tp2.6 | ✓ | ✓ | - | ✓ | ✓ | - |
| tp2.7 | ✓ | ✓ | - | ✓ | ✓ | - |
| tp2.8 | ✓ | ✓ | - | ✓ | ✓ | - |
| tp2.9 | ✓ | ✓ | - | ✓ | ✓ | - |
| tp2.10 | ✓ | ✓ | - | ✓ | ✓ | - |
| tp2.11 | ✓ | ✓ | - | ✓ | ✓ | - |
| tp2.12 | ✓ | ✓ | - | ✓ | - | - |
| tp2.13 | ✓ | ✓ | - | ✓ | ✓ | - |
| tp2.14 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| tp2.15 | ✓ | ✓ | - | ✓ | ✓ | ✓ |
| tp2.16 | ✓ | ✓ | - | ✓ | ✓ | ✓ |
| tp2.17 | ✓ | ✓ | - | ✓ | ✓ | ✓ |

## Test Details

### tp2.1: 2-D Propagation on Cartesian Grid

**Location:** `regtests/ww3_tp2.1/`  
**Reference:** [NOAA-EMC/WW3 tp2.1](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.1)  
**Duration:** 5 hours

The tp2.1 test validates pure two-dimensional wave propagation on a Cartesian grid without source terms. This test represents the fundamental two-dimensional extension of the tp1.x series, exercising simultaneous X and Y propagation with no complicating physics. Waves propagate from a point source in all directions, allowing straightforward comparison against analytical solutions for two-dimensional wave spreading and energy conservation.

The Cartesian grid uses 10-kilometer resolution with 43 points in each dimension, covering a 420-kilometer square domain. The coordinate system uses meters rather than degrees, avoiding spherical geometry effects while validating the core two-dimensional propagation algorithms. The grid employs simple closure (CLOS='NONE') since this is a regional domain test without periodic boundaries.

Key parameters include propagation flags enabling both X and Y components (flcx=True, flcy=True) with refraction and wavenumber shift disabled (flcth=False, flck=False) and all source terms disabled (flsou=False). The spectrum uses minimal resolution with 3 frequency bins and 24 directional bins, providing adequate characterization of the propagating wave field while maintaining computational efficiency. Timestep configuration follows standard guidelines with dtmax=900 seconds and dtxy=300 seconds, satisfying the three-to-one ratio for numerical stability.

The absence of source terms isolates propagation physics from wind input, dissipation, and nonlinear transfers. Validation focuses on two-dimensional energy spreading, absence of preferred directional artifacts, and conservation of total energy as the wave field expands radially from the source. This test establishes baseline confidence in the fundamental two-dimensional propagation capability before advancing to more complex geometries and physics.

### tp2.2: Half-Globe Spherical Propagation

**Location:** `regtests/ww3_tp2.2/`  
**Reference:** [NOAA-EMC/WW3 tp2.2](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.2)  
**Duration:** 20 days

The tp2.2 test validates two-dimensional wave propagation on a spherical grid covering the Northern Hemisphere from the equator to 60°N. This test exercises the spherical coordinate handling including metric terms for latitude-dependent grid spacing and the simple closure (SMPL) that provides periodicity in longitude. The spherical grid is essential for global and basin-scale wave modeling where Cartesian approximations introduce significant errors.

The grid configuration uses 1-degree resolution with 360 points in longitude (covering 360°) and 180 points in latitude (covering 60°N to 60°S). The simple closure wraps the eastern boundary to the western boundary, enabling continuous propagation across the date line without artificial boundary reflections. This configuration represents a simplified global model without the complexity of tripole closure at the poles.

Propagation flags enable full two-dimensional spherical propagation (flcx=True, flcy=True, flcth=True) while disabling source terms (flsou=False). The minimal 3×4 spectral resolution maintains computational tractability for the 20-day simulation while adequately characterizing the propagating wave field. Timestep configuration uses dtxy=3600 seconds with dtmax=3600 seconds, reflecting the coarser temporal resolution acceptable for basin-scale simulations.

Validation of tp2.2 focuses on energy conservation over multiple global circuits, correct handling of the spherical metric terms including latitude-dependent grid cell areas, and absence of boundary artifacts at the periodic longitude seam. This test establishes confidence in the fundamental spherical propagation capability that underlies all global and regional spherical grid simulations.

### tp2.3: Garden Sprinkler Effect Validation

**Location:** `regtests/ww3_tp2.3/`  
**Reference:** [NOAA-EMC/WW3 tp2.3](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.3)  
**Duration:** 15 days

The tp2.3 test validates the garden sprinkler effect (GSE), a numerical artifact that occurs in long-duration spherical wave propagation due to discrete spectral resolution. The GSE causes spurious energy transfer from low to high frequencies as waves propagate around the globe, artificially increasing high-frequency energy and degrading model accuracy for swell decay applications. This test uses high spectral resolution (30 frequencies, 24 directions) to adequately resolve the spectral evolution and validate that GSE effects remain within acceptable bounds.

The test configuration mirrors tp2.2 with a 360×180 spherical grid at 1-degree resolution but extends the duration to 15 days and increases spectral resolution substantially. The high-frequency resolution (30 bins from 0.04 Hz upward) captures the spectral evolution that manifests as GSE while the 24-direction resolution adequately characterizes directional spreading. This configuration tests WW3's ability to maintain spectral integrity over extended propagations characteristic of transoceanic swell decay.

The GSE manifests as spurious high-frequency energy generation that can be diagnosed by comparing spectral shapes at equivalent locations after different numbers of global circuits. Validation focuses on spectral shape preservation, absence of artificial high-frequency energy growth, and accurate representation of frequency-dependent group velocity for swell propagation. This test is critical for applications involving long-distance swell propagation from remote generation areas.

### tp2.4: Spherical Propagation Test

**Location:** `regtests/ww3_tp2.4/`  
**Reference:** [NOAA-EMC/WW3 tp2.4](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.4)  
**Duration:** 48 hours

The tp2.4 test provides a standard validation case for spherical grid propagation using a 225×106 grid covering the Western Pacific region. This test validates the basic spherical propagation capability at moderate resolution (0.35° grid spacing) with a regional focus. The configuration serves as a reference for many subsequent tests that build upon this grid configuration.

The grid spans approximately 80° longitude by 37° latitude, covering a substantial regional domain with realistic geographic extent. The 0.35° resolution (~35 km at mid-latitudes) represents typical operational regional model resolution. The regional focus (no simple or tripole closure) provides a standard configuration for validating propagation physics without the complexities of global periodicity or polar singularities.

Propagation configuration enables full two-dimensional propagation (flcx=True, flcy=True) with refraction (flcth=True) while maintaining no source terms (flsou=False). The 3×12 spectral resolution balances accuracy with computational efficiency for the 48-hour validation simulation. Timestep configuration uses dtxy=1100 seconds with dtmax=3300 seconds, satisfying standard timestep relationships.

This test serves as a baseline configuration for several subsequent tests including tp2.14 (boundary conditions) and provides reference output for validating spherical propagation in regional models. Validation focuses on propagation accuracy, absence of numerical artifacts, and correct handling of the spherical metric terms at mid-latitudes.

### tp2.5: Arctic Curvilinear Grid

**Location:** `regtests/ww3_tp2.5/`  
**Reference:** [NOAA-EMC/WW3 tp2.5](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.5)  
**Duration:** 12 hours

The tp2.5 test validates curvilinear grid handling using an Arctic region polar stereographic projection. Curvilinear grids allow arbitrary spacing and orientation of grid lines, enabling efficient resolution distribution for regional models with complex coastlines or specific area focus. The Arctic configuration tests the curvilinear implementation with a polar projection that introduces strong coordinate curvature.

The grid uses 361×361 points with variable spacing optimized for the polar stereographic projection. Coordinate files provide explicit longitude and latitude at each grid point, enabling arbitrary projection geometry. The curvilinear approach allows higher resolution near the pole of interest while maintaining computational efficiency through coarser spacing at greater distances.

Key curvilinear parameters include explicit coordinate reading from separate longitude and latitude files (CURV/IDLA1 format), polar stereographic projection parameters embedded in the coordinate definitions, and appropriate depth and mask files for the Arctic region. The configuration tests WW3's ability to handle arbitrary grid topologies beyond the rectilinear limitation.

Validation focuses on correct handling of coordinate transformations, proper calculation of metric terms for variable grid spacing, and accurate propagation across a non-orthogonal grid structure. This test is essential for regional models requiring complex grid geometries or variable resolution distributions.

### tp2.6: Unstructured Grid with Wind Forcing

**Location:** `regtests/ww3_tp2.6/`  
**Reference:** [NOAA-EMC/WW3 tp2.6](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.6)  
**Duration:** 10 minutes

The tp2.6 test validates unstructured triangular mesh handling using the Limón harbor, Costa Rica configuration. Unstructured grids provide maximum flexibility for coastal applications with complex shorelines, arbitrary refinement patterns, and harbor geometries that cannot be efficiently represented with structured grids. The Limón mesh represents a typical coastal application with harbor infrastructure and variable resolution.

The unstructured mesh uses 111 nodes forming triangular elements that adapt to the coastal geometry. Mesh files in standard format define node coordinates, connectivity, and element properties. The unstructured approach allows resolution refinement near the harbor entrance and along breakwaters while maintaining coarser resolution in deeper offshore areas.

The test enables homogeneous wind forcing (WINDS='H') at 8 m/s from 270° (westerly) to exercise source term interaction with the unstructured geometry. The short 10-minute duration focuses on wave generation and initial propagation rather than long-term evolution. Timestep configuration uses dtxy=1 second with dtmax=3 seconds, reflecting the fine resolution required for harbor-scale simulations.

Validation of tp2.6 focuses on correct unstructured mesh handling, proper wave propagation across arbitrary triangular elements, and accurate representation of wind-wave generation in a complex coastal geometry. This test establishes confidence in WW3's unstructured grid capability for coastal engineering and harbor applications.

### tp2.7: Unstructured Grid with Reflection Physics

**Location:** `regtests/ww3_tp2.7/`  
**Reference:** [NOAA-EMC/WW3 tp2.7](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.7)  
**Duration:** 12 hours

The tp2.7 test extends unstructured grid validation to include reflection physics (REF1 source term) for harbor applications. Reflection is critical for harbor simulations where wave energy reflects from breakwaters, seawalls, and harbor boundaries, creating standing wave patterns and resonance that affect vessel operations and harbor safety. The REF1 parameterization models wave reflection from arbitrary boundaries defined in the unstructured mesh.

The unstructured mesh uses the REF1 test configuration with boundaries explicitly defined for reflection treatment. The test validates that reflection coefficients are properly applied, wave energy reflects with correct phase and amplitude, and multiple reflections do not introduce numerical instabilities. The 12-hour duration allows wave fields to reach quasi-steady state with repeated reflections.

Propagation flags enable full physics (flcx=True, flcy=True, flcth=True, flck=True, flsou=True) with REF1 reflection explicitly configured. Spectral resolution increases to 32 frequencies and 24 directions for adequate characterization of the complex directional and frequency evolution under repeated reflections.

Validation focuses on reflection coefficient accuracy, proper treatment of oblique incidence, absence of energy accumulation artifacts, and correct phase relationships in standing wave patterns. This test is essential for operational harbor wave forecasting where reflection from harbor structures significantly impacts the internal wave climate.

### tp2.8: Regional Grid with Current Forcing

**Location:** `regtests/ww3_tp2.8/`  
**Reference:** [NOAA-EMC/WW3 tp2.8](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.8)  
**Duration:** 80 minutes

The tp2.8 test validates wave-current interaction physics using the Iroise region configuration offshore of Brittany, France. This region experiences strong tidal currents that significantly impact wave conditions, making it an important test case for operational wave forecasting in current-dominated environments. The configuration exercises the current forcing capability (CURRENTS='T') with realistic tidal current patterns.

The regional grid uses 103×119 points at approximately 1.5 km resolution, covering the Iroise Sea with its complex tidal dynamics. The spherical coordinate grid (CLOS='NONE') represents a typical regional configuration without periodic boundaries. Bathymetry files provide the realistic depth distribution that drives the current patterns and wave-current interactions.

The test enables both current forcing (CURRENTS='T') and homogeneous wind forcing (WINDS='H') to exercise combined forcing effects. The 80-minute duration spans several tidal cycles, allowing validation of current-induced wave modifications throughout the tidal period. Timestep configuration uses dtxy=45 seconds with dtmax=135 seconds, reflecting the fine resolution required for coastal current interactions.

Validation focuses on accurate representation of Doppler shifting, current-induced refraction, wave blocking and focusing effects, and proper interaction between wind generation and current modification. This test is critical for operational forecasting in tidally active coastal regions.

### tp2.9: Curvilinear Grid with Obstructions

**Location:** `regtests/ww3_tp2.9/`  
**Reference:** [NOAA-EMC/WW3 tp2.9](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.9)  
**Duration:** 24 hours

The tp2.9 test validates curvilinear grid handling with explicit obstruction files for complex bathymetric features. Obstructions represent sub-grid-scale features—such as islands, reefs, and shallow banks—that affect wave propagation but cannot be resolved at the model grid resolution. The test uses the quarter-annulus configuration with a central island and variable depth to exercise the obstruction physics.

The curvilinear grid uses 141×142 points with variable spacing optimized for the quarter-annulus geometry. Coordinate files provide explicit grid point locations while obstruction files define the sub-grid-scale features that block or attenuate wave energy. This configuration represents a typical application where complex bathymetry requires explicit obstruction treatment.

The test enables full propagation (flcx=True, flcy=True, flcth=True, flck=True) with source terms enabled (flsou=True). The 24-hour duration allows wave fields to adjust to the complex geometry and for obstruction effects to reach steady state. Spectral resolution uses 25 frequencies and 24 directions for adequate spectral characterization.

Validation focuses on correct application of obstruction transmission and reflection coefficients, proper handling of multiple obstructions, and accurate representation of wave sheltering behind islands and shallow features. This test is essential for regional models with complex coastal and island geometry.

### tp2.10: Spherical Multi-Cell (SMC) Grid

**Location:** `regtests/ww3_tp2.10/`  
**Reference:** [NOAA-EMC/WW3 tp2.10](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.10)  
**Duration:** 6 hours

The tp2.10 test validates Spherical Multi-Cell (SMC) grid handling for multi-resolution global-to-coastal modeling. SMC grids use nested rectangular cells that can be refined in specific regions while maintaining the global spherical structure. This approach provides efficient multi-resolution capability without the complexity of fully unstructured meshes, enabling global models with regional refinement.

The SMC configuration uses a Lake Erie test case with base grid of 256×128 cells at 0.02°×0.016° resolution (approximately 2 km). Cell files define the nested refinement structure, with smaller cells in the area of interest and coarser cells elsewhere. This demonstrates the SMC approach of localized refinement for coastal applications within global models.

The test enables full propagation (flcx=True, flcy=True, flcth=True, flck=True) without source terms (flsou=False). The 6-hour duration focuses on propagation accuracy across the SMC grid structure, particularly at refinement boundaries where cell sizes change. Spectral resolution uses 25 frequencies and 24 directions.

Validation focuses on correct handling of nested cell boundaries, proper energy transfer between cells of different sizes, accurate representation of propagation across resolution transitions, and computational efficiency of the SMC approach compared to uniform high-resolution grids.

### tp2.11: Curvilinear Grid with Full ST4 Physics

**Location:** `regtests/ww3_tp2.11/`  
**Reference:** [NOAA-EMC/WW3 tp2.11](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.11)  
**Duration:** 24 hours

The tp2.11 test combines curvilinear grid handling with the complete ST4 physics package, validating the integration of advanced source terms on non-rectilinear grids. The ST4 package (Ardhuin et al. 2010) represents the current state-of-the-art wave modeling physics, including wind input, nonlinear interactions, and dissipation processes. This test validates that advanced physics work correctly on curvilinear grids.

The curvilinear grid uses the same 121×121 quarter-annulus configuration as tp2.9 but with full physics enabled (flsou=True). The ST4 package is configured with SIN4 wind input, SNL4 nonlinear interactions, SDS4 whitecapping dissipation, and SBT bottom friction. The 24-hour duration allows full development of the wind-driven wave field.

Validation focuses on proper interaction between curvilinear grid metrics and source term calculations, correct application of ST4 physics parameterizations, accurate representation of wind-wave growth and decay on non-uniform grids, and stable long-term integration with full physics. This test represents a realistic operational configuration for regional wave forecasting.

### tp2.12: Global 30-Minute Grid with Simple Closure

**Location:** `regtests/ww3_tp2.12/`  
**Reference:** [NOAA-EMC/WW3 tp2.12](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.12)  
**Duration:** 24 hours

The tp2.12 test validates global wave modeling on a 30-minute (0.5°) resolution grid with simple periodic closure. This configuration represents a typical global wave forecasting setup with moderate resolution suitable for operational applications. The simple closure (SMPL) enables global coverage without tripole complications by limiting the domain to ±77.5° latitude.

The global grid uses 720×311 points with 0.5° spacing in both directions, covering longitude 0° to 360° and latitude -77.5° to +77.5°. The SMPL closure wraps the eastern boundary (i=NX+1) to the western boundary (i=1), providing continuous propagation in longitude. This configuration tests global model capability without the polar singularities that require tripole closure.

The test enables full propagation (flcx=True, flcy=True, flcth=True) without source terms (flsou=False). The 50×36 spectral resolution provides adequate characterization for global applications. Timestep configuration uses dtxy=1200 seconds with dtmax=3600 seconds, reflecting the coarse grid resolution.

Validation focuses on correct simple closure implementation, proper global energy distribution, absence of artifacts at the periodic boundary, and accurate representation of basin-scale propagation patterns. This test establishes confidence in global wave modeling capability.

### tp2.13: Regional Configuration Test

**Location:** `regtests/ww3_tp2.13/`  
**Reference:** [NOAA-EMC/WW3 tp2.13](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.13)  
**Duration:** Variable

The tp2.13 test provides a standard regional model configuration for validation of regional wave modeling workflows. This test serves as a reference configuration for developing and testing regional model setups, including typical resolution ranges, spectral configurations, and output requirements for operational applications.

The regional grid uses appropriate resolution for the chosen domain (typically 10-25 km) with full physics enabled. The test validates the complete regional modeling workflow from grid generation through output processing. Configuration details vary based on the specific regional application being validated.

This test establishes baseline configurations that can be adapted for specific regional applications. Validation focuses on configuration correctness, appropriate parameter selection, and proper workflow execution for regional wave modeling.

### tp2.14: Boundary Conditions Test

**Location:** `regtests/ww3_tp2.14/`  
**Reference:** [NOAA-EMC/WW3 tp2.14](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.14)  
**Duration:** 3 hours

The tp2.14 test validates boundary condition handling using the Bound component for spectral boundary forcing. Nested regional models require boundary conditions from larger-scale models to provide wave forcing at open boundaries. This test validates the complete boundary condition workflow including preprocessing with ww3_bound and application in ww3_shel.

The test uses the same 225×106 grid as tp2.4 but enables the Bound component to read spectral boundary data from netCDF files. The boundary data provides spectral information at the grid edges that propagates inward during the simulation. The 3-hour duration demonstrates boundary-driven wave development without requiring extended simulation.

The Bound component is configured with READ mode to process boundary data files (interp=2, verbose=1). The test validates boundary data reading, temporal interpolation, spatial application, and proper integration with the main model. No internal source terms (flsou=False) isolate boundary forcing effects.

Validation focuses on correct boundary data application, proper wave propagation from boundaries, accurate representation of spectral characteristics, and stable integration with the main model. This test is essential for nested modeling applications.

### tp2.15: Space-Time Extremes Parameters

**Location:** `regtests/ww3_tp2.15/`  
**Reference:** [NOAA-EMC/WW3 tp2.15](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.15)  
**Duration:** 6 hours

The tp2.15 test validates space-time extremes (STE) parameter calculations for wave climate assessment and extreme event analysis. STE parameters describe maximum wave characteristics within specified spatial and temporal windows, including maximum surface elevation (MXE), maximum wave height (MXH), and associated statistics. The test uses the Adriatic Sea configuration near the ISMAR Acqua Alta platform.

The curvilinear grid uses 43×42 points at 15 km resolution with Lambert conformal projection appropriate for the Adriatic region. STE output is enabled with parameters including MXE, MXES, MXH, MXHC, SDMH, and SDMHC. The 6-hour duration provides adequate data for STE calculation while maintaining computational efficiency.

Validation focuses on correct STE calculation algorithms, proper statistical treatment, accurate maximum value identification, and appropriate output format. This test supports applications including extreme wave analysis, coastal engineering design, and risk assessment.

### tp2.16: Data Assimilation Test

**Location:** `regtests/ww3_tp2.16/`  
**Reference:** [NOAA-EMC/WW3 tp2.16](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.16)  
**Duration:** 24 hours

The tp2.16 test validates data assimilation capabilities for forecast improvement through incorporation of observations. Data assimilation combines model forecasts with real measurements to produce improved initial conditions for subsequent forecasts. The test validates mean wave parameter assimilation (MEAN='T') using synthetic observation data.

The rectangular grid uses 200×200 points at 1° resolution, providing a large enough domain to demonstrate assimilation effects. The test disables source terms (flsou=False) to isolate assimilation impacts from physical processes. The 24-hour duration allows demonstration of multiple assimilation cycles.

The InputAssim namelist enables mean parameter assimilation with 1D and 2D spectrum assimilation disabled (SPEC1D='F', SPEC2D='F'). This focuses validation on the core mean parameter assimilation functionality used in operational forecasting systems.

Validation focuses on correct observation ingestion, proper state updates, accurate analysis increments, and stable integration with the model. This test supports operational forecast improvement applications.

### tp2.17: Output Post-Processing Test

**Location:** `regtests/ww3_tp2.17/`  
**Reference:** [NOAA-EMC/WW3 tp2.17](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.17)  
**Duration:** 48 hours

The tp2.17 test validates comprehensive output post-processing capabilities including both field (Ounf) and point (Ounp) output components. This test demonstrates the complete output workflow from model restart files through post-processing executables to final analysis-ready NetCDF files. The 200×200 nested domain at 0.5° resolution provides sufficient complexity for comprehensive output validation.

The Ounf component configures field output with 1-hour interval, NetCDF4 format, and 12 wave parameters including HS, T02, T01, FP, DIR, SPR, DP, PHS, PTP, PDIR, WND, and CUR. Partition output separates wind sea and swell components. The Ounp component configures point output at 30-minute intervals for time series at specified locations.

Validation focuses on correct output file generation, proper NetCDF structure and metadata, accurate variable values, appropriate temporal and spatial resolution, and partition separation accuracy. This test supports all applications requiring model output for analysis, visualization, and delivery.

## Grid Type Comparison

### Rectilinear Cartesian (RECT/CART)

Rectilinear Cartesian grids use uniform spacing in X and Y directions measured in meters. These grids are appropriate for small-scale coastal applications where spherical effects are negligible and Cartesian geometry simplifies the mathematics. Key characteristics include uniform cell areas (simplifying conservation calculations), simple neighbor relationships (easy propagation schemes), and straightforward boundary handling. Configuration requires sx (X spacing in meters), sy (Y spacing in meters), x0 (X origin), and y0 (Y origin). Tests: tp2.1.

### Rectilinear Spherical (RECT/SPHE)

Rectilinear spherical grids use uniform spacing in longitude and latitude with spacing measured in degrees. These grids are appropriate for regional to global applications where spherical geometry must be included. Key characteristics include latitude-dependent cell areas (polar cells smaller than equatorial), convergence of meridians toward poles, and periodic longitude boundaries. Configuration requires sx (longitude spacing in degrees), sy (latitude spacing in degrees), x0 (longitude origin), and y0 (latitude origin). Tests: tp2.2, tp2.3, tp2.4, tp2.8, tp2.12, tp2.13, tp2.14, tp2.16, tp2.17.

### Curvilinear (CURV/SPHE)

Curvilinear grids use arbitrary grid point distributions defined by explicit coordinate files. These grids are appropriate for regional applications requiring complex grid geometries, variable resolution, or specialized projections. Key characteristics include arbitrary grid point locations, arbitrary spacing distributions, and arbitrary orientation. Configuration requires separate longitude and latitude coordinate files with appropriate format specifications. Tests: tp2.5, tp2.9, tp2.11, tp2.15.

### Unstructured (UNST/SPHE)

Unstructured grids use triangular finite element meshes that can conform to arbitrary coastal geometries. These grids are appropriate for harbor applications, coastal engineering, and anywhere maximum flexibility is required. Key characteristics include triangular elements, arbitrary connectivity, and arbitrary refinement patterns. Configuration requires mesh file (.msh format) defining nodes, elements, and boundaries. Tests: tp2.6, tp2.7.

### Spherical Multi-Cell (SMC)

Spherical Multi-Cell grids use nested rectangular cells with variable sizes for efficient multi-resolution global modeling. These grids are appropriate for global models requiring regional refinement without unstructured mesh complexity. Key characteristics include rectangular cells (simpler than triangles), hierarchical refinement, and global coverage. Configuration requires cell files defining the nested structure and refinement levels. Tests: tp2.10.

## Physics Descriptions

### Two-Dimensional Propagation

Two-dimensional propagation in WW3 describes the simultaneous evolution of the directional wave spectrum in both horizontal dimensions according to the wave action conservation equation. Unlike one-dimensional tests that propagate energy along a single axis, two-dimensional tests capture the full spatial evolution including spreading, directional shifts, and wave interactions across the grid. The propagation terms move energy across the computational grid based on local group velocities in both dimensions, with spherical metric terms accounting for latitude-dependent geometry in global applications.

The propagation schemes available in WW3 include first-order upwind (UG/UC), higher-order upwind (UCK), and least-squares (ULV) approaches with different accuracy and computational cost tradeoffs. The timestep constraints follow the Courant-Friedrichs-Lewy (CFL) condition requiring dtxy ≤ dx/c_max where dx is grid spacing and c_max is maximum phase speed. For spherical grids, additional metric terms account for the convergence of meridians and latitude-dependent cell areas.

### Spherical Geometry Effects

Spherical geometry introduces several effects not present in Cartesian modeling. The metric terms account for latitude-dependent grid cell sizes, with cells near the poles much smaller than those at the equator. The Coriolis parameter varies with latitude, affecting wave-current interactions and wave evolution. Wave rays converge toward the poles, causing energy accumulation that must be properly treated to avoid instability. The garden sprinkler effect represents a numerical artifact arising from discrete spectral resolution that causes spurious high-frequency energy generation during long propagations.

### Garden Sprinkler Effect (GSE)

The garden sprinkler effect manifests as spurious energy transfer from low to high frequencies during long-distance wave propagation on spherical grids. As waves propagate around the globe, slight mismatches between exact group velocities and discrete propagation steps cause energy to leak from spectral bins to neighboring bins, preferentially toward higher frequencies. This effect becomes significant for transoceanic swell propagation lasting multiple days.

Mitigation strategies include using sufficiently high frequency resolution (30+ frequency bins), proper timestep selection, and higher-order propagation schemes. The tp2.3 test specifically validates GSE behavior to ensure model accuracy for swell decay applications.

### Wave-Current Interaction

Wave-current interaction modifies wave properties through momentum exchange with ambient currents. Waves propagating with (against) the current experience apparent frequency increase (decrease) through Doppler shifting, while relative group velocity decreases (increases) relative to the ground frame. Strong opposing currents can cause wave blocking where group velocity relative to the ground approaches zero, leading to energy accumulation upstream.

The wavenumber shift scheme (flck=True) handles current interaction by tracking changes in wavenumber magnitude due to current velocity. The test tp2.8 validates this physics using realistic tidal currents in the Iroise Sea region.

### Reflection Physics (REF1)

Reflection physics models wave energy reflection from coastal structures, breakwaters, and shorelines. The REF1 source term assigns reflection coefficients to grid boundaries, partial reflection coefficients to specified areas, and models the resulting standing wave patterns and resonance. This physics is essential for harbor applications where reflected waves significantly impact internal wave conditions.

The REF1 parameterization includes options for specular (mirror) reflection, diffuse scattering, and mixed reflection types. Reflection coefficients can be spatially varying based on bottom depth or specified obstruction files.

### ST4 Physics Package

The ST4 physics package (Ardhuin et al. 2010) represents the current state-of-the-art wave modeling source terms including wind input (SIN4), nonlinear interactions (SNL4), and dissipation (SDS4, SBT). ST4 provides improved accuracy for wind-wave growth, swell decay, and dissipation compared to earlier physics packages.

Key features include the wind input saturation source term for high wind conditions, discrete interaction approximation for four-wave nonlinear interactions, and depth-limited bottom friction dissipation. The tp2.11 test validates ST4 on curvilinear grids.

### Space-Time Extremes (STE)

Space-time extremes parameters describe maximum wave characteristics within specified spatial and temporal windows. These parameters support extreme wave analysis, coastal engineering design, and risk assessment applications. The STE algorithm tracks maximum values over sliding windows in space and time, computing both maximum values and their statistical moments.

Output parameters include maximum surface elevation (MXE), maximum wave height (MXH), and associated standard deviation measures. The tp2.15 test validates STE calculation using the Adriatic Sea configuration.

### Data Assimilation

Data assimilation combines model forecasts with observations to produce improved initial conditions for subsequent forecasts. WW3 supports mean parameter assimilation (HS, T02, DIR), 1D spectrum assimilation, and 2D spectrum assimilation. The assimilation uses optimal interpolation to blend forecast and observation values based on their respective error estimates.

Assimilation improves forecast accuracy by correcting systematic biases and incorporating real-time measurements. The tp2.16 test validates mean parameter assimilation capability.

## Parameter Reference

### Grid Configuration Parameters

| Parameter | Description | Typical Values | Tests |
|-----------|-------------|----------------|-------|
| nx | Grid points in X | 43-720 | All RECT |
| ny | Grid points in Y | 3-311 | All RECT |
| sx | X spacing | 0.02°-10000 m | Depends on coord |
| sy | Y spacing | 0.016°-10000 m | Depends on coord |
| x0 | X origin | -180° to 0° | Test dependent |
| y0 | Y origin | -77.5° to 50° | Test dependent |
| coord | Coordinate system | CART, SPHE | Depends on grid |
| type | Grid type | RECT, CURV, UNST, SMC | Grid dependent |
| clos | Closure type | NONE, SMPL, TRPL | Regional vs global |
| zlim | Land mask limit | -5.0 to -0.1 m | Defines wet/dry |
| dmin | Minimum depth | 0.1-10.0 m | Defines model domain |

### Spectral Configuration Parameters

| Parameter | Description | Typical Values | Tests |
|-----------|-------------|----------------|-------|
| xfr | Frequency ratio | 1.07-1.25 | All |
| freq1 | Starting frequency | 0.035-0.05 Hz | Depends on physics |
| nk | Number of frequencies | 3-50 | Resolution level |
| nth | Number of directions | 4-36 | Resolution level |
| thoff | Directional offset | 0.0-0.5° | Test dependent |

### Propagation Flags

| Flag | Description | Effect When True |
|------|-------------|------------------|
| flcx | X-propagation | Enables zonal propagation |
| flcy | Y-propagation | Enables meridional propagation |
| flcth | Theta-shift | Enables spectral refraction |
| flck | Wavenumber shift | Enables current interaction |
| flsou | Source terms | Enables all source/sink terms |

### Timestep Parameters

| Parameter | Description | Constraint | Typical Ratio |
|-----------|-------------|-------------|---------------|
| dtmax | Maximum timestep | Must satisfy CFL | 3× dtxy |
| dtxy | Propagation timestep | CFL limited | 1× base unit |
| dtkth | Refraction timestep | dtmax/10 ≤ dtkth ≤ dtmax/2 | dtmax/2 |
| dtmin | Minimum timestep | ≥ 5 s validation | Fixed minimum |

## Usage

### Running Individual Tests

Each tp2.x test can be executed independently using the provided Python configuration scripts. The scripts generate all necessary WW3 namelist files and can optionally launch model execution when WW3 binaries are available.

```bash
# Navigate to the test directory
cd regtests/ww3_tp2.1

# Generate configuration files
python rompy_ww3_tp2_1.py

# Generated files are placed in rompy_runs/
ls -la rompy_runs/ww3_tp2_1_regression/
```

### Download Input Data

Most tp2.x tests require input data files that must be downloaded from the NOAA-EMC WW3 repository. The rompy-ww3 package provides a download script to automate this process.

```bash
# Download input data for a specific test
python regtests/download_input_data.py tp2.1

# Download input data for all tp2.x tests
python regtests/download_input_data.py tp2

# Download all regression test input data
python regtests/download_input_data.py --all
```

### Configuration Overview

Each test generates namelist files depending on the components used:

| File | Component | Tests | Purpose |
|------|-----------|-------|---------|
| ww3_shel.nml | Shel | All | Shell configuration |
| ww3_grid.nml | Grid | All | Grid preprocessing |
| ww3_bound.nml | Bound | tp2.14 | Boundary conditions |
| namelists.nml | Namelists | All | Physics parameters |
| ww3_ounf.nml | Ounf | Most | Field output |
| ww3_ounp.nml | Ounp | Some | Point output |

### Running with WW3

After generating configurations, execute the WW3 model using the appropriate backend. rompy-ww3 supports local execution (requires WW3 binaries in PATH) and Docker-based execution.

```bash
# Local execution (requires WW3 installation)
cd rompy_runs/ww3_tp2_1_regression
ww3_shel ww3_shel.nml

# Docker-based execution (requires Docker)
# Configure backend in rompy_ww3.yaml
```

### Validation Approach

The tp2.x tests provide reference outputs for validation of WW3 implementations. Compare generated outputs against expected results using appropriate metrics.

```python
import numpy as np
import xarray as xr

# Load expected and generated outputs
expected = xr.open_dataset("expected_output.nc")
generated = xr.open_dataset("generated_output.nc")

# Calculate error metrics
hs_error = np.sqrt(np.mean((generated.HS - expected.HS)**2))
print(f"HS RMSE: {hs_error:.4f} m")

# Calculate correlation coefficient
correlation = np.corrcoef(expected.HS.values.flatten(), 
                          generated.HS.values.flatten())[0,1]
print(f"HS Correlation: {correlation:.4f}")
```

### Common Issues

**Missing input files:** Ensure data has been downloaded before running tests. Use the download script to retrieve required files from the WW3 repository.

**Timestep violations:** WW3 validates timestep relationships according to dtmax ≈ 3×dtxy and dtmax/10 ≤ dtkth ≤ dtmax/2. Adjust timesteps if validation errors occur.

**Coordinate system mismatches:** Ensure grid coordinates match the intended coordinate system (CART for meters, SPHE for degrees). Incorrect coordinate settings cause grid misalignment.

**Unstructured mesh errors:** Verify mesh file format and coordinate ordering. Unstructured grids require specific element connectivity formats.

## References

### Primary WW3 Documentation

- WAVEWATCH III User Guide: https://ww3-docs.readthedocs.io/
- WW3 GitHub Repository: https://github.com/NOAA-EMC/WW3
- WW3 Regression Tests: https://github.com/NOAA-EMC/WW3/tree/develop/regtests

### Scientific References

- Ardhuin, F., et al. (2010). "Semi-empirical dissipation source functions for wind-wave models." J. Phys. Oceanogr.
- Battjes, J.A., and Janssen, J.P.F.M. (1978). "Energy loss and set-up due to breaking of random waves." Proc. 16th Coastal Engineering Conference.
- Beji, S., and Battjes, J.A. (1993). "Experimental investigation of wave propagation over a bar." Coastal Engineering.
- Hasselmann, S., et al. (1985). "Measurements of wind-wave growth and swell decay during the Joint North Sea Wave Project (JONSWAP)." Ergänzungsheft.
- Warner, J.C., and Hsu, S.A. (2009). "Wave breaking and setup at a barred beach." Coastal Engineering.

### rompy-ww3 Documentation

- rompy-ww3 README: https://github.com/rom-py/rompy-ww3
- rompy Framework: https://github.com/rom-py/rompy
- Examples: https://github.com/rom-py/rompy-ww3/tree/main/examples

## Appendix A: Test Directory Structure

```
regtests/
├── ww3_tp2.x/
│   ├── README.md                    # This documentation
│   ├── ww3_tp2.1/
│   │   ├── input/                   # Input data files
│   │   │   ├── 2-D.depth
│   │   │   └── points.list
│   │   ├── rompy_runs/              # Generated outputs
│   │   ├── rompy_ww3_tp2_1.py       # Configuration script
│   │   └── rompy_ww3_tp2_1.yaml      # YAML configuration
│   ├── ww3_tp2.2/
│   │   └── ...
│   └── ...
├── download_input_data.py            # Data download script
└── INPUT_DATA.md                    # Input file documentation
```

## Appendix B: Grid Type Selection Guide

### When to Use Rectilinear Cartesian

- Small-scale coastal applications (< 100 km)
- Harbor and inlet studies
- Laboratory-scale simulations
- When spherical effects are negligible

### When to Use Rectilinear Spherical

- Regional models (100-10000 km)
- Global models without polar coverage
- Operational forecasting systems
- When simple periodic boundaries are acceptable

### When to Use Curvilinear

- Regional models requiring variable resolution
- Complex coastal geometries
- Polar stereographic projections
- Optimized resolution distribution

### When to Use Unstructured

- Harbor applications with complex boundaries
- Coastal engineering with arbitrary geometries
- Maximum flexibility required
- When other grid types cannot represent the domain

### When to Use SMC

- Global models requiring regional refinement
- Efficient multi-resolution without unstructured complexity
- Nested global-to-coastal applications
- When computational efficiency is critical

## Appendix C: Validation Criteria

### Numerical Accuracy Targets

| Quantity | Target Tolerance | Notes |
|----------|------------------|-------|
| Energy conservation | < 2% loss over domain transit | Tests without source terms |
| Propagation accuracy | < 1 grid point error | Analytical solutions |
| Garden sprinkler effect | < 5% high-frequency growth | tp2.3 validation |
| Reflection accuracy | < 5% vs analytical | REF1 tests |
| Boundary accuracy | < 5% vs boundary data | tp2.14 validation |
| STE parameters | < 10% vs reference | tp2.15 validation |

### Performance Expectations

| Test | Computational Time | Hardware Reference |
|------|-------------------|-------------------|
| tp2.1 | ~1 minute | Single core, 2+ GHz |
| tp2.6 | ~5 minutes | Single core, 2+ GHz |
| tp2.10 | ~10 minutes | Single core, 2+ GHz |
| tp2.12 | ~30 minutes | Single core, 2+ GHz |

Times are approximate and scale with hardware performance. Tests with finer timesteps (tp2.6, tp2.7) and higher resolution (tp2.10, tp2.12) require proportionally more compute time.

---

*Documentation generated for rompy-ww3 v0.1.0*  
*Compatible with WAVEWATCH III v6.07.1*
