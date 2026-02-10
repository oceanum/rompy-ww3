#!/usr/bin/env python3
"""
WW3 tp1.5 regression test: 1-D spectral refraction in Y-direction with no source terms.

Test: tp1.5 - 1-D Spectral Refraction (Y-direction)
Reference: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.5

Physics: Tests spectral refraction (flcth=T) in Y-direction propagation
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


def create_ww3_tp1_5_components():
    shell_component = Shel(
        domain=Domain(
            stop="19680606 120000",
            iostyp=1,
        ),
        input_nml=Input(),
        output_type=OutputType(
            field={"list": "HS T01 FP DIR"},
            point={"file": WW3DataBlob(source="regtests/ww3_tp1.5/input/points.list")},
        ),
        output_date=OutputDate(
            field={
                "start": "19680606 000000",
                "stride": "900",
                "stop": "19680606 120000",
            },
            point={
                "start": "19680606 000000",
                "stride": "900",
                "stop": "19680606 120000",
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
            xfr=1.25,
            freq1=0.08,
            nk=3,
            nth=24,
            thoff=0.0,
        ),
        run=Run(
            fldry=False,
            flcx=False,
            flcy=True,
            flcth=True,
            flck=False,
            flsou=False,
        ),
        timesteps=Timesteps(
            dtmax=900.0,
            dtxy=300.0,
            dtkth=150.0,
            dtmin=10.0,
        ),
        grid=GRID_NML(
            name="1-D REFRACTION Y",
            type="RECT",
            coord="CART",
            clos="NONE",
            zlim=-1.0,
            dmin=1.0,
        ),
        rect=Rect(
            nx=3,
            ny=13,
            sx=5000.0,
            sy=5000.0,
            x0=-5000.0,
            y0=-5000.0,
        ),
        depth=Depth(
            filename=WW3DataBlob(
                source="regtests/ww3_tp1.5/input/1-D.depth",
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
                )
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
            timestride="900",
            timecount="999",
            list="HS T01 FP DIR",
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
    print("Creating WW3 configuration for ww3_tp1.5 regression test...")
    print("Test: 1-D spectral refraction (Y-direction) with no source terms")

    config = NMLConfig(**create_ww3_tp1_5_components())
    period = TimeRange(start="1968-06-06T00:00:00", duration="12h", interval="15m")

    model_run = ModelRun(
        run_id="ww3_tp1_5_regression",
        config=config,
        period=period,
        output_dir="rompy_runs",
    )
    model_run.generate()

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nThis test validates 1-D spectral refraction in Y-direction.")


if __name__ == "__main__":
    main()
