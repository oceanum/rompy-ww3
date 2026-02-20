#!/usr/bin/env python3
"""
WW3 tp2.9 regression test: 2-D propagation with obstruction grids.

This test validates propagation with obstruction/mask handling on both rectilinear
and curvilinear grids. It demonstrates the use of MASK_NML and OBST_NML namelists.

Two grid configurations are provided:
- Grid A: 121×141 rectilinear grid (French Polynesian Islands)
- Grid B: 121×121 curvilinear grid (quarter annulus shape)

Key configuration:
- Grid types: RECT (grid_a) and CURV (grid_b)
- Coordinates: SPHE (spherical)
- Physics: No source terms (pure propagation)
- Special features: Obstruction and mask files
- Test Purpose: Validates obstruction/transparency physics and masking

Run with:
    python rompy_ww3_tp2_9.py           # Default: grid_a (rectilinear)
    python rompy_ww3_tp2_9.py --grid b  # Grid B (curvilinear)
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
from rompy_ww3.namelists.curv import Curv, CoordData
from rompy_ww3.namelists.depth import Depth
from rompy_ww3.namelists.mask import Mask
from rompy_ww3.namelists.obstacle import Obstacle
from rompy_ww3.namelists.field import Field
from rompy_ww3.namelists.output_file import File as FileNml


def create_ww3_tp2_9_config(grid_variant="a"):
    """Create rompy-ww3 configuration for ww3_tp2.9 regression test.

    Args:
        grid_variant: 'a' for rectilinear grid, 'b' for curvilinear grid
    """

    if grid_variant.lower() == "a":
        # Grid A: Rectilinear 121×141 grid
        grid_name = "2D Propagation with obstructions (rectilinear grid)"
        grid_nml = GRID_NML(
            name=grid_name,
            nml="../input/namelists_a.nml",
            type="RECT",
            coord="SPHE",
            clos="NONE",
            zlim=-0.10,
            dmin=2.50,
        )

        rect = Rect(
            nx=121,
            ny=141,
            sx=0.25,
            sy=0.25,
            x0=200.0,
            y0=-30.0,
            sf=1.0,
            sf0=1.0,
        )

        depth = Depth(
            filename=WW3DataBlob(
                source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.9/input/rect_2d.bot"
            ),
            sf=0.001,
        )

        mask = Mask(
            filename=WW3DataBlob(
                source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.9/input/rect_2d.mask"
            ),
        )

        obstacle = Obstacle(
            filename=WW3DataBlob(
                source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.9/input/rect_2d.obs"
            ),
            sf=0.01,
        )

        curv = None

    elif grid_variant.lower() == "b":
        # Grid B: Curvilinear 121×121 grid (quarter annulus)
        grid_name = "2D Propagation with obstructions (curvilinear grid)"
        grid_nml = GRID_NML(
            name=grid_name,
            nml="../input/namelists_b.nml",
            type="CURV",
            coord="SPHE",
            clos="NONE",
            zlim=-0.10,
            dmin=2.50,
        )

        curv = Curv(
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
        )

        depth = Depth(
            filename=WW3DataBlob(
                source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.9/input/curv_2d.bot"
            ),
            sf=0.001,
        )

        mask = Mask(
            filename=WW3DataBlob(
                source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.9/input/curv_2d.mask"
            ),
        )

        obstacle = Obstacle(
            filename=WW3DataBlob(
                source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.9/input/curv_2d.obs"
            ),
            sf=0.01,
        )

        rect = None

    else:
        raise ValueError(f"Invalid grid variant: {grid_variant}. Must be 'a' or 'b'")

    # Shell component for ww3_shel.nml
    shell_component = Shel(
        domain=Domain(
            start="19680606 000000",
            stop="19680607 000000",
            iostyp=1,
        ),
        input_nml=Input(
            forcing={},  # No forcing - pure propagation
        ),
        output_type=OutputType(
            field={"list": "HS T01 FP DIR"},
        ),
        output_date=OutputDate(
            field={
                "start": "19680606 000000",
                "stride": "10800",
                "stop": "19680607 000000",
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

    # Grid component for ww3_grid.nml
    grid_component = Grid(
        spectrum=Spectrum(
            xfr=1.1,
            freq1=0.035,
            nk=3,
            nth=36,
            thoff=0.0,
        ),
        run=Run(
            flcx=True,
            flcy=True,
            flcth=False,
            flck=False,
            flsou=False,
        ),
        timesteps=Timesteps(
            dtmax=900.0,  # 15 minutes (adjusted: 3× dtxy for validation)
            dtxy=300.0,  # 5 minutes
            dtkth=450.0,  # 7.5 minutes (dtmax/2)
            dtmin=10.0,  # 10 seconds (adjusted for validation, was 360s)
        ),
        grid=grid_nml,
        rect=rect,
        curv=curv,
        depth=depth,
        mask=mask,
        obstacle=obstacle,
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
            timestride=10800,  # 3 hour output
            timecount="1000000000",
            list="HS T01 FP DIR",
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
    # Check for grid variant argument
    grid_variant = "a"  # Default to rectilinear grid
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--grid", "-g"]:
            if len(sys.argv) > 2:
                grid_variant = sys.argv[2]
        else:
            grid_variant = sys.argv[1]

    print(f"Creating WW3 tp2.9 configuration (grid variant: {grid_variant})...")
    config = create_ww3_tp2_9_config(grid_variant=grid_variant)

    # Create model run
    period = TimeRange(
        start="19680606T000000",
        end="19680607T000000",
    )

    model = ModelRun(
        run_id=f"ww3_tp2_9_{grid_variant}",
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
        print(f"\nGrid variant: {grid_variant.upper()}")
        print(f"Configuration files generated in: {model.output_dir}")

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
