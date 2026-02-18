#!/usr/bin/env python3
"""
Example demonstrating how to use rompy-ww3 to generate WW3 namelist files
for the ww3_tp1.1 regression test case using the component-based architecture.

This example shows how to configure a WW3 model run that tests one-dimensional
propagation on a spherical grid along the equator with no source terms.
This is the simplest WW3 test validating pure wave propagation physics.

Test: tp1.1 - 1-D Propagation (Cartesian, No Sources)
Reference: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.1
"""

from rompy.model import ModelRun
from rompy.core.time import TimeRange
from rompy_ww3.core.data import WW3DataBlob

from rompy_ww3.config import NMLConfig

# Import component models
from rompy_ww3.components import (
    Shel,
    Grid,
    Namelists,
    Ounf,
)
from rompy_ww3.components.namelists import PRO3, PRO4

# Import namelist objects
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


def create_ww3_tp1_1_components():
    """Create rompy-ww3 components matching the ww3_tp1.1 regression test."""

    # Shell component for ww3_shel.nml (main model configuration)
    shell_component = Shel(
        domain=Domain(
            start="19680601 000000",
            stop="19680625 000000",
            iostyp=1,  # Output server type (default)
        ),
        input_nml=Input(),
        output_type=OutputType(
            field={"list": "HS"},  # Output significant wave height only
            point={
                "file": WW3DataBlob(source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp1.1/input/points.list")
            },  # Point output file
        ),
        output_date=OutputDate(
            field={
                "start": "19680600 000000",
                "stride": "86400",
                "stop": "19680625 000000",
            },  # Field output every 24 hours (86400 seconds)
            point={
                "start": "19680600 000000",
                "stride": "86400",
                "stop": "19680625 000000",
            },  # Point output every 24 hours
        ),
        homog_count=HomogCount(
            n_wnd=0,  # No wind input for tp1.1 (no source terms)
            n_lev=0,
            n_cur=0,
            n_ice=0,
        ),
        homog_input=[],
    )

    # Grid component for ww3_grid.nml (grid preprocessing configuration)
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
            flcx=True,
            flcy=False,
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
            name="1-D PROPAGATION EQUATOR",
            type="RECT",
            coord="SPHE",
            clos="SMPL",
            zlim=-5.0,
            dmin=5.75,
        ),
        rect=Rect(
            nx=360,
            ny=3,
            sx=1.0,
            sy=1.0,
            x0=-180.0,
            y0=-1.0,
        ),
        depth=Depth(
            filename=WW3DataBlob(
                source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp1.1/input/1-D.depth",
            ),
            sf=-2500.0,
            idf=50,
            idla=2,
        ),
    )

    # Parameters component for namelists.nml (model parameters configuration)
    namelists_component = Namelists(
        pro3=PRO3(wdthcg=0.0, wdthth=0.0),  # From namelists_1-D.nml
        pro4=PRO4(rnfac=0.0, rsfac=0.0),  # From namelists_1-D.nml
    )

    # Field output component for ww3_ounf.nml (field output post-processing)
    field_output_component = Ounf(
        field=Field(
            timestart="19680600 000000",  # Start time from reference
            timestride="86400",  # Time stride (1 day = 86400 seconds) from reference
            timecount="999",  # Number of time steps
            list="HS",  # Output significant wave height
            partition="0 1 2",  # Wave partitions
            type=4,  # Data type: REAL
            samefile=True,  # All variables in same file
        ),
        file=FileNml(  # Using FileNml alias to avoid name conflicts
            prefix="ww3.",
            netcdf=3,  # NetCDF version
            ix0=1,  # First X-axis index
            ixn=1000000000,  # Last X-axis index (default large value)
            iy0=1,  # First Y-axis index
            iyn=1000000000,  # Last Y-axis index (default large value)
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

    # Create components
    components = create_ww3_tp1_1_components()

    # Create Config with components
    config = NMLConfig(**components)

    return config


def main():
    """Main function to demonstrate the WW3 configuration approaches."""
    print("Creating WW3 configuration for ww3_tp1.1 regression test...")
    print("Using the component-based architecture")
    print("Test: 1-D propagation on spherical grid with no source terms")

    # Demonstrate Config approach
    config = demonstrate_config_approach()
    period = TimeRange(start="1968-06-01T00:00:00", duration="24D", interval="1D")

    model_run = ModelRun(
        run_id="ww3_tp1_1_regression",
        config=config,
        period=period,
        output_dir="rompy_runs",
    )
    model_run.generate()

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nGenerated namelists for tp1.1 test:")
    print("  - ww3_shel.nml: Main shell configuration")
    print("  - ww3_grid.nml: Grid preprocessing configuration")
    print("  - namelists.nml: Physics parameters configuration")
    print("  - ww3_ounf.nml: Field output post-processing configuration")
    print("\nThis test validates pure 1-D wave propagation along the equator.")


if __name__ == "__main__":
    main()
