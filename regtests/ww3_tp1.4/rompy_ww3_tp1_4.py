#!/usr/bin/env python3
"""
Example demonstrating how to use rompy-ww3 to generate WW3 namelist files
for the ww3_tp1.4 regression test case using the component-based architecture.

This example shows how to configure a WW3 model run that tests one-dimensional
spectral refraction in the X-direction with no source terms.

Test: tp1.4 - 1-D Spectral Refraction (X-direction)
Reference: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/ww3_tp1.4

Physics: Tests spectral refraction (flcth=T) in X-direction propagation
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
from rompy_ww3.namelists.inbound import InboundCount, InboundPointList, InboundPoint


def create_ww3_tp1_4_components():
    """Create rompy-ww3 components matching the ww3_tp1.4 regression test."""

    # Shell component for ww3_shel.nml (main model configuration)
    shell_component = Shel(
        domain=Domain(
            stop="19680606 120000",
            iostyp=1,  # Output server type (default)
        ),
        input_nml=Input(),
        output_type=OutputType(
            field={"list": "HS T01 DIR"},  # Output HS, mean period, direction
            point={
                "file": WW3DataBlob(source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp1.4/input/points.list")
            },  # Point output file
        ),
        output_date=OutputDate(
            field={
                "start": "19680606 000000",
                "stride": "900",
                "stop": "19680606 120000",
            },  # Field output every 15 minutes (900 seconds)
            point={
                "start": "19680606 000000",
                "stride": "900",
                "stop": "19680606 120000",
            },  # Point output every 15 minutes
        ),
        homog_count=HomogCount(
            n_wnd=0,  # No wind input for tp1.4 (no source terms)
            n_lev=0,
            n_cur=0,
            n_ice=0,
        ),
        homog_input=[],
    )

    # Grid component for ww3_grid.nml (grid preprocessing configuration)
    grid_component = Grid(
        spectrum=Spectrum(
            xfr=1.25,
            freq1=0.08,
            nk=3,
            nth=24,  # 24 directions for refraction test
            thoff=0.0,
        ),
        run=Run(
            fldry=False,
            flcx=True,  # X-component propagation
            flcy=False,  # No Y-component
            flcth=True,  # *** Spectral refraction enabled (theta shift) ***
            flck=False,  # No wavenumber shift
            flsou=False,  # No source terms
        ),
        timesteps=Timesteps(
            dtmax=900.0,  # 15 minutes
            dtxy=300.0,  # 5 minutes propagation
            dtkth=150.0,  # 2.5 minutes refraction (half of dtxy to avoid wiggling)
            dtmin=10.0,
        ),
        grid=GRID_NML(
            name="1-D REFRACTION X",
            type="RECT",
            coord="CART",  # Cartesian coordinates
            clos="NONE",
            zlim=-1.0,
            dmin=1.0,
        ),
        rect=Rect(
            nx=13,  # 13 points in X
            ny=3,  # 3 points in Y (1-D test)
            sx=5000.0,  # 5 km resolution
            sy=5000.0,
            x0=-5000.0,  # Start at -5 km
            y0=-5000.0,
        ),
        depth=Depth(
            filename=WW3DataBlob(
                source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp1.4/input/1-D.depth",
            ),
            sf=-1.0,  # Scale factor
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

    # Parameters component for namelists.nml (model parameters configuration)
    namelists_component = Namelists(
        pro3=PRO3(wdthcg=0.0, wdthth=0.0),  # From namelists_1-D.nml
        pro4=PRO4(rnfac=0.0, rsfac=0.0),  # From namelists_1-D.nml
    )

    # Field output component for ww3_ounf.nml (field output post-processing)
    field_output_component = Ounf(
        field=Field(
            timestart="19680606 000000",
            timestride="900",  # Time stride (15 minutes = 900 seconds)
            timecount="999",  # Number of time steps
            list="HS T01 DIR",  # Output HS, mean period, direction
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
    components = create_ww3_tp1_4_components()

    # Create Config with components
    config = NMLConfig(**components)

    return config


def main():
    """Main function to demonstrate the WW3 configuration approaches."""
    print("Creating WW3 configuration for ww3_tp1.4 regression test...")
    print("Using the component-based architecture")
    print("Test: 1-D spectral refraction (X-direction) with no source terms")

    # Demonstrate Config approach
    config = demonstrate_config_approach()
    period = TimeRange(start="1968-06-06T00:00:00", duration="12h", interval="15m")

    model_run = ModelRun(
        run_id="ww3_tp1_4_regression",
        config=config,
        period=period,
        output_dir="rompy_runs",
    )
    model_run.generate()

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nGenerated namelists for tp1.4 test:")
    print("  - ww3_shel.nml: Main shell configuration")
    print("  - ww3_grid.nml: Grid preprocessing configuration")
    print("  - namelists.nml: Physics parameters configuration")
    print("  - ww3_ounf.nml: Field output post-processing configuration")
    print("\nThis test validates 1-D spectral refraction in X-direction.")


if __name__ == "__main__":
    main()
