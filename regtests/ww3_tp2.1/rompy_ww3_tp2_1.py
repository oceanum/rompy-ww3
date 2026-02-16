#!/usr/bin/env python3
"""
WW3 tp2.1 regression test configuration using rompy-ww3.

Test: 2-D propagation on Cartesian grid with no source terms.
Physics: !/LN0 !/ST0 !/NL0 !/BT0 !/DB0 !/TR0 !/BS0 (no source terms)
Reference: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp2.1
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
from rompy_ww3.namelists.field import Field
from rompy_ww3.namelists.output_file import File as FileNml


def create_ww3_tp2_1_components():
    """Create rompy-ww3 components for tp2.1 2-D Cartesian propagation test."""

    shell_component = Shel(
        domain=Domain(
            start="19680606 000000",
            stop="19680606 050000",
            iostyp=0,
        ),
        input_nml=Input(),
        output_type=OutputType(
            field={"list": "HS DIR SPR DP EF TH1M STH1M TH2M STH2M"},
        ),
        output_date=OutputDate(
            field={
                "start": "19680606 000000",
                "stride": "86400",
                "stop": "19680606 050000",
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
            freq1=0.04665,
            nk=3,
            nth=24,
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
            dtmax=900.0,
            dtxy=300.0,
            dtkth=450.0,
            dtmin=10.0,
        ),
        grid=GRID_NML(
            name="2-D PROPAGATION TEST #1",
            type="RECT",
            coord="CART",
            clos="NONE",
            zlim=-5.0,
            dmin=5.75,
        ),
        rect=Rect(
            nx=43,
            ny=43,
            sx=10000.0,  # 10 km spacing
            sy=10000.0,
            x0=-60000.0,  # -60 km origin
            y0=-60000.0,
        ),
        depth=Depth(
            filename=WW3DataBlob(
                source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.1/input/2-D.depth",
            ),
            sf=-2500.0,
            idf=50,
            idla=2,
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
            timestride="86400",
            timecount="999",
            list="HS DIR SPR DP EF TH1M STH1M TH2M STH2M",
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
    """Generate WW3 configuration for tp2.1 regression test."""
    print("Creating WW3 configuration for ww3_tp2.1 regression test...")
    print("Test: 2-D propagation on Cartesian grid, no source terms")

    components = create_ww3_tp2_1_components()
    config = NMLConfig(**components)
    period = TimeRange(start="1968-06-06T00:00:00", duration="5H", interval="1H")

    model_run = ModelRun(
        run_id="ww3_tp2_1_regression",
        config=config,
        period=period,
        output_dir="rompy_runs",
    )
    model_run.generate()

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nGenerated namelists for tp2.1 test:")
    print("  - ww3_shel.nml: Main shell configuration")
    print("  - ww3_grid.nml: Grid preprocessing (43x43 CART)")
    print("  - namelists.nml: Physics parameters")
    print("  - ww3_ounf.nml: Field output")
    print("\nThis test validates 2-D wave propagation on Cartesian grid.")


if __name__ == "__main__":
    main()
