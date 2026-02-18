#!/usr/bin/env python3
"""
WW3 tp2.7 regression test: Small unstructured grid with reflection.

This test validates unstructured grid handling with reflection physics (REF1).

Key configuration:
- Grid type: UNST (unstructured, 111 nodes)
- Coordinates: SPHE (spherical)
- Grid: ref1.msh (small triangular mesh)
- Forcing: Homogeneous wind input (8 m/s, 270°)
- Physics: Reflection enabled (REF1 source term)
- Inbound points: 19 boundary points
- Test Purpose: Validates reflection physics on unstructured grids
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
from rompy_ww3.namelists.grid import Grid as GRID_NML
from rompy_ww3.namelists.unst import Unst
from rompy_ww3.namelists.field import Field
from rompy_ww3.namelists.output_file import File as FileNml
from rompy_ww3.namelists.inbound import InboundCount, InboundPointList, InboundPoint
from rompy_ww3.namelists.homogeneous import HomogInput


def create_ww3_tp2_7_config():
    """Create rompy-ww3 configuration for ww3_tp2.7 regression test."""

    shell_component = Shel(
        domain=Domain(
            start="20030101 000000",
            stop="20030101 120000",
            iostyp=2,
        ),
        input_nml=Input(forcing={"winds": "H"}),
        output_type=OutputType(
            field={"list": "HS T02 T01 ABR UBR"},
            point={"file": WW3DataBlob(source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.7/input/points.list")},
        ),
        output_date=OutputDate(
            field={
                "start": "20030101 000000",
                "stride": "3600",
                "stop": "20031231 233000",
            },
            point={
                "start": "20030101 000000",
                "stride": "3600",
                "stop": "20031231 233000",
            },
        ),
        homog_count=HomogCount(n_wnd=1),
        homog_input=[
            HomogInput(
                name="WND",
                date="20020905 000000",
                value1=8.0,
                value2=270.0,
                value3=0.0,
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
            flsou=True,
        ),
        timesteps=Timesteps(
            dtmax=600.0,
            dtxy=200.0,
            dtkth=200.0,
            dtmin=10.0,
        ),
        grid=GRID_NML(
            name="REF-UG",
            type="UNST",
            coord="SPHE",
            clos="NONE",
            zlim=-0.1,
            dmin=0.30,
        ),
        unst=Unst(
            sf=-1.0,
            filename=WW3DataBlob(source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.7/input/ref1.msh"),
            idf=20,
            idla=4,
            idfm=1,
            format="(20f10.2)",
            ugobcfile="../input/ref1.mshb",
        ),
        inbound_count=InboundCount(n_point=19),
        inbound_points=InboundPointList(
            points=[
                InboundPoint(x_index=1, y_index=1, connect=False),
                InboundPoint(x_index=19, y_index=1, connect=True),
                InboundPoint(x_index=70, y_index=1, connect=False),
                InboundPoint(x_index=53, y_index=1, connect=False),
                InboundPoint(x_index=107, y_index=1, connect=False),
                InboundPoint(x_index=62, y_index=1, connect=False),
                InboundPoint(x_index=41, y_index=1, connect=False),
                InboundPoint(x_index=110, y_index=1, connect=False),
                InboundPoint(x_index=90, y_index=1, connect=False),
                InboundPoint(x_index=88, y_index=1, connect=False),
                InboundPoint(x_index=86, y_index=1, connect=False),
                InboundPoint(x_index=87, y_index=1, connect=False),
                InboundPoint(x_index=79, y_index=1, connect=False),
                InboundPoint(x_index=109, y_index=1, connect=False),
                InboundPoint(x_index=100, y_index=1, connect=False),
                InboundPoint(x_index=101, y_index=1, connect=False),
                InboundPoint(x_index=105, y_index=1, connect=False),
                InboundPoint(x_index=50, y_index=1, connect=False),
                InboundPoint(x_index=42, y_index=1, connect=False),
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
            timestart="20030101 000000",
            timestride="3600",
            timecount="999",
            list="HS ABR UBR",
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
    print("Creating WW3 configuration for ww3_tp2.7 regression test...")
    print("Small unstructured grid with reflection physics")

    config = create_ww3_tp2_7_config()
    period = TimeRange(start="2003-01-01T00:00:00", duration="12H", interval="1H")

    model_run = ModelRun(
        run_id="ww3_tp2_7",
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
