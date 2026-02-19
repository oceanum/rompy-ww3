#!/usr/bin/env python3
"""
WW3 tp1.8 regression test: Wave breaking on a beach.

Test: tp1.8 - Wave Breaking on Beach
Reference: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.8

Physics: Tests wave breaking physics on a beach (DB1 source term)
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


def create_ww3_tp1_8_components():
    """
    tp1.8: Wave breaking on a beach with DB1 source terms.

    Key features:
    - Cartesian grid: 52x3, 20m resolution
    - Spectrum: 30 frequencies (0.04 Hz), 90 directions
    - Source terms enabled (breaking: DB1)
    - Very fine timesteps: dtxy=0.25s for breaking stability
    - 1-D propagation with full spectral processes
    """
    shell_component = Shel(
        domain=Domain(
            start="20110101 000000",
            stop="20110101 000100",
            iostyp=1,
        ),
        input_nml=Input(),
        output_type=OutputType(
            field={"list": "DPT WND WLV HS T02 DIR SPR TAW TWO BHD SXY FOC USS USF"},
            point={
                "file": WW3DataBlob(
                    source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp1.8/input/points.list"
                )
            },
        ),
        output_date=OutputDate(
            field={
                "start": "20110101 000000",
                "stride": "10",
                "stop": "20110102 000000",
            },
            point={
                "start": "20110101 000000",
                "stride": "10",
                "stop": "20110102 000000",
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

    # Adjust timesteps for rompy-ww3 validation
    # Official: all 0.5s, but dtmin must be 5-60s
    # Use dtmax ≈ 3×dtxy constraint
    grid_component = Grid(
        spectrum=Spectrum(
            xfr=1.091,
            freq1=0.04,
            nk=30,
            nth=90,
            thoff=0.0,
        ),
        run=Run(
            fldry=False,
            flcx=True,
            flcy=False,
            flcth=True,
            flck=True,
            flsou=True,  # Source terms enabled (breaking)
        ),
        timesteps=Timesteps(
            dtmax=0.75,  # 3× dtxy (validation constraint)
            dtxy=0.25,  # Fine spatial timestep for breaking
            dtkth=0.25,  # Between dtmax/10 and dtmax/2
            dtmin=5.0,  # Minimum allowed by validation
        ),
        grid=GRID_NML(
            name="VALIDATION - Haas Warner 2009",
            nml="../input/namelists_VALIDATION.nml",
            type="RECT",
            coord="CART",
            clos="NONE",
            zlim=-98.0,
            dmin=0.1,
        ),
        rect=Rect(
            nx=52,
            ny=3,
            sx=20.0,
            sy=20.0,
            x0=-10.0,
            y0=-10.0,
        ),
        depth=Depth(
            filename=WW3DataBlob(
                source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp1.8/input/BathyWW3.dat",
            ),
            sf=-1.0,
            idf=50,
            idla=1,
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
            timestart="20110101 000000",
            timestride=10,
            timecount="999",
            list="DPT WND WLV HS T02 DIR SPR TAW TWO BHD SXY FOC USS USF",
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
    print("Creating WW3 configuration for ww3_tp1.8 regression test...")
    print("Test: Wave breaking on a beach (DB1 source terms)")

    config = NMLConfig(**create_ww3_tp1_8_components())
    period = TimeRange(start="2011-01-01T00:00:00", duration="100s", interval="10s")

    model_run = ModelRun(
        run_id="ww3_tp1_8_regression",
        config=config,
        period=period,
        output_dir="rompy_runs",
    )
    model_run.generate()

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nThis test validates wave breaking physics on a beach.")
    print("Key features:")
    print("  - Breaking dissipation (DB1 source term)")
    print("  - Cartesian grid: 52x3, 20m resolution")
    print("  - Fine timesteps (0.25s spatial) for breaking stability")
    print("  - Full spectral processes (refraction, wavenumber shift)")


if __name__ == "__main__":
    main()
