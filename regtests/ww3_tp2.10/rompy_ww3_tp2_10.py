#!/usr/bin/env python3
"""
WW3 tp2.10 regression test: SMC (Spherical Multi-Cell) Grid.

This test validates WW3 on SMC grids with multi-resolution capabilities.
SMC grids use nested cells for higher resolution in specific regions.

Grid Configuration:
- Grid type: SMCG (Spherical Multi-Cell Grid)
- Base grid: 256×128 cells
- Resolution: Variable (0.02° lon × 0.016° lat base)
- Extent: Lake Erie region (276.41°W, 41.028°N base)

Physics:
- Pure propagation (no source terms, flsou=False)
- Full spatial propagation (flcx=True, flcy=True)
- Spectral processes enabled (flcth=True, flck=True)

Input Data:
- ErieSMCel.dat: SMC cell arrays
- ErieISide.dat: I-direction face arrays
- ErieJSide.dat: J-direction face arrays
- ErieObstr.dat: Obstruction data

Run with:
    python rompy_ww3_tp2_10.py
"""

import sys
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
from rompy_ww3.namelists.grid import Grid as GRID_NML, Rect
from rompy_ww3.namelists.smc import Smc, SMCFile
from rompy_ww3.namelists.depth import Depth
from rompy_ww3.namelists.field import Field
from rompy_ww3.namelists.output_file import File as FileNml


def create_ww3_tp2_10_config():
    """Create rompy-ww3 configuration for ww3_tp2.10 regression test.

    This test validates SMC (Spherical Multi-Cell) grids in WW3.
    SMC grids provide multi-resolution capability with nested cells.
    """

    # Shell component for ww3_shel.nml
    shell_component = Shel(
        domain=Domain(
            start="19680606 000000",
            stop="19680606 060000",  # 6 hours
            iostyp=1,
        ),
        input_nml=Input(
            forcing={},  # No forcing - pure propagation test
        ),
        output_type=OutputType(
            field={"list": "WND HS T01"},
            point={"file": "../input/points.list"},
        ),
        output_date=OutputDate(
            field={
                "start": "19680606 000000",
                "stride": "3600",  # 1 hour output
                "stop": "19680608 000000",
            },
            point={
                "start": "19680606 000000",
                "stride": "3600",
                "stop": "19680608 000000",
            },
        ),
        homog_count=HomogCount(
            n_wnd=0,
            n_lev=0,
            n_cur=0,
            n_ice=0,
        ),
        homog_input=[],
    )

    # Grid component for ww3_grid.nml with SMC configuration
    grid_component = Grid(
        spectrum=Spectrum(
            xfr=1.1,
            freq1=0.04118,
            nk=25,
            nth=24,
            thoff=0.0,
        ),
        run=Run(
            flcx=True,  # X-direction propagation
            flcy=True,  # Y-direction propagation
            flcth=True,  # Spectral refraction
            flck=True,  # Wavenumber shift
            flsou=False,  # No source terms
        ),
        timesteps=Timesteps(
            dtmax=180.0,  # 3 minutes (adjusted: 3× dtxy for validation)
            dtxy=60.0,  # 1 minute
            dtkth=60.0,  # 1 minute
            dtmin=10.0,  # 10 seconds (adjusted for validation, was 60s)
        ),
        grid=GRID_NML(
            name="SMC0512 Grid",
            nml="../input/namelists_SMC0512.nml",
            type="SMC",  # SMC Grid type
            coord="SPHE",
            clos="NONE",
            zlim=-0.1,
            dmin=10.0,
        ),
        rect=Rect(
            # Base rectilinear grid parameters for SMC grid extent
            nx=256,
            ny=128,
            sx=0.02000,  # 0.02 degrees longitude
            sy=0.01600,  # 0.016 degrees latitude
            x0=276.41000,  # Lake Erie region
            y0=41.02800,
            sf=1.0,
            sf0=1.0,
        ),
        smc=Smc(
            # SMC-specific grid files
            mcel=SMCFile(
                filename=WW3DataBlob(source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.10/input/ErieSMCel.dat"),
            ),
            iside=SMCFile(
                filename=WW3DataBlob(source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.10/input/ErieISide.dat"),
            ),
            jside=SMCFile(
                filename=WW3DataBlob(source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.10/input/ErieJSide.dat"),
            ),
            subtr=SMCFile(
                filename=WW3DataBlob(source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.10/input/ErieObstr.dat"),
            ),
        ),
        depth=Depth(
            sf=-1.0,  # Depth scale factor
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
            timestart="19680606 000000",
            timestride="3600",  # 1 hour output
            timecount="1000000000",
            list="WND HS T01",
            partition="0 1 2",
            type="4",
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
    print("Creating WW3 tp2.10 configuration (SMC Grid)...")
    config = create_ww3_tp2_10_config()

    # Create model run
    period = TimeRange(
        start="19680606T000000",
        end="19680606T060000",
    )

    model = ModelRun(
        run_id="ww3_tp2_10",
        output_dir="rompy_runs",
        period=period,
        config=config,
    )

    # Generate configuration files
    print("\nGenerating namelist files...")
    result = model()

    # Print summary
    if result:
        print("\n" + "=" * 70)
        print("✓ EXAMPLE COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print(f"\nConfiguration files generated in: {model.output_dir}")

        import os

        output_path = os.path.join(model.output_dir, model.run_id)
        if os.path.exists(output_path):
            files = [f for f in os.listdir(output_path) if f.endswith(".nml")]
            print(f"Files created: {len(files)}")
            for f in sorted(files):
                print(f"  - {f}")
    else:
        print("\n✗ Configuration generation failed")
        sys.exit(1)
