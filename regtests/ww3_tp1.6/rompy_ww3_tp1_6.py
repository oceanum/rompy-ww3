#!/usr/bin/env python3
"""
WW3 tp1.6 regression test: 1-D wave blocking with currents.

Test: tp1.6 - Wave Blocking with Currents
Reference: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.6

Physics: Tests wave-current interaction (flck=T) and wave blocking with strong opposing currents
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


def create_ww3_tp1_6_components():
    shell_component = Shel(
        domain=Domain(
            iostyp=1,
        ),
        input_nml=Input(
            forcing={
                "currents": "T",
            }
        ),
        output_type=OutputType(
            field={"list": "DPT CUR HS"},
            point={
                "file": WW3DataBlob(
                    source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp1.6/input/points.list"
                )
            },
        ),
        output_date=OutputDate(
            field={
                "start": "19680606 000000",
                "stride": "900",
                "stop": "19680616 000000",
            },
            point={
                "start": "19680606 000000",
                "stride": "900",
                "stop": "19680616 000000",
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
            freq1=0.18628,
            nk=15,
            nth=8,
            thoff=0.0,
        ),
        run=Run(
            fldry=False,
            flcx=True,
            flcy=False,
            flcth=False,
            flck=True,
            flsou=False,
        ),
        timesteps=Timesteps(
            dtmax=1800.0,
            dtxy=600.0,
            dtkth=300.0,
            dtmin=10.0,
        ),
        grid=GRID_NML(
            name="WAVE BLOCKING TEST",
            nml="../input/namelists_WAVE.nml",
            type="RECT",
            coord="CART",
            clos="NONE",
            zlim=-1.0,
            dmin=1.0,
        ),
        rect=Rect(
            nx=22,
            ny=3,
            sx=3000.0,
            sy=3000.0,
            x0=-3000.0,
            y0=-3000.0,
        ),
        depth=Depth(
            filename=WW3DataBlob(
                source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp1.6/input/WAVE.depth",
            ),
            sf=-1000.0,
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
            timestride=900,
            timecount="999",
            list="DPT CUR HS",
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
    print("Creating WW3 configuration for ww3_tp1.6 regression test...")
    print("Test: Wave blocking with currents (flck=T)")

    config = NMLConfig(**create_ww3_tp1_6_components())
    period = TimeRange(start="1968-06-06T00:00:00", duration="10d", interval="15m")

    model_run = ModelRun(
        run_id="ww3_tp1_6_regression",
        config=config,
        period=period,
        output_dir="rompy_runs",
    )
    model_run.generate()

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nThis test validates wave-current interaction and wave blocking.")


if __name__ == "__main__":
    main()
