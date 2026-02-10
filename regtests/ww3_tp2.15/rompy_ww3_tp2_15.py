#!/usr/bin/env python3
"""
WW3 tp2.15 regression test: Space-Time Extremes Parameters.

This test validates WW3's space-time extremes (STE) parameters in the Adriatic Sea.

Test Purpose:
- Validate space-time extremes formulations
- Wind-driven wave growth in the Adriatic Sea
- Test near ISMAR research platform Acqua Alta

Grid Configuration:
- Grid type: CURV (curvilinear, Lambert conformal projection)
- Coordinates: SPHE (spherical)
- Size: 43 × 42 grid points
- Resolution: 15 km spacing
- Region: Adriatic Sea

Physics:
- Full source terms (wind input, ST4/ST6)
- Wind forcing: COSMO-ME model data
- Space-time extremes output

STE Output Parameters:
- STMAXE (MXE): Max surface elevation
- STMAXD (MXES): St Dev of max surface elevation
- HMAXE (MXH): Max wave height
- HCMAXE (MXHC): Max wave height from crest
- HMAXD (SDMH): St Dev of max wave height
- HCMAXD (SDMHC): St Dev of max height from crest

Run with:
    python rompy_ww3_tp2_15.py
"""

from rompy.model import ModelRun
from rompy.core.time import TimeRange
from rompy_ww3.core.data import WW3DataBlob

from rompy_ww3.config import NMLConfig

from rompy_ww3.components import Shel, Grid, Namelists, Ounf
from rompy_ww3.components.namelists import PRO2, PRO3, PRO4

from rompy_ww3.namelists import (
    Domain,
    Spectrum,
    Run,
    Timesteps,
    OutputType,
    HomogCount,
    Input,
)
from rompy_ww3.namelists.output_date import OutputDate
from rompy_ww3.namelists.grid import Grid as GRID_NML
from rompy_ww3.namelists.curv import Curv, CoordData
from rompy_ww3.namelists.depth import Depth
from rompy_ww3.namelists.mask import Mask
from rompy_ww3.namelists.field import Field
from rompy_ww3.namelists.output_file import File as FileNml


def create_ww3_tp2_15_config():
    """Create rompy-ww3 configuration for ww3_tp2.15 regression test.

    This test validates space-time extremes (STE) parameter calculations
    for wind-driven wave growth in the Adriatic Sea.
    """

    # Shell component for ww3_shel.nml
    shell_component = Shel(
        domain=Domain(
            start="20140310 000000",
            stop="20140310 060000",  # 6 hours simulation
            iostyp=1,
        ),
        input_nml=Input(
            forcing={
                "winds": "T",  # Wind forcing enabled
            }
        ),
        output_type=OutputType(
            field={
                "list": "HS WND T02 DP DIR FP MXE MXES MXH MXHC SDMH SDMHC"
            },  # Include STE parameters
            point={"file": "../input/points.list"},
        ),
        output_date=OutputDate(
            field={
                "start": "20140310 000000",
                "stride": "900",  # 15 minutes output
                "stop": "20140310 060000",
            },
            point={
                "start": "20140310 000000",
                "stride": "3600",  # 1 hour point output
                "stop": "20140310 060000",
            },
        ),
        homog_count=HomogCount(
            n_wnd=0,  # No homogeneous wind (use wind files instead)
            n_lev=0,
            n_cur=0,
            n_ice=0,
        ),
        homog_input=[],
    )

    # Grid component for ww3_grid.nml with curvilinear grid
    grid_component = Grid(
        spectrum=Spectrum(
            xfr=1.1,
            freq1=0.05,  # 0.05 Hz first frequency
            nk=40,  # 40 frequency bins
            nth=36,  # 36 directional bins
            thoff=0.5,  # Direction offset
        ),
        run=Run(
            flcx=True,  # X-direction propagation
            flcy=True,  # Y-direction propagation
            flcth=True,  # Spectral refraction
            flck=False,  # No wavenumber shift
            flsou=True,  # Source terms enabled (wind input)
        ),
        timesteps=Timesteps(
            dtmax=1350.0,  # 22.5 minutes max timestep (3× dtxy)
            dtxy=450.0,  # 7.5 minutes spatial step
            dtkth=450.0,  # 7.5 minutes spectral step
            dtmin=5.0,  # 5 seconds minimum
        ),
        grid=GRID_NML(
            name="ADRIATIC SEA 15km LAMBERT CONFORMAL",
            nml="../input/namelists_ADRIATIC.nml",
            type="CURV",  # Curvilinear grid
            coord="SPHE",  # Spherical coordinates
            clos="NONE",  # Regional domain (no closure)
            zlim=-0.10,  # Depth limit
            dmin=2.50,  # Minimum depth
        ),
        curv=Curv(
            nx=43,  # 43 points in x-direction
            ny=42,  # 42 points in y-direction
            xcoord=CoordData(
                filename=WW3DataBlob(
                    source="regtests/ww3_tp2.15/input/lon_ste_adri_15km.dat"
                ),
                format="(...)",  # Auto-detect format
            ),
            ycoord=CoordData(
                filename=WW3DataBlob(
                    source="regtests/ww3_tp2.15/input/lat_ste_adri_15km.dat"
                ),
                format="(...)",  # Auto-detect format
            ),
        ),
        depth=Depth(
            sf=0.001,  # Scale factor (convert from mm to m)
            filename=WW3DataBlob(
                source="regtests/ww3_tp2.15/input/ste_adri_15km_etopo1.depth"
            ),
        ),
        mask=Mask(
            filename=WW3DataBlob(
                source="regtests/ww3_tp2.15/input/ste_adri_15km_etopo1.mask"
            ),
            format="(...)",  # Auto-detect format
        ),
    )

    # Parameters component for namelists.nml
    parameters_component = Namelists(
        pro2=PRO2(dtime=0.0),
        pro3=PRO3(wdthcg=0.0, wdthth=0.0),
        pro4=PRO4(rnfac=0.0, rsfac=0.0),
    )

    # Field output component for ww3_ounf.nml
    field_output_component = Ounf(
        field=Field(
            timestart="20140310 000000",
            timestride="900",  # 15 minutes output
            timecount="1000000000",
            list="HS WND T02 DP DIR FP MXE MXES MXH MXHC SDMH SDMHC",
            partition="0 1 2",
            type="4",  # NetCDF4
            samefile=True,
        ),
        file=FileNml(
            prefix="ww3.",
            netcdf=3,
        ),
    )

    # Combine all components into configuration
    config = NMLConfig(
        shell_component=shell_component,
        grid_component=grid_component,
        parameters_component=parameters_component,
        field_output_component=field_output_component,
    )

    return config


if __name__ == "__main__":
    print("=" * 70)
    print("WW3 tp2.15: Space-Time Extremes Parameters Test")
    print("=" * 70)
    print("\nCreating WW3 configuration for Adriatic Sea STE test...")
    print("Grid: 43×42 curvilinear (15km Lambert conformal)")
    print("Physics: Wind-driven with ST4/ST6 source terms")
    print("STE Parameters: MXE, MXES, MXH, MXHC, SDMH, SDMHC")

    config = create_ww3_tp2_15_config()

    # Create model run
    period = TimeRange(
        start="20140310T000000",
        duration="6H",
        interval="1H",
    )

    model = ModelRun(
        run_id="ww3_tp2_15",
        output_dir="rompy_runs",
        period=period,
        config=config,
    )

    # Generate configuration files
    print("\nGenerating namelist files...")
    model.generate()

    print("\n" + "=" * 70)
    print("✓ CONFIGURATION COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\nThis configuration includes:")
    print("  - Curvilinear grid (43×42) with Lambert conformal projection")
    print("  - Spherical coordinates for Adriatic Sea region")
    print("  - Wind forcing from COSMO-ME model data")
    print("  - Space-time extremes (STE) output parameters")
    print("  - 6-hour simulation with 15-minute field output")
    print("\nSTE Parameters:")
    print("  - MXE (STMAXE): Max surface elevation")
    print("  - MXES (STMAXD): St Dev of max surface elevation")
    print("  - MXH (HMAXE): Max wave height")
    print("  - MXHC (HCMAXE): Max wave height from crest")
    print("  - SDMH (HMAXD): St Dev of max wave height")
    print("  - SDMHC (HCMAXD): St Dev of max height from crest")
    print("\nInput files required in regtests/ww3_tp2.15/input/:")
    print("  - lon_ste_adri_15km.dat (longitude coordinates)")
    print("  - lat_ste_adri_15km.dat (latitude coordinates)")
    print("  - ste_adri_15km_etopo1.depth (bathymetry)")
    print("  - ste_adri_15km_etopo1.mask (land-sea mask)")
    print("  - points.list (point output locations)")
    print("  - namelists_ADRIATIC.nml (physics parameters)")
    print("  - Wind forcing files (from COSMO-ME model)")
