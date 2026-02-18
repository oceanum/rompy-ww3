# WW3 tp1.x Test Series Documentation

## Overview

The WW3 tp1.x test series constitutes the foundational validation suite for WAVEWATCH III (WW3) one-dimensional wave propagation physics. This comprehensive collection of ten regression tests systematically validates the core numerical and physical processes that govern wave behavior in oceanic and coastal environments. Each test isolates specific physical mechanisms—including pure propagation, shoaling, refraction, wave-current interactions, and nonlinear triad interactions—to ensure accurate wave simulation across diverse conditions.

The tp1.x series serves as the entry point for WW3 model validation, establishing baseline confidence in fundamental wave transformation processes before advancing to more complex two-dimensional and multi-grid configurations. These tests employ simplified one-dimensional domains that isolate individual physics while minimizing computational requirements, enabling rapid validation of model implementations and numerical changes.

The rompy-ww3 plugin provides complete configuration support for all tp1.x tests through its component-based architecture. Each test includes pre-configured Python scripts that generate all necessary WW3 namelist files, including shell configuration (ww3_shel.nml), grid preprocessing (ww3_grid.nml), physics parameters (namelists.nml), and output configuration (ww3_ounf.nml). This standardized approach ensures reproducibility and facilitates integration with automated testing frameworks.

### Test Series Objectives

The tp1.x test series accomplishes several critical objectives for WW3 model validation. First, it verifies the correct implementation of wave propagation mathematics, including dispersion relation accuracy and numerical advection schemes. Second, it validates depth-dependent transformation processes such as shoaling coefficients and refraction patterns. Third, it exercises source term implementations including wave-current interactions, breaking dissipation, and nonlinear energy transfers. Finally, it provides reference outputs that enable detection of regressions during model development and maintenance.

Each test targets a specific physical process or combination of processes, allowing developers to pinpoint the source of discrepancies when model behavior deviates from expectations. The isolated nature of these tests simplifies debugging by eliminating competing physical mechanisms that could mask underlying issues. This modular validation approach has proven essential for maintaining WW3 code quality throughout its development history.

### Physical Processes Covered

The ten tests in the tp1.x series comprehensively cover the essential physical processes governing wave evolution in the coastal ocean. Pure propagation tests establish baseline numerical accuracy without the complicating effects of forcing or depth variation. Shoaling tests verify depth-limited wave transformation according to linear wave theory. Refraction tests validate directional spectral evolution due to depth gradients and current shear. Wave-current interaction tests examine momentum exchange between waves and ambient currents. Dissipation tests evaluate energy loss through depth-limited breaking. Nonlinear tests address triad interactions that transfer energy between spectral components. Bottom scattering tests validate energy redistribution due to seabed interactions.

These processes represent the building blocks of more complex wave climate simulations. Accurate representation of individual processes ensures reliable predictions when processes interact in realistic scenarios. The tp1.x series thus provides essential validation that supports confidence in operational wave forecasting and scientific wave research applications.

## Test Matrix

The following matrix provides a consolidated overview of all ten tp1.x tests, including their primary physics focus, grid configuration, spectral resolution, and computational parameters.

### Quick Reference Table

| Test | Grid (nx×ny) | Resolution | Spectrum | dtxy (s) | Duration | Primary Physics |
|------|-------------|------------|----------|----------|----------|-----------------|
| tp1.1 | 360×3 | 1° × 1° (SPHE) | 3×4 | 3600 | 24 days | Zonal propagation |
| tp1.2 | 3×123 | 1° × 1° (SPHE) | 3×4 | 3600 | 6 days | Meridional propagation |
| tp1.3 | 43×3 | 15 km × 15 km (CART) | 3×4 | 1200 | 2 days | Monochromatic shoaling |
| tp1.4 | 13×3 | 5 km × 5 km (CART) | 3×24 | 300 | 12 hours | Spectral refraction (X) |
| tp1.5 | 3×13 | 5 km × 5 km (CART) | 3×24 | 300 | 12 hours | Spectral refraction (Y) |
| tp1.6 | 22×3 | 3 km × 3 km (CART) | 15×8 | 600 | 10 days | Wave blocking (currents) |
| tp1.7 | 29×3 | 0.02° × 0.1° (SPHE) | 30×24 | 5 | 6 hours | IG wave generation |
| tp1.8 | 52×3 | 20 m × 20 m (CART) | 30×90 | 0.25 | 100 seconds | Wave breaking (beach) |
| tp1.9 | 303×3 | 0.1 m × 0.1 m (CART) | 35×180 | 0.01 | 5 seconds | Triad interactions |
| tp1.10 | 51×3 | 2 km × 2 km (CART) | 24×120 | 80 | 18 hours | Bottom scattering |

### Source Terms Configuration

| Test | Wind | Currents | Breaking | Triads | Scattering | IG |
|------|------|----------|----------|--------|------------|----|
| tp1.1 | Off | Off | Off | Off | Off | Off |
| tp1.2 | Off | Off | Off | Off | Off | Off |
| tp1.3 | Off | Off | Off | Off | Off | Off |
| tp1.4 | Off | Off | Off | Off | Off | Off |
| tp1.5 | Off | Off | Off | Off | Off | Off |
| tp1.6 | Off | On | Off | Off | Off | Off |
| tp1.7 | On | Off | On | On | Off | On |
| tp1.8 | On | Off | On | Off | Off | Off |
| tp1.9 | On | Off | On | On | Off | Off |
| tp1.10 | On | Off | Off | Off | On | Off |

### Output Variables by Test

| Test | Standard Output | Point Output |
|------|----------------|--------------|
| tp1.1 | HS | Yes |
| tp1.2 | HS | Yes |
| tp1.3 | DPT, HS, FC, CFX | Yes |
| tp1.4 | HS, T01, DIR | Yes |
| tp1.5 | HS, T01, FP, DIR | Yes |
| tp1.6 | DPT, CUR, HS | Yes |
| tp1.7 | DPT, HS, T0M1, DIR, SPR, HIG, EF, P2L | Yes |
| tp1.8 | DPT, WND, WLV, HS, T02, DIR, SPR, TAW, TWO, BHD, SXY, FOC, USS, USF | Yes |
| tp1.9 | DPT, HS, T0M1 | Yes |
| tp1.10 | HS, DIR, SPR | Yes |

## Test Details

### tp1.1: Zonal Propagation Test

**Location:** `regtests/ww3_tp1.1/`  
**Reference:** [NOAA-EMC/WW3 tp1.1](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.1)  
**Duration:** 24 days

The tp1.1 test validates pure one-dimensional wave propagation along the equator on a spherical grid. This test represents the simplest WW3 configuration, exercising only the fundamental propagation mathematics without any source terms, forcing, or depth variation that might complicate interpretation of results. Waves propagate zonally (east-to-west) with no directional evolution, allowing straightforward comparison against analytical solutions.

The test domain spans 360 degrees of longitude at nearly equatorial latitude, providing a comprehensive validation of spherical coordinate handling. The grid uses 1-degree resolution in both dimensions, with 360 points in the propagation direction and 3 points transverse to flow. This transverse averaging eliminates any edge effects from lateral boundaries while maintaining computational efficiency.

Key parameters for tp1.1 include propagation flags set for zonal flow (flcx=True, flcy=False) with all other propagation components disabled (flcth=False, flck=False). The spectrum uses minimal resolution with 3 frequency bins and 4 directional bins, sufficient to characterize the propagating wave packet without excessive computational cost. Timestep configuration follows standard guidelines with dtmax approximately three times dtxy, ensuring numerical stability while maintaining temporal resolution adequate for the wave group.

The absence of source terms means all wave energy originates from initial conditions rather than continuous generation. This approach isolates propagation physics by eliminating wind input, dissipation, and nonlinear transfers that would otherwise complicate the energy balance. Validation focuses on energy conservation, phase speed accuracy, and absence of numerical artifacts during the 24-day simulation.

### tp1.2: Meridional Propagation Test

**Location:** `regtests/ww3_tp1.2/`  
**Reference:** [NOAA-EMC/WW3 tp1.2](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.2)  
**Duration:** 6 days

The tp1.2 test complements tp1.1 by examining meridional (north-south) propagation on a spherical grid. While tp1.1 validates zonal propagation and spherical longitude handling, tp1.2 exercises latitude propagation and the spherical coordinate metric terms that differ between dimensions. Together, these tests establish confidence in fundamental spherical propagation in all principal directions.

The grid configuration inverts tp1.1, using 123 points in latitude and only 3 points in longitude. This arrangement spans from -61° to +61° latitude, crossing both hemispheres and testing the model's treatment of the equator as a coordinate singularity. The shorter 6-day duration reflects the more limited longitudinal extent while still providing adequate time for energy to traverse the domain.

Propagation flags configure meridional flow (flcx=False, flcy=True) while disabling all other propagation components. The spectral configuration matches tp1.1 with 3 frequencies and 4 directions, and timestep settings remain consistent. This parameter alignment ensures that differences between tests reflect geometry changes rather than configuration variations.

Validation of tp1.2 focuses on symmetric treatment of northern and southern hemispheres, correct handling of convergence/divergence near the poleward boundaries, and preservation of energy as waves traverse varying Coriolis parameters. The spherical geometry introduces additional metric terms in meridional propagation that differ from the zonal case, making this test essential for comprehensive validation.

### tp1.3: Monochromatic Shoaling Test

**Location:** `regtests/ww3_tp1.3/`  
**Reference:** [NOAA-EMC/WW3 tp1.3](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.3)  
**Duration:** 2 days

The tp1.3 test validates one-dimensional monochromatic shoaling on a Cartesian grid, exercising the depth-dependent transformation processes that govern wave evolution in coastal waters. Unlike the pure propagation tests, tp1.3 includes depth variation that causes wave energy to shoal (increase in height and steepen) as waves propagate into shallower water. This process follows from linear wave theory and conservation of energy flux across depth contours.

The Cartesian grid uses 15-kilometer resolution with 43 points in the propagation direction, covering a domain with a sloping bottom that decreases depth from 200 meters to approximately 1 meter. This depth range spans the transition from deep water through intermediate depths to very shallow water where wave breaking eventually occurs. The wave spectrum uses 3 frequencies and 4 directions with a low starting frequency (0.08 Hz) appropriate for the shoaling test.

The PRO2 namelist parameter dtime=0.0 indicates a stationary wave field without time-dependent evolution, which isolates the shoaling transformation from any transient effects. Propagation flags enable X-direction propagation (flcx=True) while disabling all other processes. Timestep configuration uses dtxy=1200 seconds with dtmax=3600 seconds, following the standard three-to-one ratio for stability.

Validation of tp1.3 compares simulated shoaling coefficients against analytical predictions from linear wave theory. Key metrics include wave height increase as depth decreases, frequency downshift due to dispersion, and preservation of energy flux across the shoaling region. Accurate shoaling is essential for coastal wave predictions where waves approaching shore undergo substantial transformation before breaking.

### tp1.4: Spectral Refraction Test (X-Direction)

**Location:** `regtests/ww3_tp1.4/`  
**Reference:** [NOAA-EMC/WW3 tp1.4](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.4)  
**Duration:** 12 hours

The tp1.4 test examines one-dimensional spectral refraction in the X-direction, validating the angular (directional) evolution of wave spectra due to depth-dependent changes in wave speed. Refraction causes wave directions to bend toward normal to depth contours, redistributing energy across the directional spectrum without changing total energy. This process shapes coastal wave climates and determines which directions deliver energy to specific shorelines.

The test uses a Cartesian grid with 5-kilometer resolution and 13 points in the propagation direction. Depth contours run perpendicular to propagation, creating a depth gradient that induces refraction. The spectral configuration increases directional resolution to 24 directions while maintaining 3 frequencies, allowing detailed examination of directional redistribution.

The key parameter enabling refraction is flcth=True, which activates the theta-shift scheme for spectral refraction. This scheme tracks directional changes due to the depth-dependent dispersion relation without requiring full wavenumber integration. The dtxy timestep of 300 seconds with dtkth=150 seconds for the refraction component follows recommended guidelines that set refraction timesteps between dtmax/10 and dtmax/2 to prevent numerical artifacts.

Output variables include significant wave height (HS), mean period (T01), and mean direction (DIR), providing comprehensive characterization of the spectral evolution. Point output at 15-minute intervals enables detailed time series analysis of refraction-induced changes. Validation compares simulated directional spreading against analytical solutions for simplified depth profiles.

### tp1.5: Spectral Refraction Test (Y-Direction)

**Location:** `regtests/ww3_tp1.5/`  
**Reference:** [NOAA-EMC/WW3 tp1.5](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.5)  
**Duration:** 12 hours

The tp1.5 test parallels tp1.4 but examines Y-direction spectral refraction, validating refraction processes when propagation occurs perpendicular to the depth gradient orientation used in tp1.4. This complementary test ensures that the refraction implementation handles arbitrary grid orientations correctly, not just the specific configuration used in tp1.4.

Grid configuration inverts tp1.4 with 3 points in X and 13 points in Y, maintaining 5-kilometer resolution. The depth gradient now points in the X-direction while propagation proceeds in Y, reversing the relative geometry. This configuration tests the refraction implementation's handling of the coordinate transformations required to map depth gradients onto directional changes.

Propagation flags configure Y-direction flow (flcy=True, flcx=False) with refraction enabled (flcth=True). The spectral and timestep configurations match tp1.4, ensuring that differences between tests reflect geometry rather than parameter variations. Output variables expand slightly to include peak frequency (FP) in addition to HS, T01, and DIR.

Validation of tp1.5 confirms correct implementation of the general refraction equations for arbitrary grid orientations. Together with tp1.4, these tests establish confidence that refraction works correctly regardless of how the computational grid aligns with physical depth contours. This generality is essential for real-world applications where coastlines and depth gradients rarely align with model grid axes.

### tp1.6: Wave Blocking with Currents

**Location:** `regtests/ww3_tp1.6/`  
**Reference:** [NOAA-EMC/WW3 tp1.6](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.6)  
**Duration:** 10 days

The tp1.6 test validates wave-current interaction physics, specifically the wave blocking phenomenon that occurs when strong opposing currents reduce relative group velocity to zero. This process occurs in regions of strong adverse currents such as tidal rips, western boundary currents, and river plumes. Wave blocking causes energy accumulation upstream of the current jet and can dramatically alter wave conditions in coastal and oceanic environments.

The test domain spans 22 grid points in X at 3-kilometer resolution, with a current field that varies spatially to create a region of strong opposing flow. Waves propagating into the current experience Doppler shifting of frequency and wavenumber, with the group velocity decreasing as current speed increases. When current speed exceeds the intrinsic group velocity, waves cannot propagate upstream and instead accumulate, creating a region of elevated wave energy.

Key parameters include current forcing enabled through the input configuration (forcing: currents: T) and the wavenumber shift scheme activated (flck=True). The PRO4 namelist parameters rnfac=0.0 and rsfac=0.0 configure the refraction schemes for the current interaction test. The spectral configuration uses 15 frequencies and 8 directions, providing adequate resolution to characterize the blocking response across the wave spectrum.

Output variables include depth (DPT), current velocity (CUR), and significant wave height (HS), enabling visualization of the current field and the resulting wave response. The 10-day duration allows the wave field to reach quasi-steady state as energy accumulates in the blocking region. Validation compares simulated blocking characteristics against analytical solutions and laboratory measurements.

### tp1.7: Infragravity Wave Generation

**Location:** `regtests/ww3_tp1.7/`  
**Reference:** [NOAA-EMC/WW3 tp1.7](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.7)  
**Duration:** 6 hours

The tp1.7 test validates infragravity (IG) wave generation mechanisms, examining the transfer of energy from short wind waves to low-frequency IG motions through breaking and reflection processes. IG waves have periods of 30-300 seconds, longer than typical wind waves, and dominate wave motions in the inner surf zone. These long waves can propagate far onshore and significantly impact coastal circulation, sediment transport, and harbor operations.

The test uses a spherical grid with 29 points in longitude at 0.02-degree resolution, covering a coastal domain with a sloping beach. Depth decreases from approximately 100 meters offshore to shallow nearshore depths, providing the varying depth that drives IG wave generation through breakpoint forcing. The spectrum extends to very low frequencies (starting at 0.01 Hz) with 30 frequencies and 24 directions to capture the IG band.

The physics enabled for IG wave generation include breaking dissipation (DB1), reflection (REF1), and IG wave generation (IG1) source terms. All propagation components are active (flcx=True, flcy=True, flcth=True, flck=True) to allow full spectral evolution. The timestep configuration uses dtxy=5 seconds with dtmax=15 seconds, providing fine temporal resolution for the rapidly evolving breaking and IG processes.

Output variables are extensive, including depth, significant wave height, mean period (T0M1), direction, directional spreading, IG height (HIG), mean frequency, and second-lowest frequency moment (P2L). The 1-minute output interval captures the IG wave dynamics with adequate temporal resolution. Validation focuses on IG wave height and frequency content compared against laboratory measurements.

### tp1.8: Wave Breaking on Beach

**Location:** `regtests/ww3_tp1.8/`  
**Reference:** [NOAA-EMC/WW3 tp1.8](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.8)  
**Duration:** 100 seconds

The tp1.8 test validates depth-limited wave breaking physics on a natural beach profile, exercising the DB1 breaking dissipation source term and related parameterizations. Wave breaking represents the primary energy sink for wind-generated waves, determining the offshore wave climate that reaches beaches and structures. Accurate breaking parameterization is essential for coastal predictions and has been the subject of extensive research and model development.

The test domain uses a Cartesian grid with 20-meter resolution spanning a coastal profile with a gradually sloping beach. The 52-point domain extends from approximately 1000 meters offshore to the shoreline, with depth decreasing to zero at the beach face. The spectrum uses 30 frequencies from 0.04 Hz and 90 directions, providing high directional resolution to capture the complex breaking-induced directional evolution.

The timestep configuration employs very fine temporal resolution with dtxy=0.25 seconds and dtmax=0.75 seconds. This fine resolution reflects the demanding requirements of breaking simulations where rapid energy loss occurs over short spatial and temporal scales. The dtmin=5 seconds parameter satisfies validation constraints while allowing the necessary spatial resolution.

Output variables are comprehensive, including depth, wind speed, water level, significant wave height, mean period, direction, spreading, wind stress, radiation stress components (BHD, SXY), forces, and energy flux components (USS, USF). This extensive output enables detailed analysis of the energy balance and breaking dissipation. Validation compares modeled breaking characteristics against the Warner and Hsu (2009) laboratory experiments.

### tp1.9: Nonlinear Shoaling with Triads

**Location:** `regtests/ww3_tp1.9/`  
**Reference:** [NOAA-EMC/WW3 tp1.9](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.9)  
**Duration:** 5 seconds

The tp1.9 test validates triad interaction physics using the Beji and Battjes (1993) laboratory experiments on a barred laboratory flume. Triad interactions transfer energy between spectral components through second-order nonlinear processes that generate superharmonics (higher frequencies) and subharmonics (lower frequencies). These interactions are particularly important for wave transformation over complex bathymetry such as sand bars and ripples.

The laboratory-scale domain spans 303 points at 0.1-meter resolution, providing centimeter-scale resolution appropriate for the meter-scale laboratory experiments being simulated. The spectrum uses 35 frequencies starting at 0.10 Hz and 180 directions, offering exceptional directional resolution to capture the triad-induced spectral changes.

The TR1 source term enables triad interactions while breaking (DB1) is also active. Propagation flags enable X-direction propagation (flcx=True) with all other propagation components disabled (flcy=False, flcth=False, flck=False), isolating the triad physics from refraction and current interactions. Timestep configuration uses dtxy=0.01 seconds, reflecting the extremely fine temporal resolution required for laboratory-scale simulations.

Output variables include depth, significant wave height, and mean period (T0M1), with point output at 5-second intervals capturing the time evolution of the triad interactions. The very short 5-second duration provides adequate simulation time for nonlinear transfers to develop while remaining computationally efficient. Validation compares simulated energy transfer against the well-documented Beji and Battjes measurements.

### tp1.10: Bottom Scattering

**Location:** `regtests/ww3_tp1.10/`  
**Reference:** [NOAA-EMC/WW3 tp1.10](https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.10)  
**Duration:** 18 hours

The tp1.10 test validates bottom scattering physics using the BS1 source term, which models energy redistribution due to interactions with the seabed. Bottom scattering becomes significant in shallow water where the evanescent wave component extends to the seafloor and seabed roughness causes directional spreading and frequency changes. This process is particularly relevant for continental shelf environments where water depths range from tens to hundreds of meters.

The domain spans 51 points at 2-kilometer resolution, providing a 100-kilometer coastal domain with appropriate scale for shelf processes. The spectrum uses 24 frequencies from 0.04 Hz and 120 directions, offering high directional resolution to capture scattering-induced spreading.

The BS1 source term enables bottom scattering while propagation flags enable X-direction flow (flcx=True) with refraction disabled (flcth=False). The timestep configuration uses dtxy=80 seconds with dtmax=240 seconds, following standard guidelines for the moderate resolution domain. Boundary input at the western edge provides continuous wave forcing that scatters as it propagates eastward.

Output variables include significant wave height, mean direction, and directional spreading, enabling analysis of how bottom interactions modify the directional spectrum. Point output at 20-minute intervals captures the temporal evolution of the scattering process. Validation focuses on the development of directional spreading as waves traverse the domain.

## Physics Descriptions

### Wave Propagation Fundamentals

Wave propagation in WW3 describes the spatial and temporal evolution of the directional wave spectrum according to the wave action conservation equation. The directional spectrum F(σ,θ) represents energy density as a function of relative frequency σ and direction θ, with integration over all frequencies and directions yielding bulk wave parameters such as significant wave height and mean period. The propagation terms move energy across the computational grid based on the local dispersion relation and group velocity.

The dispersion relation connects wave properties (frequency, wavenumber, direction) to water depth and ambient currents. For intermediate depths where kh ≈ 1 (k is wavenumber, h is depth), the dispersion relation transitions from deep-water form (frequency proportional to wavenumber) to shallow-water form (frequency proportional to sqrt(depth)). This depth dependence drives refraction, shoaling, and other depth-limited processes that shape wave evolution.

WW3 employs several propagation schemes with different computational approaches. The first-order upwind scheme (UG/UC) provides computational efficiency with adequate accuracy for most applications. Higher-order schemes (UCK or ULV) offer improved accuracy for complex domains at increased computational cost. The timestep constraints for propagation follow the Courant-Friedrichs-Lewy (CFL) condition, requiring dtxy ≤ dx/c_max where dx is grid spacing and c_max is maximum phase speed.

### Shoaling and Refraction

Shoaling describes the depth-dependent change in wave properties as waves propagate from deep to shallow water. According to linear wave theory, wave energy flux remains constant in the absence of energy sources and sinks, requiring wave height to increase as group velocity decreases with decreasing depth. The shoaling coefficient relates to the ratio of group velocities at different depths, approaching infinity as depth approaches zero at the shoreline.

The shoaling coefficient K_s can be expressed as:

```
K_s = [c_g0 / c_g]^{1/2}
```

where c_g0 is the deep-water group velocity and c_g is the local group velocity. For sinusoidal waves, this yields K_s proportional to h^{-1/4} in shallow water. WW3 calculates shoaling analytically within the propagation scheme based on the local dispersion relation and depth.

Refraction describes the angular change in wave direction due to depth-dependent phase speed variation. Waves tend to bend toward regions of slower phase speed (shallower water), causing energy to converge on headlands and diverge in bays. The refraction coefficient K_r accounts for spatial convergence/divergence due to directional changes:

```
K_r = [cosθ0 / cosθ]^{1/2}
```

where θ0 is the deep-water direction and θ is the local direction. For straight parallel depth contours, this yields simple turning toward the normal without spatial focusing.

### Wave-Current Interaction

Wave-current interaction modifies wave properties through momentum exchange with ambient currents. Waves propagating with (against) the current experience apparent frequency increase (decrease) through Doppler shifting, while relative group velocity decreases (increases) relative to the ground frame. The relative frequency σ remains invariant in the absence of other processes:

```
σ = ω - k·U
```

where ω is absolute frequency, k is wavenumber vector, and U is current velocity vector.

Strong opposing currents can reduce relative group velocity to zero, causing wave blocking. The blocking condition occurs when U = -c_g, where c_g is intrinsic group velocity. Upstream of the blocking point, waves cannot propagate against the current and energy accumulates, potentially creating significant wave height increases. The wavenumber shift scheme (flck=True) in WW3 handles this physics by tracking the change in wavenumber magnitude due to current interaction.

### Wave Breaking and Dissipation

Wave breaking represents the primary energy sink for wind-generated waves in coastal environments. The DB1 source term in WW3 parameterizes depth-limited breaking based on the work of Battjes and Janssen (1978) and subsequent developments. The dissipation rate depends on the ratio of local significant wave height to the maximum allowable height based on local depth:

```
Q_b = (1 - H_rms / H_max)^p
```

where Q_b is the fraction of breaking waves, H_rms is root-mean-square wave height, H_max is the maximum stable wave height (typically 0.88h for random waves), and p is a calibration parameter. The dissipation rate scales with Q_b and the frequency-dependent energy density.

The WB1 parameterization adds depth-dependent whitecapping to the breaking dissipation, accounting for breaking not only at depth-limited locations but throughout the water column where wave steepness exceeds critical values. The transition from whitecapping to depth-limited breaking depends on the local ratio of wave height to depth.

### Nonlinear Wave Interactions

Nonlinear wave interactions transfer energy between spectral components through resonant and non-resonant wave-wave interactions. The dominant resonant interaction is the quartet interaction (four-wave process) that redistributes energy within the wind wave band according to the Hasselmann kinetic equation. Triad interactions (three-wave processes) transfer energy to higher and lower frequencies, particularly important in shallow water.

The triad interaction parameterization accounts for second-order nonlinear transfers between frequencies. The transfer rate depends on the product of three spectral components whose frequencies and wavenumbers satisfy the resonance conditions. In shallow water, triad interactions generate bound long waves (infragravity waves) that can become free waves after reflection from the shoreline.

WW3 implements triad interactions through the LTA (Lowe-Teixeira) approach, which solves the evolution equations for bispectral moments. This parameterization captures the essential triad physics including superharmonic generation (upshift to higher frequencies) and subharmonic generation (downshift to lower frequencies). The Beji and Battjes (1993) experiments provide benchmark validation for triad implementations.

### Bottom Scattering

Bottom scattering transfers wave energy between directions through interactions with seabed roughness features. The BS1 source term in WW3 parameterizes this process based on the头部理论 for Bragg scattering from sinusoidal bottom corrugations. The scattering coefficient depends on bottom roughness, water depth, and wave properties:

```
S_bs = α k^{-3} (k h)^{-4} |B(k_b)|^2 δ(σ - σ')
```

where α is a calibration coefficient, k_b is the bottom wavenumber, and B is the bottom roughness spectrum. Energy transfers preferentially to directions satisfying the Bragg resonance condition.

Bottom scattering becomes significant when the evanescent wave component extends to the seafloor, typically at depths less than approximately 10 times the significant wavelength. The process causes directional spreading and frequency shifting as waves propagate over rough bottoms. Continental shelf environments where water depths range from 20-200 meters exhibit notable scattering effects.

## Parameter Reference

### Grid Configuration Parameters

| Parameter | Description | Typical Values | Test Usage |
|-----------|-------------|----------------|------------|
| nx | Number of grid points in X | 3-360 | Varies by test |
| ny | Number of grid points in Y | 3-123 | Varies by test |
| sx | X-direction spacing | 0.01°-2000 m | Depends on coordinate |
| sy | Y-direction spacing | 0.01°-2000 m | Depends on coordinate |
| x0 | X-origin | -180° to 0° | Test dependent |
| y0 | Y-origin | -61° to -0.1° | Test dependent |
| coord | Coordinate system | CART, SPHE | Depends on domain |
| type | Grid type | RECT | All tests |
| clos | Closure type | NONE, SMPL | Depends on boundaries |
| zlim | Land mask limit | -5.0 to -98.0 m | Defines wet/dry |
| dmin | Minimum depth | 0.1-5.75 m | Defines model domain |

### Spectrum Configuration Parameters

| Parameter | Description | Typical Values | Test Usage |
|-----------|-------------|----------------|------------|
| xfr | Frequency ratio | 1.1-1.25 | Test dependent |
| freq1 | Starting frequency | 0.01-0.186 Hz | Depends on physics |
| nk | Number of frequencies | 3-35 | Resolution level |
| nth | Number of directions | 4-180 | Resolution level |
| thoff | Directional offset | 0.0° | All tests |

### Propagation Flags

| Flag | Description | Effect When True |
|------|-------------|------------------|
| flcx | X-propagation | Enables zonal propagation |
| flcy | Y-propagation | Enables meridional propagation |
| flcth | Theta-shift | Enables spectral refraction |
| flck | Wavenumber shift | Enables current interaction |
| flsou | Source terms | Enables all source/sink terms |
| fldry | Dry run | Tests without execution |

### Timestep Parameters

| Parameter | Description | Constraint | Typical Ratio |
|-----------|-------------|-------------|---------------|
| dtmax | Maximum timestep | Must satisfy CFL | 3× dtxy |
| dtxy | Propagation timestep | CFL limited | 1× base unit |
| dtkth | Refraction timestep | dtmax/10 ≤ dtkth ≤ dtmax/2 | dtmax/2 |
| dtmin | Minimum timestep | ≥ 5 s validation | Fixed minimum |

### Physics Parameters (namelists.nml)

| Parameter | Module | Description | Range |
|-----------|--------|-------------|-------|
| wdthcg | PRO3 | Directional spreading in propagation | 0.0-1.0 |
| wdthth | PRO3 | Angular resolution parameter | 0.0-1.0 |
| rnfac | PRO4 | Refraction coefficient | 0.0-1.0 |
| rsfac | PRO4 | Scattering coefficient | 0.0-1.0 |
| dtime | PRO2 | Time step for stationary calculations | 0.0 for stationary |

### Output Variables

| Variable | Description | Units |
|----------|-------------|-------|
| HS | Significant wave height | m |
| T01 | Mean period (first moment) | s |
| T02 | Mean period (second moment) | s |
| T0M1 | Mean period (inverse first moment) | s |
| FP | Peak frequency | Hz |
| DIR | Mean direction | ° |
| SPR | Directional spreading | ° |
| DPT | Water depth | m |
| CUR | Current speed | m/s |
| HIG | Infragravity wave height | m |
| WND | Wind speed | m/s |
| WLV | Water level | m |
| EF | Mean frequency | Hz |
| P2L | Second-lowest frequency moment | Hz |
| BHD | Radiation stress (xx) | N/m |
| SXY | Radiation stress (xy) | N/m |
| TAW | Wind stress | N/m |
| TWO | Total energy flux | W/m |
| FOC | Friction velocity | m/s |
| USS | Total sea state | m²/Hz |
| USF | Sea state flux | W/m |

## Usage

### Running Individual Tests

Each tp1.x test can be executed independently using the provided Python configuration scripts. The scripts generate all necessary WW3 namelist files and can optionally launch model execution when WW3 binaries are available.

```bash
# Navigate to the test directory
cd regtests/ww3_tp1.1

# Generate configuration files
python rompy_ww3_tp1_1.py

# Generated files are placed in rompy_runs/
ls -la rompy_runs/ww3_tp1_1_regression/
```

### Download Input Data

Most tp1.x tests require input data files that must be downloaded from the NOAA-EMC WW3 repository. The rompy-ww3 package provides a download script to automate this process.

```bash
# Download input data for a specific test
python regtests/download_input_data.py tp1.1

# Download input data for all tp1.x tests
python regtests/download_input_data.py tp1

# Download all regression test input data
python regtests/download_input_data.py --all
```

### Configuration Overview

Each test generates the following namelist files:

| File | Purpose | Contents |
|------|---------|----------|
| ww3_shel.nml | Shell configuration | Domain, timing, I/O settings |
| ww3_grid.nml | Grid preprocessing | Grid, depth, boundary conditions |
| namelists.nml | Physics parameters | Source term configurations |
| ww3_ounf.nml | Field output | Output variables and format |

### Running with WW3

After generating configurations, execute the WW3 model using the appropriate backend. rompy-ww3 supports local execution (requires WW3 binaries in PATH) and Docker-based execution.

```bash
# Local execution (requires WW3 installation)
cd rompy_runs/ww3_tp1_1_regression
ww3_shel ww3_shel.nml

# Docker-based execution (requires Docker)
# Configure backend in rompy_ww3.yaml
```

### Validation Approach

The tp1.x tests provide reference outputs for validation of WW3 implementations. Compare generated outputs against expected results using appropriate metrics:

```python
import numpy as np
import xarray as xr

# Load expected and generated outputs
expected = xr.open_dataset("expected_output.nc")
generated = xr.open_dataset("generated_output.nc")

# Calculate error metrics
hs_error = np.sqrt(np.mean((generated.HS - expected.HS)**2))
print(f"HS RMSE: {hs_error:.4f} m")
```

### Common Issues

**Missing input files:** Ensure data has been downloaded before running tests. Use the download script to retrieve required files from the WW3 repository.

**Timestep violations:** WW3 validates timestep relationships according to dtmax ≈ 3×dtxy and dtmax/10 ≤ dtkth ≤ dtmax/2. Adjust timesteps if validation errors occur.

**Coordinate system mismatches:** Ensure grid coordinates match the intended coordinate system (CART for meters, SPHE for degrees). Incorrect coordinate settings cause grid misalignment.

## References

### Primary WW3 Documentation

- WAVEWATCH III User Guide: https://ww3-docs.readthedocs.io/
- WW3 GitHub Repository: https://github.com/NOAA-EMC/WW3
- WW3 Regression Tests: https://github.com/NOAA-EMC/WW3/tree/develop/regtests

### Scientific References

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
├── ww3_tp1.x/
│   ├── README.md                    # This documentation
│   ├── ww3_tp1.1/
│   │   ├── input/                   # Input data files
│   │   │   ├── 1-D.depth
│   │   │   └── points.list
│   │   ├── rompy_runs/              # Generated outputs
│   │   ├── rompy_ww3_tp1_1.py       # Configuration script
│   │   └── rompy_ww3_tp1_1.yaml      # YAML configuration
│   ├── ww3_tp1.2/
│   │   └── ...
│   └── ...
├── download_input_data.py            # Data download script
└── INPUT_DATA.md                    # Input file documentation
```

## Appendix B: Validation Criteria

### Numerical Accuracy Targets

| Quantity | Target Tolerance | Notes |
|----------|------------------|-------|
| Energy conservation | < 1% loss over domain transit | Tests without source terms |
| Shoaling coefficient | < 5% vs analytical | Linear theory comparison |
| Refraction angle | < 1° vs analytical | Simple geometry tests |
| Blocking location | < 1 grid point | Current interaction tests |
| Breaking dissipation | < 10% vs laboratory | Benchmarked tests |

### Performance Expectations

| Test | Computational Time | Hardware Reference |
|------|-------------------|-------------------|
| tp1.1 | ~1 minute | Single core, 2+ GHz |
| tp1.6 | ~5 minutes | Single core, 2+ GHz |
| tp1.8 | ~10 minutes | Single core, 2+ GHz |

Times are approximate and scale with hardware performance. Tests with finer timesteps (tp1.8, tp1.9) require proportionally more compute time.

---

*Documentation generated for rompy-ww3 v0.1.0*  
*Compatible with WAVEWATCH III v6.07.1*
