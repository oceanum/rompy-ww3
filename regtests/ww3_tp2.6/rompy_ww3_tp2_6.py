#!/usr/bin/env python3
"""
WW3 tp2.6 regression test: Unstructured grid example (Limon harbour, Costa Rica).

This test validates propagation on an unstructured triangular grid with wind forcing.

Key configuration:
- Grid type: UNST (unstructured)
- Coordinates: SPHE (spherical)
- Grid: limon_ll.msh (111 nodes triangular mesh)
- Forcing: Homogeneous wind input
- Test Purpose: Validates unstructured grid handling with simple wind forcing
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


def create_ww3_tp2_6_config():
    """Create rompy-ww3 configuration for ww3_tp2.6 regression test."""

    shell_component = Shel(
        domain=Domain(
            start="20100801 000000",
            stop="20100801 001000",  # 10 minute run
            iostyp=1,
        ),
        input_nml=Input(
            forcing={"winds": "H"}  # Homogeneous wind forcing
        ),
        output_type=OutputType(
            field={"list": "HS LM T02 T01 T0M1 UST CHA CGE DTD FC CFX CFD QP QKK"},
            point={"file": WW3DataBlob(source="regtests/ww3_tp2.6/input/points.list")},
        ),
        output_date=OutputDate(
            field={
                "start": "20071101 000000",
                "stride": "10",
                "stop": "20121231 233000",
            },
            point={
                "start": "20071101 000000",
                "stride": "60",
                "stop": "20121231 233000",
            },
        ),
        homog_count=HomogCount(n_wnd=1),
        homog_input=[
            HomogInput(
                name="WND",
                date="20020905 000000",
                value1=30.0,  # Wind speed (m/s)
                value2=180.0,  # Wind direction (degrees)
                value3=0.0,
            )
        ],
    )

    grid_component = Grid(
        spectrum=Spectrum(
            xfr=1.1,
            freq1=0.05,
            nk=36,  # 36 frequencies
            nth=36,  # 36 directions
            thoff=0.0,
        ),
        run=Run(
            fldry=False,
            flcx=True,
            flcy=True,
            flcth=False,
            flck=False,
            flsou=False,
        ),
        timesteps=Timesteps(
            dtmax=3.0,  # Adjusted for validation (3× dtxy)
            dtxy=1.0,
            dtkth=1.5,
            dtmin=5.0,
        ),
        grid=GRID_NML(
            name="LIMON",
            type="UNST",  # Unstructured grid
            coord="SPHE",
            clos="NONE",
            zlim=-0.1,  # Adjusted to satisfy validation (must be ≤ 0)
            dmin=0.10,
        ),
        unst=Unst(
            sf=-1.0,
            filename=WW3DataBlob(source="regtests/ww3_tp2.6/input/limon_ll.msh"),
            idf=20,
            idla=4,
            idfm=1,
            format="(20f10.2)",
        ),
        inbound_count=InboundCount(n_point=2),
        inbound_points=InboundPointList(
            points=[
                InboundPoint(x_index=66, y_index=1, connect=False),
                InboundPoint(x_index=99, y_index=1, connect=True),
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
            timestart="20100801 000000",
            timestride="10",
            timecount="999",
            list="HS",
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
    print("Creating WW3 configuration for ww3_tp2.6 regression test...")
    print("Limon harbour (Costa Rica) - unstructured triangular mesh")

    config = create_ww3_tp2_6_config()
    period = TimeRange(start="2010-08-01T00:00:00", duration="10M", interval="1M")

    model_run = ModelRun(
        run_id="ww3_tp2_6",
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
