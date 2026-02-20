#!/usr/bin/env python3
"""
Example demonstrating how to use rompy-ww3 to generate WW3 namelist files
for the ww3_tp1.2 regression test case using the component-based architecture.

This example shows how to configure a WW3 model run that tests one-dimensional
propagation on a spherical grid along a meridian with no source terms.
This test validates pure wave propagation physics in the Y (meridional) direction.

Test: tp1.2 - 1-D Propagation Along Meridian (Spherical, No Sources)
Reference: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.2

Key Difference from tp1.1: Propagation is along meridian (flcy=T) not equator (flcx=T).
Grid is 3x123 (narrow in longitude, extended in latitude) vs 360x3 for tp1.1.
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


def create_ww3_tp1_2_components():
    """Create rompy-ww3 components matching the ww3_tp1.2 regression test."""

    shell_component = Shel(
        domain=Domain(
            start="19680601 000000",
            stop="19680607 000000",
            iostyp=1,
        ),
        input_nml=Input(),
        output_type=OutputType(
            field={"list": "HS"},
        ),
        output_date=OutputDate(
            field={
                "start": "19680601 000000",
                "stride": "43200",
                "stop": "19680607 000000",
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
            freq1=0.03679,
            nk=3,
            nth=4,
            thoff=0.0,
        ),
        run=Run(
            fldry=False,
            flcx=False,
            flcy=True,
            flcth=False,
            flck=False,
            flsou=False,
        ),
        timesteps=Timesteps(
            dtmax=10800.0,
            dtxy=3600.0,
            dtkth=5400.0,
            dtmin=10.0,
        ),
        grid=GRID_NML(
            name="1-D PROPAGATION MERIDIAN",
            type="RECT",
            coord="SPHE",
            clos="NONE",
            zlim=-5.0,
            dmin=5.75,
        ),
        rect=Rect(
            nx=3,
            ny=123,
            sx=1.0,
            sy=1.0,
            x0=-1.0,
            y0=-61.0,
        ),
        depth=Depth(
            filename=WW3DataBlob(
                source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp1.2/input/1-D.depth",
            ),
            sf=-2500.0,
            idf=50,
            idla=2,
        ),
    )

    namelists_component = Namelists(
        pro3=PRO3(wdthcg=0.0, wdthth=0.0),
        pro4=PRO4(rnfac=0.0, rsfac=0.0),
    )

    field_output_component = Ounf(
        field=Field(
            timestart="19680601 000000",
            timestride=43200,
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

    return {
        "shell_component": shell_component,
        "grid_component": grid_component,
        "parameters_component": namelists_component,
        "field_output_component": field_output_component,
    }


def demonstrate_config_approach():
    """Demonstrate using the Config class with components."""
    print("=== Demonstrating Config Class with Components ===")

    components = create_ww3_tp1_2_components()

    config = NMLConfig(**components)

    return config


def main():
    """Main function to demonstrate the WW3 configuration approaches."""
    print("Creating WW3 configuration for ww3_tp1.2 regression test...")
    print("Using the component-based architecture")
    print("Test: 1-D propagation on spherical grid along meridian with no source terms")

    config = demonstrate_config_approach()
    period = TimeRange(start="1968-06-01T00:00:00", duration="6D", interval="12H")

    model_run = ModelRun(
        run_id="ww3_tp1_2_regression",
        config=config,
        period=period,
        output_dir="rompy_runs",
    )
    model_run.generate()

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nGenerated namelists for tp1.2 test:")
    print("  - ww3_shel.nml: Main shell configuration")
    print("  - ww3_grid.nml: Grid preprocessing configuration")
    print("  - namelists.nml: Physics parameters configuration")
    print("  - ww3_ounf.nml: Field output post-processing configuration")
    print("\nThis test validates pure 1-D wave propagation along a meridian.")
    print(
        "Key difference from tp1.1: propagation in Y direction (flcy=T) not X (flcx=T)."
    )


if __name__ == "__main__":
    main()
