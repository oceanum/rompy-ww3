#!/usr/bin/env python3
"""
WW3 tp2.13 regression test: Regional Configuration (Curvilinear Grid).

This test validates curvilinear grid handling in regional mode with NONE closure.

Key configuration:
- Grid type: CURV (curvilinear, 1500x200)
- Coordinates: SPHE (spherical)
- Closure: NONE (regional, no wrapping)
- Grid files: lon.1500x200, lat.1500x200, depth.1500x200, mask1.1500x200
- Forcing: None (pure propagation)
- Test Purpose: Validates regional boundary handling with curvilinear grids
"""

from rompy.model import ModelRun
from rompy.core.time import TimeRange
from rompy_ww3.core.data import WW3DataBlob

from rompy_ww3.config import NMLConfig

from rompy_ww3.components import Shel, Grid

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


def create_ww3_tp2_13_config():
    """Create rompy-ww3 configuration for ww3_tp2.13 regression test."""

    shell_component = Shel(
        domain=Domain(
            start="20080522 000000",
            stop="20080522 090000",
            iostyp=1,
        ),
        input_nml=Input(),
        output_type=OutputType(
            field={"list": "DPT HS FP DIR SPR"},
            point={
                "file": WW3DataBlob(
                    source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.13/input/points.list"
                )
            },
        ),
        output_date=OutputDate(
            field={
                "start": "20080522 000000",
                "stride": "3600",
                "stop": "20080525 000000",
            },
            point={
                "start": "20090522 000000",
                "stride": "3600",
                "stop": "20090525 000000",
            },
        ),
        homog_count=HomogCount(),
    )

    grid_component = Grid(
        spectrum=Spectrum(
            xfr=1.1,
            freq1=0.03679,
            nk=3,
            nth=72,
            thoff=0.0,
        ),
        run=Run(
            fldry=False,
            flcx=True,
            flcy=True,
            flcth=True,
            flck=False,
            flsou=False,
        ),
        timesteps=Timesteps(
            dtmax=900.0,
            dtxy=300.0,
            dtkth=300.0,
            dtmin=60.0,
        ),
        grid=GRID_NML(
            name="2-D PROPAGATION TEST 2.13",
            nml="../input/namelists_2-D.nml",
            type="CURV",
            coord="SPHE",
            clos="NONE",
            zlim=-0.1,
            dmin=7.50,
        ),
        curv=Curv(
            nx=1500,
            ny=200,
            xcoord=CoordData(
                sf=1.0,
                off=0.0,
                filename="./../input/lon.1500x200",
            ),
            ycoord=CoordData(
                sf=1.0,
                off=0.0,
                filename="./../input/lat.1500x200",
            ),
        ),
        depth=Depth(
            sf=-1.0,
            filename="./../input/depth.1500x200",
        ),
        mask=Mask(
            filename="../input/mask1.1500x200",
        ),
    )

    return NMLConfig(
        shell_component=shell_component,
        grid_component=grid_component,
    )


def main():
    """Main function to demonstrate the WW3 configuration."""
    print("Creating WW3 configuration for ww3_tp2.13 regression test...")
    print("Regional configuration with curvilinear grid and NONE closure")

    config = create_ww3_tp2_13_config()
    period = TimeRange(start="2008-05-22T00:00:00", duration="9H", interval="1H")

    model_run = ModelRun(
        run_id="ww3_tp2_13",
        config=config,
        period=period,
        output_dir="rompy",
    )
    model_run.generate()

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    main()
