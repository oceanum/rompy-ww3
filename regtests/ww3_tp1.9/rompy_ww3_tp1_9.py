#!/usr/bin/env python3
"""
WW3 tp1.9 regression test: Nonlinear shoaling with triad interactions.

Test: tp1.9 - Nonlinear Shoaling (Triad Interactions)
Reference: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.9

Physics: Tests triad interaction physics (TR1) for Beji & Battjes (1993) barred flume case
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


def create_ww3_tp1_9_components():
    """
    tp1.9: Nonlinear shoaling with triad interactions (Beji & Battjes 1993).

    Key features:
    - Cartesian grid: 303x3, 0.1m resolution (flume scale)
    - Spectrum: 35 frequencies (0.10 Hz), 180 directions (high resolution)
    - Source terms enabled for triad interactions (TR1)
    - Very fine timesteps: dtxy=0.01s for laboratory-scale simulation
    - 1-D propagation with spectral processes
    """
    shell_component = Shel(
        domain=Domain(
            stop="19680606 000005",
            iostyp=1,
        ),
        input_nml=Input(),
        output_type=OutputType(
            field={"list": "DPT HS T0M1"},
            point={"file": WW3DataBlob(source="regtests/ww3_tp1.9/input/points.list")},
        ),
        output_date=OutputDate(
            field={
                "start": "19680606 000000",
                "stride": "5",
                "stop": "19680606 000200",
            },
            point={
                "start": "19680606 000000",
                "stride": "5",
                "stop": "19680606 000200",
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
            freq1=0.10,
            nk=35,
            nth=180,
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
            dtmax=0.03,
            dtxy=0.01,
            dtkth=0.01,
            dtmin=5.0,
        ),
        grid=GRID_NML(
            name="NONLINEAR SHOALING X",
            nml="../input/namelists_NONLINEAR.nml",
            type="RECT",
            coord="CART",
            clos="NONE",
            zlim=-0.08,
            dmin=0.08,
        ),
        rect=Rect(
            nx=303,
            ny=3,
            sx=0.1,
            sy=0.1,
            x0=-0.1,
            y0=-0.1,
        ),
        depth=Depth(
            filename=WW3DataBlob(
                source="regtests/ww3_tp1.9/input/NONLINEAR.depth",
            ),
            sf=-1.0,
            idf=50,
            idla=2,
        ),
        inbound_count=InboundCount(n_point=1),
        inbound_points=InboundPointList(
            points=[
                InboundPoint(
                    x_index=2,
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
            timestart="19680606 000000",
            timestride="5",
            timecount="999",
            list="DPT HS T0M1",
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
    print("Creating WW3 configuration for ww3_tp1.9 regression test...")
    print("Test: Nonlinear shoaling with triad interactions (Beji & Battjes 1993)")

    config = NMLConfig(**create_ww3_tp1_9_components())
    period = TimeRange(start="1968-06-06T00:00:00", duration="5s", interval="5s")

    model_run = ModelRun(
        run_id="ww3_tp1_9_regression",
        config=config,
        period=period,
        output_dir="rompy_runs",
    )
    model_run.generate()

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nThis test validates triad interaction physics for nonlinear shoaling.")
    print("Key features:")
    print("  - Triad interactions (TR1 source term)")
    print("  - Laboratory-scale flume (303x3, 0.1m resolution)")
    print("  - Very fine timesteps (0.01s) for lab-scale simulation")
    print("  - High directional resolution (180 directions)")


if __name__ == "__main__":
    main()
