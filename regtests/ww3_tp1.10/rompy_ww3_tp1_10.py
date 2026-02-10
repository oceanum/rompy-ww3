#!/usr/bin/env python3
"""
WW3 tp1.10 regression test: Bottom scattering.

Test: tp1.10 - Bottom Scattering
Reference: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.10

Physics: Tests bottom scattering physics (BS1 source term) on propagating waves
"""

from rompy.model import ModelRun
from rompy.core.time import TimeRange
from rompy_ww3.core.data import WW3DataBlob
from rompy_ww3.config import NMLConfig
from rompy_ww3.components import Shel, Grid, Namelists, Ounf
from rompy_ww3.components.namelists import PRO3, PRO4
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
from rompy_ww3.namelists.depth import Depth
from rompy_ww3.namelists.field import Field
from rompy_ww3.namelists.output_file import File as FileNml
from rompy_ww3.namelists.inbound import InboundCount, InboundPointList, InboundPoint


def create_ww3_tp1_10_components():
    """
    tp1.10: Bottom scattering on 1-D propagation domain.

    Key features:
    - Cartesian grid: 51x3, 2 km resolution
    - Spectrum: 24 frequencies (0.04 Hz), 120 directions
    - Source terms enabled for bottom scattering (BS1)
    - Moderate timesteps: dtxy=80s for 2km resolution
    - 1-D propagation with spectral processes
    """
    shell_component = Shel(
        domain=Domain(
            start="19680601 000000",
            stop="19680601 180000",
            iostyp=1,
        ),
        input_nml=Input(),
        output_type=OutputType(
            field={"list": "HS DIR SPR"},
            point={"file": WW3DataBlob(source="regtests/ww3_tp1.10/input/points.list")},
        ),
        output_date=OutputDate(
            field={
                "start": "19680601 000000",
                "stride": "1200",
                "stop": "19680625 000000",
            },
            point={
                "start": "19680601 000000",
                "stride": "1200",
                "stop": "19680625 000000",
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

    grid_component = Grid(
        spectrum=Spectrum(
            xfr=1.1,
            freq1=0.04,
            nk=24,
            nth=120,
            thoff=0.0,
        ),
        run=Run(
            fldry=False,
            flcx=True,
            flcy=False,
            flcth=False,
            flck=False,
            flsou=True,
        ),
        timesteps=Timesteps(
            dtmax=240.0,
            dtxy=80.0,
            dtkth=80.0,
            dtmin=5.0,
        ),
        grid=GRID_NML(
            name="1-D PROPAGATION SCATTERING",
            nml="../input/namelists_1-D.nml",
            type="RECT",
            coord="CART",
            clos="NONE",
            zlim=-5.0,
            dmin=5.75,
        ),
        rect=Rect(
            nx=51,
            ny=3,
            sx=2000.0,
            sy=2000.0,
            x0=0.0,
            y0=-2000.0,
        ),
        depth=Depth(
            filename=WW3DataBlob(
                source="regtests/ww3_tp1.10/input/1-D.depth",
            ),
            sf=-20.0,
            idf=50,
            idla=2,
        ),
        inbound_count=InboundCount(n_point=1),
        inbound_points=InboundPointList(
            points=[
                InboundPoint(
                    x_index=50,
                    y_index=2,
                    connect=False,
                ),
            ]
        ),
    )

    namelists_component = Namelists(
        pro3=PRO3(wdthcg=0.0, wdthth=0.0),
        pro4=PRO4(rnfac=0.0, rsfac=0.0),
    )

    field_output_component = Ounf(
        field=Field(
            timestart="19680601 000000",
            timestride="1200",
            timecount="999",
            list="HS DIR SPR",
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

    return {
        "shell_component": shell_component,
        "grid_component": grid_component,
        "parameters_component": namelists_component,
        "field_output_component": field_output_component,
    }


def main():
    print("Creating WW3 configuration for ww3_tp1.10 regression test...")
    print("Test: Bottom scattering (BS1 source term)")

    config = NMLConfig(**create_ww3_tp1_10_components())
    period = TimeRange(start="1968-06-01T00:00:00", duration="18h", interval="20m")

    model_run = ModelRun(
        run_id="ww3_tp1_10_regression",
        config=config,
        period=period,
        output_dir="rompy_runs",
    )
    model_run.generate()

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nThis test validates bottom scattering physics.")
    print("Key features:")
    print("  - Bottom scattering (BS1 source term)")
    print("  - Cartesian grid: 51x3, 2 km resolution")
    print("  - High directional resolution (120 directions)")
    print("  - Moderate timesteps (80s) for 2km scale")


if __name__ == "__main__":
    main()
