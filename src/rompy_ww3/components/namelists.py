"""Physics parameter namelist implementations for WW3 model parameters.

All fields match the WW3 Fortran NAMELIST declarations in ww3_grid.ftn exactly.
Field names are snake_case versions of the Fortran variable names.
"""

from typing import Optional
from pydantic import Field
from ..namelists.basemodel import NamelistBaseModel


# =============================================================================
# Wind input (SIN) namelists
# =============================================================================


class SIN1(NamelistBaseModel):
    """&SIN1 — WW3 first wind input (WAM-3 / Komen)."""

    cinp: Optional[float] = Field(
        default=None, description="Proportionality constant for wind input"
    )


class SIN2(NamelistBaseModel):
    """&SIN2 — WW3 second wind input (Tolman & Chalikov)."""

    zwnd: Optional[float] = Field(
        default=None, description="Wind measurement height (m)"
    )
    swellf: Optional[float] = Field(default=None, description="Swell factor")
    stabsh: Optional[float] = Field(default=None, description="STABSH parameter")
    stabof: Optional[float] = Field(default=None, description="STABOF parameter")
    cneg: Optional[float] = Field(default=None, description="CNEG parameter")
    cpos: Optional[float] = Field(default=None, description="CPOS parameter")
    fneg: Optional[float] = Field(default=None, description="FNEG parameter")


class SIN3(NamelistBaseModel):
    """&SIN3 — WW3 third wind input (WAM4 / Janssen)."""

    zwnd: Optional[float] = Field(
        default=None, description="Wind measurement height (m)"
    )
    alpha0: Optional[float] = Field(
        default=None, description="Minimum Charnock coefficient"
    )
    z0max: Optional[float] = Field(
        default=None, description="Maximum air-side roughness z0"
    )
    betamax: Optional[float] = Field(
        default=None, description="Maximum wind-wave coupling parameter"
    )
    sinthp: Optional[float] = Field(
        default=None, description="Power of cosine in wind input"
    )
    zalp: Optional[float] = Field(
        default=None, description="Wave age shift for gustiness"
    )
    swellf: Optional[float] = Field(
        default=None, description="Swell attenuation factor"
    )


class SIN4(NamelistBaseModel):
    """&SIN4 — WW3 fourth wind input (ST4)."""

    zwnd: Optional[float] = Field(
        default=None, description="Wind measurement height (m)"
    )
    alpha0: Optional[float] = Field(
        default=None, description="Minimum Charnock coefficient"
    )
    z0max: Optional[float] = Field(
        default=None, description="Maximum air-side roughness z0"
    )
    betamax: Optional[float] = Field(
        default=None, description="Maximum wind-wave coupling parameter"
    )
    sinthp: Optional[float] = Field(
        default=None, description="Power of cosine in wind input"
    )
    zalp: Optional[float] = Field(
        default=None, description="Wave age shift for gustiness"
    )
    tauwshelter: Optional[float] = Field(
        default=None, description="Sheltering factor to reduce u_star for short waves"
    )
    swellfpar: Optional[int] = Field(
        default=None, description="Swell attenuation formulation: 1=TC1996, 3=ACC2008"
    )
    swellf: Optional[float] = Field(
        default=None, description="Swell attenuation factor"
    )
    swellf2: Optional[float] = Field(
        default=None, description="Swell attenuation factor 2"
    )
    swellf3: Optional[float] = Field(
        default=None, description="Swell attenuation factor 3"
    )
    swellf4: Optional[float] = Field(
        default=None, description="Threshold Reynolds number for ACC2008 swell"
    )
    swellf5: Optional[float] = Field(
        default=None, description="Relative viscous decay below threshold (ACC2008)"
    )
    swellf6: Optional[float] = Field(
        default=None, description="Swell attenuation factor 6"
    )
    swellf7: Optional[float] = Field(
        default=None, description="Swell attenuation factor 7"
    )
    z0rat: Optional[float] = Field(
        default=None, description="Roughness ratio: oscillatory flow / mean flow"
    )
    sinbr: Optional[float] = Field(
        default=None, description="Breaking parameter for wind input"
    )


class SIN6(NamelistBaseModel):
    """&SIN6 — WW3 BYDRZ wind input."""

    sina0: Optional[float] = Field(
        default=None, description="Factor for negative input"
    )
    sinws: Optional[float] = Field(
        default=None, description="Wind speed scaling option"
    )
    sinfc: Optional[float] = Field(
        default=None,
        description="High-frequency extent of the prognostic frequency region",
    )


class SLN1(NamelistBaseModel):
    """&SLN1 — WW3 Cavaleri & Malanotte-Rizzoli linear input."""

    clin: Optional[float] = Field(default=None, description="Proportionality constant")
    rfpm: Optional[float] = Field(default=None, description="Factor for fPM in filter")
    rfhf: Optional[float] = Field(default=None, description="Factor for fh in filter")


# =============================================================================
# Nonlinear interaction (SNL) namelists
# =============================================================================


class SNL1(NamelistBaseModel):
    """&SNL1 — WW3 Discrete Interaction Approximation (DIA)."""

    nlambda: Optional[float] = Field(default=None, description="Lambda in source term")
    nlprop: Optional[float] = Field(
        default=None, description="C in source term (depends on other source terms)"
    )
    kdconv: Optional[float] = Field(
        default=None, description="Factor before kd in source term equation"
    )
    kdmin: Optional[float] = Field(default=None, description="Minimum kd")
    snlcs1: Optional[float] = Field(
        default=None, description="Constant c1 in depth scaling function"
    )
    snlcs2: Optional[float] = Field(
        default=None, description="Constant c2 in depth scaling function"
    )
    snlcs3: Optional[float] = Field(
        default=None, description="Constant c3 in depth scaling function"
    )


class SNL2(NamelistBaseModel):
    """&SNL2 — WW3 Exact nonlinear interactions (XNL)."""

    iqtype: Optional[int] = Field(
        default=None,
        description="Depth treatment type: 1=deep, 2=deep/WAM scaling, 3=shallow",
    )
    tailnl: Optional[float] = Field(default=None, description="Parametric tail power")
    ndepth: Optional[int] = Field(
        default=None,
        description="Number of depths for integration space (IQTYPE=3 only)",
    )


class SNL3(NamelistBaseModel):
    """&SNL3 — WW3 Generalized Multiple DIA (GMD)."""

    nqdef: Optional[int] = Field(default=None, description="Number of quadruplets")
    msc: Optional[float] = Field(default=None, description="Scaling constant m")
    nsc: Optional[float] = Field(default=None, description="Scaling constant N")
    kdfd: Optional[float] = Field(
        default=None, description="Deep water relative filter depth"
    )
    kdfs: Optional[float] = Field(
        default=None, description="Shallow water relative filter depth"
    )


class SNL4(NamelistBaseModel):
    """&SNL4 — WW3 Two-Scale Approximation (TSA/FBI)."""

    indtsa: Optional[int] = Field(
        default=None, description="Index for TSA/FBI: 0=FBI, 1=TSA"
    )
    altlp: Optional[int] = Field(
        default=None, description="Index for alternate looping: 1=no, 2=yes"
    )


class SNLS(NamelistBaseModel):
    """&SNLS — WW3 Nonlinear filter based on DIA."""

    a34: Optional[float] = Field(
        default=None, description="Relative offset in quadruplet"
    )
    fhfc: Optional[float] = Field(default=None, description="Proportionality constants")
    dnm: Optional[float] = Field(default=None, description="Maximum relative change")
    fc1: Optional[float] = Field(
        default=None, description="Constant in frequency filter"
    )
    fc2: Optional[float] = Field(
        default=None, description="Constant in frequency filter"
    )
    fc3: Optional[float] = Field(
        default=None, description="Constant in frequency filter"
    )


# =============================================================================
# Dissipation (SDS) namelists
# =============================================================================


class SDS1(NamelistBaseModel):
    """&SDS1 — WW3 WAM-3 whitecapping dissipation."""

    cdis: Optional[float] = Field(default=None, description="CDIS dissipation constant")
    apm: Optional[float] = Field(default=None, description="APM parameter")


class SDS2(NamelistBaseModel):
    """&SDS2 — WW3 Tolman & Chalikov whitecapping."""

    sdsa0: Optional[float] = Field(default=None, description="Constant a0")
    sdsa1: Optional[float] = Field(default=None, description="Constant a1")
    sdsa2: Optional[float] = Field(default=None, description="Constant a2")
    sdsb0: Optional[float] = Field(default=None, description="Constant b0")
    sdsb1: Optional[float] = Field(default=None, description="Constant b1")
    phimin: Optional[float] = Field(default=None, description="PHImin parameter")


class SDS3(NamelistBaseModel):
    """&SDS3 — WW3 WAM4 / Westhuysen whitecapping."""

    sdsc1: Optional[float] = Field(default=None, description="WAM4 Cds coefficient")
    wnmeanp: Optional[float] = Field(
        default=None, description="Power of wavenumber for mean definitions"
    )
    fxpm3: Optional[float] = Field(
        default=None, description="Frequency exponent for PM3"
    )
    fxfm3: Optional[float] = Field(
        default=None, description="Frequency exponent for FM3"
    )
    sdsdelta1: Optional[float] = Field(
        default=None, description="Weight of k part of WAM4 dissipation"
    )
    sdsdelta2: Optional[float] = Field(
        default=None, description="Weight of k^2 part of WAM4 dissipation"
    )


class SDS4(NamelistBaseModel):
    """&SDS4 — WW3 ST4 whitecapping dissipation."""

    sdsc1: Optional[float] = Field(default=None, description="WAM4 Cds coefficient")
    wnmeanp: Optional[float] = Field(
        default=None, description="Power of wavenumber for mean definitions"
    )
    wnmeanptail: Optional[float] = Field(
        default=None, description="Power of wavenumber for mean in tail"
    )
    fxpm3: Optional[float] = Field(
        default=None, description="Frequency exponent for PM3"
    )
    fxfm3: Optional[float] = Field(
        default=None, description="Frequency exponent for FM3"
    )
    fxfmage: Optional[float] = Field(
        default=None, description="Frequency exponent for FM age correction"
    )
    sdsc2: Optional[float] = Field(
        default=None, description="Saturation dissipation coefficient"
    )
    sdscum: Optional[float] = Field(
        default=None, description="Cumulative dissipation coefficient"
    )
    sdsstrain: Optional[float] = Field(default=None, description="Strain parameter")
    sdsstraina: Optional[float] = Field(default=None, description="Strain parameter A")
    sdsstrain2: Optional[float] = Field(default=None, description="Strain parameter 2")
    sdsc4: Optional[float] = Field(
        default=None, description="Value of B0=B/Br for zero dissipation"
    )
    sdsc5: Optional[float] = Field(
        default=None, description="Turbulence dissipation coefficient"
    )
    sdsc6: Optional[float] = Field(
        default=None, description="Weight for isotropic part of Sds_SAT"
    )
    sdsbr: Optional[float] = Field(
        default=None, description="Threshold Br for saturation"
    )
    sdsbr2: Optional[float] = Field(
        default=None, description="Threshold Br2 for saturated/unsaturated separation"
    )
    sdsp: Optional[float] = Field(
        default=None, description="Power of (B/Br-B0) in dissipation"
    )
    sdsiso: Optional[float] = Field(
        default=None, description="Isotropic dissipation factor"
    )
    sdsbck: Optional[float] = Field(default=None, description="Background dissipation")
    sdsabk: Optional[float] = Field(default=None, description="Alpha for background")
    sdspbk: Optional[float] = Field(default=None, description="Power for background")
    sdsbint: Optional[float] = Field(
        default=None, description="B-integral for dissipation"
    )
    sdshck: Optional[float] = Field(default=None, description="High-frequency cut-off")
    sdsdth: Optional[float] = Field(
        default=None, description="Angular half-width for B integration"
    )
    sdscos: Optional[float] = Field(
        default=None, description="Cos power for angular distribution"
    )
    sdsbrf1: Optional[float] = Field(default=None, description="Breaking factor 1")
    sdsbrfdf: Optional[float] = Field(
        default=None, description="Breaking factor frequency"
    )
    sdsbm0: Optional[float] = Field(
        default=None, description="Breaking mean parameter M0"
    )
    sdsbm1: Optional[float] = Field(
        default=None, description="Breaking mean parameter M1"
    )
    sdsbm2: Optional[float] = Field(
        default=None, description="Breaking mean parameter M2"
    )
    sdsbm3: Optional[float] = Field(
        default=None, description="Breaking mean parameter M3"
    )
    sdsbm4: Optional[float] = Field(
        default=None, description="Breaking mean parameter M4"
    )
    sdshfgen: Optional[float] = Field(
        default=None, description="High-frequency generation factor"
    )
    sdslfgen: Optional[float] = Field(
        default=None, description="Low-frequency generation factor"
    )
    whitecapwidth: Optional[float] = Field(
        default=None, description="Whitecapping width parameter"
    )
    fxincut: Optional[float] = Field(
        default=None, description="Frequency input cut-off"
    )
    fxdscut: Optional[float] = Field(
        default=None, description="Frequency dissipation cut-off"
    )


class SDS6(NamelistBaseModel):
    """&SDS6 — WW3 BYDRZ dissipation."""

    sdset: Optional[float] = Field(
        default=None, description="Select threshold normalization spectra"
    )
    sdsa1: Optional[float] = Field(default=None, description="Coefficient for T1 term")
    sdsa2: Optional[float] = Field(default=None, description="Coefficient for T2 term")
    sdsp1: Optional[float] = Field(default=None, description="Power for T1 term")
    sdsp2: Optional[float] = Field(default=None, description="Power for T2 term")


class SWL6(NamelistBaseModel):
    """&SWL6 — WW3 swell dissipation (BYDRZ)."""

    swlb1: Optional[float] = Field(
        default=None, description="Swell dissipation coefficient"
    )
    cstb1: Optional[float] = Field(
        default=None, description="Constant for swell dissipation"
    )


# =============================================================================
# Bottom friction (SBT) namelists
# =============================================================================


class SBT1(NamelistBaseModel):
    """&SBT1 — WW3 JONSWAP bottom friction."""

    gamma: Optional[float] = Field(
        default=None, description="JONSWAP bottom friction empirical constant"
    )


class SBT4(NamelistBaseModel):
    """&SBT4 — WW3 sedimentary bottom friction (SHOWEX)."""

    sedmapd50: Optional[bool] = Field(
        default=None, description="Use sediment map for D50"
    )
    sed_d50_uniform: Optional[float] = Field(
        default=None, description="Uniform D50 value (m)"
    )
    ripfac1: Optional[float] = Field(default=None, description="Ripple factor 1")
    ripfac2: Optional[float] = Field(default=None, description="Ripple factor 2")
    ripfac3: Optional[float] = Field(default=None, description="Ripple factor 3")
    ripfac4: Optional[float] = Field(default=None, description="Ripple factor 4")
    sigdepth: Optional[float] = Field(default=None, description="Significant depth")
    botroughmin: Optional[float] = Field(
        default=None, description="Minimum bottom roughness"
    )
    botroughfac: Optional[float] = Field(
        default=None, description="Bottom roughness factor"
    )


# =============================================================================
# Surf breaking (SDB) namelist
# =============================================================================


class SDB1(NamelistBaseModel):
    """&SDB1 — WW3 Battjes & Janssen surf/depth-induced breaking."""

    bjalfa: Optional[float] = Field(
        default=None, description="Dissipation constant (default=1)"
    )
    bjgam: Optional[float] = Field(
        default=None, description="Breaking threshold (default=0.73)"
    )
    bjflag: Optional[bool] = Field(
        default=None, description="T=Hmax/d ratio only, F=Hmax/d in Miche formulation"
    )


# =============================================================================
# Flux (FLX) namelists
# =============================================================================


class FLX3(NamelistBaseModel):
    """&FLX3 — WW3 Tolman & Chalikov 1996 flux with cap."""

    cdmax: Optional[float] = Field(
        default=None, description="Maximum allowed drag coefficient"
    )
    ctype: Optional[int] = Field(
        default=None, description="Cap type: 0=discontinuous, 1=hyperbolic tangent"
    )


class FLX4(NamelistBaseModel):
    """&FLX4 — WW3 Hwang 2011 flux."""

    cdfac: Optional[float] = Field(
        default=None, description="Re-scaling factor for drag"
    )


# =============================================================================
# Sea-state dependent stress (FLD) namelists
# =============================================================================


class FLD1(NamelistBaseModel):
    """&FLD1 — WW3 Reichl et al. 2014 sea-state dependent stress."""

    tailtype: Optional[int] = Field(
        default=None,
        description="High frequency tail method: 0=constant, 1=wind-dependent",
    )
    taillev: Optional[float] = Field(
        default=None,
        description="Level of high frequency tail (TAILTYPE=0, 0.001..0.02)",
    )
    tailt1: Optional[float] = Field(
        default=None, description="Tail transition ratio 1 (default=1.25)"
    )
    tailt2: Optional[float] = Field(
        default=None, description="Tail transition ratio 2 (default=3.00)"
    )


class FLD2(NamelistBaseModel):
    """&FLD2 — WW3 Donelan et al. 2012 sea-state dependent stress."""

    tailtype: Optional[int] = Field(
        default=None,
        description="High frequency tail method: 0=constant, 1=wind-dependent",
    )
    taillev: Optional[float] = Field(
        default=None, description="Level of high frequency tail"
    )
    tailt1: Optional[float] = Field(default=None, description="Tail transition ratio 1")
    tailt2: Optional[float] = Field(default=None, description="Tail transition ratio 2")


# =============================================================================
# Propagation (PRO) namelists
# =============================================================================


class PRO1(NamelistBaseModel):
    """&PRO1 — WW3 first-order propagation scheme."""

    cfltm: Optional[float] = Field(
        default=None, description="Maximum CFL number for refraction"
    )


class PRO2(NamelistBaseModel):
    """&PRO2 — WW3 UQ/UNO with diffusion propagation scheme."""

    cfltm: Optional[float] = Field(
        default=None, description="Maximum CFL number for refraction"
    )
    dtime: Optional[float] = Field(
        default=None,
        description="Swell age (s) in garden sprinkler correction. 0=no diffusion",
    )
    latmin: Optional[float] = Field(
        default=None,
        description="Maximum latitude for diffusion strength calculation",
    )


class PRO3(NamelistBaseModel):
    """&PRO3 — WW3 UQ/UNO with averaging propagation scheme."""

    cfltm: Optional[float] = Field(
        default=None, description="Maximum CFL number for refraction"
    )
    wdthcg: Optional[float] = Field(
        default=None, description="Tuning factor for propagation direction"
    )
    wdthth: Optional[float] = Field(
        default=None, description="Tuning factor for normal direction"
    )


class PRO4(NamelistBaseModel):
    """&PRO4 — Not a standard WW3 namelist; kept for backwards compatibility.

    No equivalent in the WW3 Fortran source. Uses custom refraction parameters
    for experimentation.
    """

    rnfac: Optional[float] = Field(default=None, description="Refraction factor")
    rsfac: Optional[float] = Field(
        default=None, description="Refraction smoothing factor"
    )


# =============================================================================
# Ice scattering / dissipation (SIS) namelists
# =============================================================================


class SIS1(NamelistBaseModel):
    """&SIS1 — WW3 ice scattering (Williams et al. 2013)."""

    isc1: Optional[float] = Field(default=None, description="Scattering coefficient")
    isc2: Optional[float] = Field(default=None, description="Scattering coefficient 2")


class SIS2(NamelistBaseModel):
    """&SIS2 — WW3 generalized ice scattering / creep dissipation."""

    isc1: Optional[float] = Field(default=None, description="Scattering coefficient")
    is2c2: Optional[float] = Field(
        default=None, description="Frequency dependence of scattering in pack ice c2"
    )
    is2c3: Optional[float] = Field(
        default=None, description="Frequency dependence of scattering in pack ice c3"
    )
    is2backscat: Optional[float] = Field(
        default=None, description="Fraction of energy back-scattered"
    )
    is2isoscat: Optional[float] = Field(
        default=None,
        description="Fraction of scattered energy isotropically redistributed",
    )
    is2break: Optional[bool] = Field(
        default=None, description="T=update floe max diameter"
    )
    is2disp: Optional[bool] = Field(
        default=None, description="Use ice-specific dispersion relation"
    )
    is2fragility: Optional[float] = Field(
        default=None, description="Parameter 0..1 for FSD shape"
    )
    is2conc: Optional[float] = Field(
        default=None, description="Ice concentration parameter"
    )
    is2dmin: Optional[float] = Field(
        default=None, description="Minimum floe diameter (m)"
    )
    is2damp: Optional[float] = Field(
        default=None, description="Multiplicative coefficient for dissipation from RP"
    )
    is2dupdate: Optional[bool] = Field(
        default=None, description="T=update max floe diameter with forcing only"
    )
    is2creepb: Optional[float] = Field(default=None, description="Creep parameter B")
    is2creepc: Optional[float] = Field(default=None, description="Creep parameter C")
    is2creepd: Optional[float] = Field(default=None, description="Creep parameter D")
    is2creepn: Optional[float] = Field(default=None, description="Creep parameter N")
    is2breake: Optional[float] = Field(default=None, description="Breaking parameter E")
    is2breakf: Optional[float] = Field(default=None, description="Breaking parameter F")
    is2wim1: Optional[float] = Field(default=None, description="WIM parameter 1")
    is2flexstr: Optional[float] = Field(default=None, description="Flexural strength")
    is2andisb: Optional[float] = Field(default=None, description="Andis parameter B")
    is2andise: Optional[float] = Field(default=None, description="Andis parameter E")
    is2andisd: Optional[float] = Field(default=None, description="Andis parameter D")
    is2andisn: Optional[float] = Field(default=None, description="Andis parameter N")


# =============================================================================
# Ice interaction (SIC) namelists
# =============================================================================


class SIC2(NamelistBaseModel):
    """&SIC2 — WW3 Liu et al. ice dissipation."""

    ic2disper: Optional[bool] = Field(
        default=None,
        description="T=Liu formulation with eddy viscosity, F=generalization with laminar-turbulent transition",
    )
    ic2turb: Optional[float] = Field(
        default=None, description="Empirical factor for turbulent part"
    )
    ic2rough: Optional[float] = Field(
        default=None, description="Under-ice roughness length"
    )
    ic2reynolds: Optional[float] = Field(
        default=None, description="Re number for laminar-turbulent transition"
    )
    ic2smooth: Optional[float] = Field(
        default=None, description="Smoothing of transition for random waves"
    )
    ic2visc: Optional[float] = Field(
        default=None, description="Empirical factor for viscous part"
    )
    ic2turbs: Optional[float] = Field(
        default=None, description="Turbulence strength parameter"
    )
    ic2dmax: Optional[float] = Field(
        default=None, description="Maximum floe diameter (m)"
    )


class SIC3(NamelistBaseModel):
    """&SIC3 — WW3 ice interaction (extended)."""

    ic3maxthk: Optional[float] = Field(
        default=None, description="Maximum ice thickness (m)"
    )
    ic2turb: Optional[float] = Field(default=None, description="Turbulent part factor")
    ic2rough: Optional[float] = Field(default=None, description="Under-ice roughness")
    ic2reynolds: Optional[float] = Field(
        default=None, description="Transition Re number"
    )
    ic2smooth: Optional[float] = Field(default=None, description="Transition smoothing")
    ic2visc: Optional[float] = Field(default=None, description="Viscous part factor")
    ic2turbs: Optional[float] = Field(default=None, description="Turbulence strength")
    ic3maxcnc: Optional[float] = Field(
        default=None, description="Maximum ice concentration"
    )
    ic3cheng: Optional[float] = Field(
        default=None, description="Cheng et al. friction parameter"
    )
    usecgice: Optional[bool] = Field(
        default=None, description="Use CG ice dispersion relation"
    )
    ic3hilim: Optional[float] = Field(default=None, description="Ice thickness limit")
    ic3kilim: Optional[float] = Field(default=None, description="Ice wavenumber limit")
    ic3visc: Optional[float] = Field(default=None, description="Ice viscosity")
    ic3elas: Optional[float] = Field(default=None, description="Ice elasticity")
    ic3dens: Optional[float] = Field(default=None, description="Ice density")
    ic3hice: Optional[float] = Field(default=None, description="Ice thickness")


class SIC4(NamelistBaseModel):
    """&SIC4 — WW3 empirical/parametric ice dissipation."""

    ic4method: Optional[int] = Field(
        default=None, description="Method selection: integer 1-7"
    )
    ic4ki: Optional[float] = Field(default=None, description="Ice wavenumber parameter")
    ic4fc: Optional[float] = Field(default=None, description="Cut-off frequency")


class SIC5(NamelistBaseModel):
    """&SIC5 — WW3 ice interaction (elastic wave propagation)."""

    ic5minig: Optional[float] = Field(
        default=None, description="Minimum ice elasticity"
    )
    ic5minwt: Optional[float] = Field(default=None, description="Minimum wave period")
    ic5maxkratio: Optional[float] = Field(
        default=None, description="Maximum wavenumber ratio"
    )
    ic5maxki: Optional[float] = Field(
        default=None, description="Maximum ice wavenumber"
    )
    ic5minhw: Optional[float] = Field(default=None, description="Minimum water depth")
    ic5maxiter: Optional[int] = Field(default=None, description="Maximum iterations")
    ic5rkick: Optional[float] = Field(default=None, description="RK kick parameter")
    ic5kfilter: Optional[float] = Field(default=None, description="Wavenumber filter")


# =============================================================================
# Infragravity (SIG) namelist
# =============================================================================


class SIG1(NamelistBaseModel):
    """&SIG1 — WW3 infragravity waves."""

    igmethod: Optional[int] = Field(
        default=None, description="Method: 1=Hasselmann, 2=Krasitskii-Janssen"
    )
    igaddoutp: Optional[bool] = Field(
        default=None, description="Activate bound wave correction in output"
    )
    igsource: Optional[int] = Field(
        default=None, description="Source type: 1=bound waves, 2=empirical"
    )
    igbcoverwrite: Optional[bool] = Field(
        default=None, description="T=replace IG spectrum, F=add"
    )
    igmaxfreq: Optional[float] = Field(
        default=None, description="Maximum frequency of IG band"
    )
    igsterms: Optional[int] = Field(
        default=None, description=">0=no source terms in IG band"
    )
    igswellmax: Optional[bool] = Field(
        default=None, description="T=activate free IG sources for all frequencies"
    )
    igsourceatbp: Optional[float] = Field(
        default=None, description="IG source at boundary point"
    )
    igkdmin: Optional[float] = Field(default=None, description="Minimum kd for IG")
    igfixeddepth: Optional[float] = Field(
        default=None, description="Fixed depth for IG"
    )
    igempirical: Optional[float] = Field(
        default=None, description="Constant in empirical free IG source"
    )


# =============================================================================
# Miscellaneous (MISC) namelist
# =============================================================================


class MISC(NamelistBaseModel):
    """&MISC namelist for WW3 miscellaneous parameters.

    Full parameter set from WW3 source (ww3_grid.ftn).
    """

    # Ice parameters
    cice0: Optional[float] = Field(
        default=None, description="Ice concentration cut-off for output"
    )
    cicen: Optional[float] = Field(
        default=None, description="Ice concentration normalization factor"
    )
    lice: Optional[bool] = Field(default=None, description="Ice point treatment flag")
    icehmin: Optional[float] = Field(
        default=None, description="Minimum ice thickness (m)"
    )
    icehinit: Optional[float] = Field(
        default=None, description="Initial ice thickness (m)"
    )
    icedisp: Optional[float] = Field(
        default=None, description="Ice dispersion parameter"
    )
    icesln: Optional[float] = Field(default=None, description="Ice salinity (ppt)")
    icewind: Optional[float] = Field(default=None, description="Ice wind factor")
    icesnl: Optional[float] = Field(
        default=None, description="Ice nonlinear interaction factor"
    )
    icesds: Optional[float] = Field(default=None, description="Ice dissipation factor")
    icehfac: Optional[float] = Field(default=None, description="Ice thickness factor")
    icehdisp: Optional[float] = Field(
        default=None, description="Ice thickness dispersion"
    )
    iceddisp: Optional[float] = Field(
        default=None, description="Ice diameter dispersion"
    )
    icefdisp: Optional[float] = Field(
        default=None, description="Ice floe diameter dispersion"
    )

    # Obstruction / grid parameters
    xseed: Optional[float] = Field(
        default=None, description="Xseed in seeding algorithm"
    )
    flagtr: Optional[int] = Field(
        default=None,
        description="Subgrid obstruction: 0=none, 1=cell boundaries, "
        "2=cell centers, 3=like1+cont.ice, 4=like2+cont.ice",
    )
    xp: Optional[float] = Field(
        default=None, description="Dynamic integration parameter Xp"
    )
    xr: Optional[float] = Field(
        default=None, description="Dynamic integration parameter Xr"
    )
    xfilt: Optional[float] = Field(
        default=None, description="Dynamic integration filter Xf"
    )
    pmove: Optional[float] = Field(
        default=None, description="Power p in GSE alleviation for moving grids"
    )

    # Partitioning parameters
    ptm: Optional[int] = Field(
        default=None,
        description="Partitioning method: 1=standard, 2=watershed+wind, "
        "3=watershed, 4=wind cutoff, 5=high/low band",
    )
    ptfc: Optional[float] = Field(
        default=None,
        description="Partitioning frequency cutoff for 2-band partitioning (Hz)",
    )
    ihm: Optional[int] = Field(
        default=None, description="Number of discrete levels in partitioning"
    )
    hspm: Optional[float] = Field(
        default=None, description="Minimum Hs in partitioning (m)"
    )
    wsm: Optional[float] = Field(
        default=None, description="Wind speed multiplier in partitioning"
    )
    wsc: Optional[float] = Field(
        default=None, description="Wind sea fraction cutoff for identifying wind sea"
    )
    flc: Optional[bool] = Field(
        default=None, description="Flag for combining wind seas in partitioning"
    )
    nosw: Optional[int] = Field(
        default=None,
        description="Number of partitioned swell fields in field output",
    )
    fmiche: Optional[float] = Field(
        default=None, description="Constant in Miche limiter"
    )
    btbet: Optional[float] = Field(
        default=None, description="Beta parameter for bottom friction correction"
    )

    # Wind / iceberg correction
    rwndc: Optional[float] = Field(default=None, description="Wind reduction factor")
    facberg: Optional[float] = Field(default=None, description="Iceberg factor")
    gshift: Optional[float] = Field(default=None, description="Grid shift parameter")
    wcor1: Optional[float] = Field(
        default=None, description="Wind correction parameter 1"
    )
    wcor2: Optional[float] = Field(
        default=None, description="Wind correction parameter 2"
    )

    # Space-Time Extremes (STE)
    stdx: Optional[float] = Field(
        default=None, description="Space-Time Extremes X-Length"
    )
    stdy: Optional[float] = Field(
        default=None, description="Space-Time Extremes Y-Length"
    )
    stdt: Optional[float] = Field(
        default=None, description="Space-Time Extremes Duration"
    )

    # Calendar
    noleap: Optional[bool] = Field(
        default=None, description="No-leap calendar flag (T=360-day calendar)"
    )

    # Output
    trckcmpr: Optional[bool] = Field(
        default=None, description="Track compression: F to disable compression"
    )


# =============================================================================
# Shoreline reflections (REF1)
# =============================================================================


class REF1(NamelistBaseModel):
    """&REF1 — WW3 shoreline reflection parameters."""

    refcoast: Optional[float] = Field(
        default=None, description="Reflection coefficient at shoreline"
    )
    reffreq: Optional[bool] = Field(
        default=None, description="Activate frequency-dependent reflection"
    )
    refmap: Optional[float] = Field(
        default=None, description="Scale factor for bottom slope map"
    )
    refmapd: Optional[float] = Field(
        default=None, description="Scale factor for depth map"
    )
    refsubgrid: Optional[float] = Field(
        default=None, description="Reflection coefficient for subgrid islands"
    )
    reficeberg: Optional[float] = Field(
        default=None, description="Reflection coefficient for icebergs"
    )
    refcosp_straight: Optional[float] = Field(
        default=None, description="Power of cosine for straight shoreline"
    )
    refslope: Optional[float] = Field(
        default=None, description="Reflection slope parameter"
    )
    refrmax: Optional[float] = Field(
        default=None, description="Maximum reflection coefficient (default=0.8)"
    )
    reffreqpow: Optional[float] = Field(
        default=None, description="Power of frequency in reflection"
    )
    refunstsource: Optional[bool] = Field(
        default=None, description="Unstructured source term flag"
    )


# =============================================================================
# Rotated pole (ROTD)
# =============================================================================


class ROTD(NamelistBaseModel):
    """&ROTD — WW3 rotated pole parameters."""

    plat: Optional[float] = Field(default=None, description="Rotated pole latitude")
    plon: Optional[float] = Field(default=None, description="Rotated pole longitude")
    unrot: Optional[bool] = Field(
        default=None, description="T=un-rotate directions to true north"
    )


# =============================================================================
# Unstructured grid obstacle (UOST)
# =============================================================================


class UOST(NamelistBaseModel):
    """&UOST — WW3 unstructured grid obstacle parameters."""

    uostfilelocal: Optional[str] = Field(
        default=None, description="Local obstacle file"
    )
    uostfileshadow: Optional[str] = Field(
        default=None, description="Shadow obstacle file"
    )
    uostfactorlocal: Optional[float] = Field(
        default=None, description="Factor for local obstacle"
    )
    uostfactorshadow: Optional[float] = Field(
        default=None, description="Factor for shadow obstacle"
    )


# =============================================================================
# Container for all namelists (namelists.nml)
# =============================================================================


class Namelists(NamelistBaseModel):
    """Container for all WW3 physics parameter namelists.

    This model contains all the individual physics parameter components
    that make up the namelists.nml file in WW3. All field names match the
    Fortran source NAMELIST group names exactly (snake_case convention).
    """

    # Wind input
    sin1: Optional[SIN1] = Field(default=None, description="SIN1 — WAM-3 wind input")
    sin2: Optional[SIN2] = Field(
        default=None, description="SIN2 — Tolman & Chalikov wind input"
    )
    sin3: Optional[SIN3] = Field(default=None, description="SIN3 — WAM4 wind input")
    sin4: Optional[SIN4] = Field(default=None, description="SIN4 — ST4 wind input")
    sin6: Optional[SIN6] = Field(default=None, description="SIN6 — BYDRZ wind input")
    sln1: Optional[SLN1] = Field(
        default=None, description="SLN1 — Cavaleri & Malanotte-Rizzoli linear input"
    )

    # Nonlinear interactions
    snl1: Optional[SNL1] = Field(default=None, description="SNL1 — DIA")
    snl2: Optional[SNL2] = Field(
        default=None, description="SNL2 — Exact nonlinear (XNL)"
    )
    snl3: Optional[SNL3] = Field(
        default=None, description="SNL3 — Generalized Multiple DIA (GMD)"
    )
    snl4: Optional[SNL4] = Field(
        default=None, description="SNL4 — Two-Scale Approximation (TSA/FBI)"
    )
    snls: Optional[SNLS] = Field(
        default=None, description="SNLS — Nonlinear filter based on DIA"
    )

    # Dissipation
    sds1: Optional[SDS1] = Field(default=None, description="SDS1 — WAM-3 whitecapping")
    sds2: Optional[SDS2] = Field(
        default=None, description="SDS2 — Tolman & Chalikov whitecapping"
    )
    sds3: Optional[SDS3] = Field(default=None, description="SDS3 — WAM4 whitecapping")
    sds4: Optional[SDS4] = Field(default=None, description="SDS4 — ST4 whitecapping")
    sds6: Optional[SDS6] = Field(default=None, description="SDS6 — BYDRZ dissipation")
    swl6: Optional[SWL6] = Field(
        default=None, description="SWL6 — Swell dissipation (BYDRZ)"
    )

    # Bottom friction
    sbt1: Optional[SBT1] = Field(
        default=None, description="SBT1 — JONSWAP bottom friction"
    )
    sbt4: Optional[SBT4] = Field(
        default=None, description="SBT4 — Sedimentary bottom friction (SHOWEX)"
    )

    # Surf breaking
    sdb1: Optional[SDB1] = Field(
        default=None, description="SDB1 — Battjes & Janssen surf breaking"
    )

    # Flux / stress
    flx3: Optional[FLX3] = Field(
        default=None, description="FLX3 — TC1996 flux with cap"
    )
    flx4: Optional[FLX4] = Field(default=None, description="FLX4 — Hwang 2011 flux")
    fld1: Optional[FLD1] = Field(
        default=None, description="FLD1 — Reichl et al. 2014 sea-state stress"
    )
    fld2: Optional[FLD2] = Field(
        default=None, description="FLD2 — Donelan et al. 2012 sea-state stress"
    )

    # Propagation
    pro1: Optional[PRO1] = Field(
        default=None, description="PRO1 — First-order propagation"
    )
    pro2: Optional[PRO2] = Field(
        default=None, description="PRO2 — UQ/UNO with diffusion"
    )
    pro3: Optional[PRO3] = Field(
        default=None, description="PRO3 — UQ/UNO with averaging"
    )
    pro4: Optional[PRO4] = Field(
        default=None, description="PRO4 — Custom refraction parameters"
    )

    # Ice scattering
    sis1: Optional[SIS1] = Field(
        default=None, description="SIS1 — Ice scattering (Williams 2013)"
    )
    sis2: Optional[SIS2] = Field(
        default=None, description="SIS2 — Generalized ice scattering/creep"
    )

    # Ice dissipation
    sic2: Optional[SIC2] = Field(
        default=None, description="SIC2 — Liu et al. ice dissipation"
    )
    sic3: Optional[SIC3] = Field(
        default=None, description="SIC3 — Extended ice interaction"
    )
    sic4: Optional[SIC4] = Field(
        default=None, description="SIC4 — Empirical/parametric ice dissipation"
    )
    sic5: Optional[SIC5] = Field(
        default=None, description="SIC5 — Elastic wave ice interaction"
    )

    # Infragravity
    sig1: Optional[SIG1] = Field(default=None, description="SIG1 — Infragravity waves")

    # Miscellaneous
    misc: Optional[MISC] = Field(
        default=None, description="MISC — Miscellaneous parameters"
    )

    # Shoreline reflections
    ref1: Optional[REF1] = Field(
        default=None, description="REF1 — Shoreline reflection parameters"
    )

    # Rotated pole
    rotd: Optional[ROTD] = Field(
        default=None, description="ROTD — Rotated pole parameters"
    )

    # Unstructured grid obstacle
    uost: Optional[UOST] = Field(
        default=None, description="UOST — Unstructured grid obstacle parameters"
    )

    def render(self, *args, **kwargs) -> str:
        """Render namelists as Fortran namelist string.

        Each set sub-model renders as: &NAMELIST_NAME FIELD = value, ... /
        Followed by END OF NAMELISTS.
        """
        content = []
        model_data = self.model_dump()
        for key, value in model_data.items():
            if value is None:
                continue
            line = f"&{key.upper()}"
            separator = " "
            for sub_key, sub_value in value.items():
                # Convert boolean to WW3 format
                if isinstance(sub_value, bool):
                    sub_value = "T" if sub_value else "F"
                line += f"{separator}{sub_key.upper()} = {sub_value}"
                separator = ", "
            line += " /"
            content.append(line)

        content.append("END OF NAMELISTS")
        return "\n".join(content)
