#!/usr/bin/env python3
"""
WW3 tp2.11 regression test: Curvilinear grid with full physics (ST4).

This test validates curvilinear grid propagation with the full ST4 physics package,
combining spatial complexity with complete wave physics simulation.

Key configuration:
- Grid type: CURV (curvilinear)
- Coordinates: SPHE (spherical)
- Grid: Quarter annulus shape (121×121 points)
- Physics: ST4 package (SIN4, SNL4, SDS4, SBT1)
- Source terms: Full physics enabled (flsou=True)
- Test Purpose: Validates curvilinear grids with complete physics

Run with:
    python rompy_ww3_tp2_11.py
"""

import sys
from rompy.model import ModelRun
from rompy.core.time import TimeRange
from rompy_ww3.core.data import WW3DataBlob

from rompy_ww3.config import NMLConfig

from rompy_ww3.components import Shel, Grid, Namelists, Ounf
from rompy_ww3.components.namelists import (
    SIN4,
    SNL4,
    SDS4,
    SBT,
    PRO2,
    PRO3,
    PRO4,
)

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
from rompy_ww3.namelists.obstacle import Obstacle
from rompy_ww3.namelists.field import Field
from rompy_ww3.namelists.output_file import File as FileNml
from rompy_ww3.namelists.homogeneous import HomogInput


def create_ww3_tp2_11_config():
    """Create rompy-ww3 configuration for ww3_tp2.11 regression test.

    Combines curvilinear grid handling with full ST4 physics package.
    """

    # Shell component for ww3_shel.nml
    shell_component = Shel(
        domain=Domain(
            start="19680606 000000",
            stop="19680607 000000",
            iostyp=1,
        ),
        input_nml=Input(
            forcing={"winds": "H"},  # Homogeneous wind forcing for physics
        ),
        output_type=OutputType(
            field={"list": "HS T01 FP DIR SPR WND"},
        ),
        output_date=OutputDate(
            field={
                "start": "19680606 000000",
                "stride": "10800",  # 3 hour output
                "stop": "19680607 000000",
            },
        ),
        homog_count=HomogCount(
            n_wnd=1,  # One wind input
            n_lev=0,
            n_cur=0,
            n_ice=0,
        ),
        homog_input=[
            HomogInput(
                name="WND",
                date="19680606 000000",
                value1=20.0,  # Wind speed (m/s)
                value2=270.0,  # Wind direction (degrees - westerly)
                value3=0.0,
            )
        ],
    )

    # Grid component for ww3_grid.nml with curvilinear configuration
    grid_component = Grid(
        spectrum=Spectrum(
            xfr=1.1,
            freq1=0.035,
            nk=25,  # More frequencies for full physics
            nth=24,  # More directions for full physics
            thoff=0.0,
        ),
        run=Run(
            flcx=True,  # X-direction propagation
            flcy=True,  # Y-direction propagation
            flcth=False,  # No spectral refraction
            flck=False,  # No wavenumber shift
            flsou=True,  # Source terms ENABLED for full physics
        ),
        timesteps=Timesteps(
            dtmax=900.0,  # 15 minutes (adjusted: 3× dtxy for validation)
            dtxy=300.0,  # 5 minutes
            dtkth=450.0,  # 7.5 minutes (dtmax/2)
            dtmin=10.0,  # 10 seconds
        ),
        grid=GRID_NML(
            name="Curvilinear grid with full physics (ST4)",
            nml="../input/namelists_ST4.nml",
            type="CURV",
            coord="SPHE",
            clos="NONE",
            zlim=-0.10,
            dmin=2.50,
        ),
        curv=Curv(
            nx=121,
            ny=121,
            xcoord=CoordData(
                filename=WW3DataBlob(
                    source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.9/input/curv_2d.lon"
                ),
                sf=0.0001,
                off=0.0,
                idf=11,
                idla=1,
                idfm=1,
                format="(....)",
            ),
            ycoord=CoordData(
                filename=WW3DataBlob(
                    source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.9/input/curv_2d.lat"
                ),
                sf=0.0001,
                off=0.0,
                idf=12,
                idla=1,
                idfm=1,
                format="(....)",
            ),
        ),
        depth=Depth(
            filename=WW3DataBlob(
                source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.9/input/curv_2d.bot"
            ),
            sf=0.001,
        ),
        mask=Mask(
            filename=WW3DataBlob(
                source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.9/input/curv_2d.mask"
            ),
        ),
        obstacle=Obstacle(
            filename=WW3DataBlob(
                source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.9/input/curv_2d.obs"
            ),
            sf=0.01,
        ),
    )

    # Parameters component for namelists.nml with full ST4 physics
    parameters_component = Namelists(
        sin4=SIN4(),  # ST4 wind input
        snl4=SNL4(),  # ST4 nonlinear interactions
        sds4=SDS4(),  # ST4 whitecapping dissipation
        sbt=SBT(),  # Bottom friction
        pro2=PRO2(dtime=0.0),
        pro3=PRO3(wdthcg=0.0, wdthth=0.0),
        pro4=PRO4(rnfac=0.0, rsfac=0.0),
    )

    # Field output component for ww3_ounf.nml
    field_output_component = Ounf(
        field=Field(
            timestart="19680606 000000",
            timestride=10800,  # 3 hour output
            timecount="1000000000",
            list="HS T01 FP DIR SPR WND",
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
        ww3_shel=shell_component,
        ww3_grid=grid_component,
        namelists=parameters_component,
        ww3_ounf=field_output_component,
    )

    return config


if __name__ == "__main__":
    print("Creating WW3 tp2.11 configuration (Curvilinear + ST4 Physics)...")
    config = create_ww3_tp2_11_config()

    # Create model run
    period = TimeRange(
        start="19680606T000000",
        end="19680607T000000",
    )

    model = ModelRun(
        run_id="ww3_tp2_11",
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
