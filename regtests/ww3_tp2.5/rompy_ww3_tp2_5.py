#!/usr/bin/env python3
"""
WW3 tp2.5 regression test: Arctic region on polar stereographic (curvilinear) grid.

This test validates 2-D propagation on a curvilinear grid with spherical coordinates.
The grid covers the Arctic region using a polar stereographic projection.

Key configuration:
- Grid type: CURV (curvilinear)
- Coordinates: SPHE (spherical)
- Grid size: 361×361 points
- No source terms (!/ST0 - pure propagation)
- Test Purpose: Validates curvilinear grid handling in Arctic region
"""

from rompy.model import ModelRun
from rompy.core.time import TimeRange
from rompy_ww3.core.data import WW3DataBlob

from rompy_ww3.config import NMLConfig

# Import component models
from rompy_ww3.components import Shel, Grid, Namelists, Ounf
from rompy_ww3.components.namelists import PRO2, PRO3, PRO4

# Import namelist objects
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
from rompy_ww3.namelists.field import Field
from rompy_ww3.namelists.output_file import File as FileNml


def create_ww3_tp2_5_config():
    """Create rompy-ww3 configuration for ww3_tp2.5 regression test."""

    # Shell component for ww3_shel.nml (main model configuration)
    shell_component = Shel(
        domain=Domain(
            start="20080522 000000",
            stop="20080522 120000",  # 12 hour run
            iostyp=1,
        ),
        input_nml=Input(),  # No forcing inputs
        output_type=OutputType(
            field={"list": "DPT HS FP DIR SPR"},
            point={"file": WW3DataBlob(source="regtests/ww3_tp2.5/input/points.list")},
        ),
        output_date=OutputDate(
            field={
                "start": "20080522 000000",
                "stride": "3600",  # Hourly output
                "stop": "20080525 000000",
            },
            point={
                "start": "20080522 000000",
                "stride": "3600",
                "stop": "20080525 000000",
            },
        ),
        homog_count=HomogCount(
            n_wnd=0,  # No wind forcing
            n_lev=0,
            n_cur=0,
            n_ice=0,
        ),
        homog_input=[],
    )

    # Grid component for ww3_grid.nml (grid preprocessing configuration)
    # tp2.5 uses curvilinear grid with separate coordinate files
    grid_component = Grid(
        spectrum=Spectrum(
            xfr=1.1,
            freq1=0.03679,
            nk=3,
            nth=12,  # 12 directional bins
            thoff=0.0,
        ),
        run=Run(
            fldry=False,
            flcx=True,  # X-component propagation
            flcy=True,  # Y-component propagation
            flcth=True,  # Direction shift (refraction)
            flck=False,  # No wavenumber shift
            flsou=False,  # No source terms (LN0 ST0 NL0 BT0 DB0 TR0 BS0)
        ),
        timesteps=Timesteps(
            dtmax=1650.0,  # Adjusted to satisfy dtmax ≈ 3×dtxy
            dtxy=550.0,  # Propagation timestep (from official)
            dtkth=825.0,  # Between dtmax/10 and dtmax/2
            dtmin=10.0,  # Minimum timestep
        ),
        grid=GRID_NML(
            name="2-D PROPAGATION TEST 2.5",
            type="CURV",  # Curvilinear grid
            coord="SPHE",  # Spherical coordinates
            clos="NONE",  # No closure
            zlim=-0.1,
            dmin=7.50,
        ),
        curv=Curv(
            nx=361,
            ny=361,
            xcoord=CoordData(
                sf=1.0,
                off=0.0,
                filename=WW3DataBlob(
                    source="regtests/ww3_tp2.5/input/lon.361x361.IDLA1.dat"
                ),
                idf=21,
                idla=1,
                idfm=1,
                format="(....)",
            ),
            ycoord=CoordData(
                sf=1.0,
                off=0.0,
                filename=WW3DataBlob(
                    source="regtests/ww3_tp2.5/input/lat.361x361.IDLA1.dat"
                ),
                idf=22,
                idla=1,
                idfm=1,
                format="(....)",
            ),
        ),
        depth=Depth(
            filename=WW3DataBlob(
                source="regtests/ww3_tp2.5/input/depth.361x361.IDLA1.dat"
            ),
            sf=-1.0,
            idf=50,
            idla=1,
        ),
    )

    # Parameters component for namelists.nml
    namelists_component = Namelists(
        pro2=PRO2(dtime=64800.0),
        pro3=PRO3(wdthcg=1.5, wdthth=1.5),
        pro4=PRO4(rnfac=0.0, rsfac=0.0),
    )

    # Field output component for ww3_ounf.nml
    field_output_component = Ounf(
        field=Field(
            timestart="20080522 000000",
            timestride="3600",
            timecount="999",
            list="DPT HS",
            partition="0 1 2",
            type=4,
            samefile=True,
        ),
        file=FileNml(
            prefix="ww3.",
            netcdf=3,
            ix0=1,
            ixn=1000000000,
            iy0=1,
            iyn=1000000000,
        ),
    )

    return NMLConfig(
        shell_component=shell_component,
        grid_component=grid_component,
        parameters_component=namelists_component,
        field_output_component=field_output_component,
    )


def main():
    """Main function to demonstrate the WW3 configuration."""
    print("Creating WW3 configuration for ww3_tp2.5 regression test...")
    print("Arctic region on polar stereographic (curvilinear) grid")

    config = create_ww3_tp2_5_config()
    period = TimeRange(start="2008-05-22T00:00:00", duration="12H", interval="1H")

    model_run = ModelRun(
        run_id="ww3_tp2_5",
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
