#!/usr/bin/env python3
"""
WW3 tp1.3 regression test configuration using rompy-ww3.

Test: 1-D propagation on Cartesian grid with monochromatic shoaling (no source terms).
Physics: !/LN0 !/ST0 !/NL0 !/BT0 !/DB0 !/TR0 !/BS0 (no source terms)
Reference: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.3
"""

from rompy.model import ModelRun
from rompy.core.time import TimeRange
from rompy_ww3.core.data import WW3DataBlob

from rompy_ww3.config import NMLConfig

from rompy_ww3.components import (
    Shel,
    Grid,
    Namelists,
    Ounf,
)
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
from rompy_ww3.namelists.inbound import InboundCount, InboundPointList, InboundPoint
from rompy_ww3.namelists.field import Field
from rompy_ww3.namelists.output_file import File as FileNml


def create_ww3_tp1_3_components():
    """Create rompy-ww3 components for tp1.3 monochromatic shoaling test."""

    shell_component = Shel(
        domain=Domain(
            start="19680606 000000",
            stop="19680608 000000",
            iostyp=1,
        ),
        input_nml=Input(),
        output_type=OutputType(
            field={"list": "DPT HS FC CFX"},
        ),
        output_date=OutputDate(
            field={
                "start": "19680606 000000",
                "stride": "3600",
                "stop": "19680608 000000",
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
            nth=4,
            thoff=0.0,
        ),
        run=Run(
            fldry=False,
            flcx=True,
            flcy=False,
            flcth=False,
            flck=False,
            flsou=False,
        ),
        timesteps=Timesteps(
            dtmax=3600.0,
            dtxy=1200.0,
            dtkth=1800.0,
            dtmin=10.0,
        ),
        grid=GRID_NML(
            name="MONOCHROMATIC SHOALING X",
            type="RECT",
            coord="CART",
            clos="NONE",
            zlim=-1.0,
            dmin=1.0,
        ),
        rect=Rect(
            nx=43,
            ny=3,
            sx=15000.0,
            sy=15000.0,
            x0=-15000.0,
            y0=-15000.0,
        ),
        depth=Depth(
            filename=WW3DataBlob(
                source="regtests/ww3_tp1.3/input/MONOCHROMATIC.depth",
            ),
            sf=-1.0,
            idf=50,
            idla=2,
        ),
        inbound_count=InboundCount(
            n_point=1,
        ),
        inbound_points=InboundPointList(
            points=[
                InboundPoint(
                    x_index=1,
                    y_index=2,
                    connect=False,
                )
            ]
        ),
    )

    namelists_component = Namelists(
        pro2=PRO2(dtime=0.0),
        pro3=PRO3(wdthcg=0.0, wdthth=0.0),
        pro4=PRO4(rnfac=0.0, rsfac=0.0),
    )

    field_output_component = Ounf(
        field=Field(
            timestart="19680606 000000",
            timestride="3600",
            timecount="999",
            list="DPT HS FC CFX",
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


def demonstrate_config_approach():
    """Demonstrate using the Config class with components."""
    print("=== Creating Config with Components ===")

    components = create_ww3_tp1_3_components()
    config = NMLConfig(**components)

    return config


def main():
    """Generate WW3 configuration for tp1.3 regression test."""
    print("Creating WW3 configuration for ww3_tp1.3 regression test...")
    print("Test: 1-D monochromatic shoaling on Cartesian grid")

    config = demonstrate_config_approach()
    period = TimeRange(start="1968-06-06T00:00:00", duration="48H", interval="1H")

    model_run = ModelRun(
        run_id="ww3_tp1_3_regression",
        config=config,
        period=period,
        output_dir="rompy_runs",
    )
    model_run.generate()

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nGenerated namelists for tp1.3 test:")
    print("  - ww3_shel.nml: Main shell configuration")
    print("  - ww3_grid.nml: Grid preprocessing with boundary points")
    print("  - namelists.nml: Physics parameters")
    print("  - ww3_ounf.nml: Field output")
    print("\nThis test validates 1-D wave shoaling on Cartesian grid.")


if __name__ == "__main__":
    main()
