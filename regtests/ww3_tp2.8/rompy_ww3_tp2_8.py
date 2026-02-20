#!/usr/bin/env python3
"""
WW3 tp2.8 regression test: Regular grid (Brest region) with currents.

This test validates RECT grid handling with current forcing from external files.

Key configuration:
- Grid type: RECT (regular rectilinear)
- Coordinates: SPHE (spherical)
- Grid size: 103×119 points (Ir oise region, France)
- Resolution: 0.019° × 0.0125° (~1.5 km)
- Forcing: Currents (external file) + homogeneous wind
- Inbound points: 6 boundary points
- Test Purpose: Validates current forcing with regular grids
"""

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
from rompy_ww3.namelists.depth import Depth
from rompy_ww3.namelists.field import Field
from rompy_ww3.namelists.output_file import File as FileNml
from rompy_ww3.namelists.inbound import InboundCount, InboundPointList, InboundPoint
from rompy_ww3.namelists.homogeneous import HomogInput


def create_ww3_tp2_8_config():
    """Create rompy-ww3 configuration for ww3_tp2.8 regression test."""

    shell_component = Shel(
        domain=Domain(
            start="20080310 063000",
            stop="20080310 071000",
            iostyp=1,
        ),
        input_nml=Input(
            forcing={
                "currents": "T",
                "winds": "H",
            }
        ),
        output_type=OutputType(
            field={"list": "DPT CUR HS FP DIR SPR"},
            point={
                "file": WW3DataBlob(
                    source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.8/input/points.list"
                )
            },
        ),
        output_date=OutputDate(
            field={
                "start": "20080310 000000",
                "stride": "600",
                "stop": "20080525 000000",
            },
            point={
                "start": "20080310 000000",
                "stride": "600",
                "stop": "20080523 000000",
            },
        ),
        homog_count=HomogCount(n_wnd=1),
        homog_input=[
            HomogInput(
                name="WND",
                date="20080310 063000",
                value1=2.0,
                value2=270.0,
                value3=-10.0,
            )
        ],
    )

    grid_component = Grid(
        spectrum=Spectrum(
            xfr=1.1,
            freq1=0.0373,
            nk=32,
            nth=24,
            thoff=0.0,
        ),
        run=Run(
            fldry=False,
            flcx=True,
            flcy=True,
            flcth=True,
            flck=True,
            flsou=False,
        ),
        timesteps=Timesteps(
            dtmax=135.0,
            dtxy=45.0,
            dtkth=45.0,
            dtmin=10.0,
        ),
        grid=GRID_NML(
            name="IROISE 1.5KM",
            type="RECT",
            coord="SPHE",
            clos="NONE",
            zlim=-0.1,
            dmin=1.0,
        ),
        rect=Rect(
            nx=103,
            ny=119,
            sx=0.019,
            sy=0.0125,
            x0=-6.119,
            y0=47.6375,
        ),
        depth=Depth(
            sf=-1.0,
            filename=WW3DataBlob(
                source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.8/input/iro_1p5k.bot"
            ),
            idf=50,
            idla=1,
        ),
        inbound_count=InboundCount(n_point=6),
        inbound_points=InboundPointList(
            points=[
                InboundPoint(x_index=102, y_index=86, connect=False),
                InboundPoint(x_index=102, y_index=118, connect=True),
                InboundPoint(x_index=2, y_index=118, connect=True),
                InboundPoint(x_index=2, y_index=2, connect=True),
                InboundPoint(x_index=102, y_index=2, connect=True),
                InboundPoint(x_index=102, y_index=11, connect=True),
            ]
        ),
    )

    namelists_component = Namelists(
        pro2=PRO2(dtime=64800.0),
        pro3=PRO3(wdthcg=1.5, wdthth=1.5),
        pro4=PRO4(rnfac=0.0, rsfac=0.0),
    )

    field_output_component = Ounf(
        field=Field(
            timestart="20080310 063000",
            timestride=600,
            timecount="999",
            list="HS CUR",
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
    print("Creating WW3 configuration for ww3_tp2.8 regression test...")
    print("Iroise region (France) - regular grid with current forcing")

    config = create_ww3_tp2_8_config()
    period = TimeRange(start="2008-03-10T06:30:00", duration="80M", interval="10M")

    model_run = ModelRun(
        run_id="ww3_tp2_8",
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
