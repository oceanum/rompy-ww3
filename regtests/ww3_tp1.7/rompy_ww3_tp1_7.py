#!/usr/bin/env python3
"""
WW3 tp1.7 regression test: 1-D IG wave generation near shore.

Test: tp1.7 - IG Wave Generation
Reference: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.7

Physics: Tests infragravity wave generation with breaking, reflection (DB1, REF1, IG1)
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


def create_ww3_tp1_7_components():
    shell_component = Shel(
        domain=Domain(
            start="20120601 000000",
            stop="20120601 060000",
            iostyp=1,
        ),
        input_nml=Input(),
        output_type=OutputType(
            field={"list": "DPT HS T0M1 DIR SPR HIG EF P2L"},
            point={
                "file": WW3DataBlob(
                    source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp1.7/input/points.list"
                )
            },
        ),
        output_date=OutputDate(
            field={
                "start": "20120600 000000",
                "stride": "60",
                "stop": "20120625 000000",
            },
            point={
                "start": "20120600 000000",
                "stride": "60",
                "stop": "20120625 000000",
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
            freq1=0.010,
            nk=30,
            nth=24,
            thoff=0.0,
        ),
        run=Run(
            fldry=False,
            flcx=True,
            flcy=True,
            flcth=True,
            flck=True,
            flsou=True,
        ),
        timesteps=Timesteps(
            dtmax=15.0,
            dtxy=5.0,
            dtkth=5.0,
            dtmin=5.0,
        ),
        grid=GRID_NML(
            name="1-D IG WAVE GENERATION",
            nml="../input/namelists_1-D.nml",
            type="RECT",
            coord="SPHE",
            clos="NONE",
            zlim=-3.0,
            dmin=0.5,
        ),
        rect=Rect(
            nx=29,
            ny=3,
            sx=0.02,
            sy=0.1,
            x0=-0.02,
            y0=-0.1,
        ),
        depth=Depth(
            filename=WW3DataBlob(
                source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp1.7/input/1-D.depth",
            ),
            sf=-10.0,
            idf=50,
            idla=2,
        ),
        inbound_count=InboundCount(n_point=2),
        inbound_points=InboundPointList(
            points=[
                InboundPoint(
                    x_index=2,
                    y_index=2,
                    connect=False,
                ),
                InboundPoint(
                    x_index=2,
                    y_index=2,
                    connect=True,
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
            timestart="20120600 000000",
            timestride=60,
            timecount="999",
            list="DPT HS T0M1 DIR SPR HIG EF P2L",
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
    print("Creating WW3 configuration for ww3_tp1.7 regression test...")
    print("Test: IG wave generation with breaking and reflection")

    config = NMLConfig(**create_ww3_tp1_7_components())
    period = TimeRange(start="2012-06-01T00:00:00", duration="6h", interval="1m")

    model_run = ModelRun(
        run_id="ww3_tp1_7_regression",
        config=config,
        period=period,
        output_dir="rompy_runs",
    )
    model_run.generate()

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nThis test validates IG wave generation near shore.")


if __name__ == "__main__":
    main()
