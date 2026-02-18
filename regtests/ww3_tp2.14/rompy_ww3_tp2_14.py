#!/usr/bin/env python3
"""
WW3 tp2.14 regression test: Boundary Conditions Test.

This test validates boundary condition handling in WW3 using the Bound component.

Key configuration:
- Grid type: RECT (rectilinear, 225x106)
- Coordinates: SPHE (spherical)
- Closure: NONE (regional with open boundaries)
- Boundary forcing: Spectral boundary data via Bound component
- Forcing: Boundary conditions only (no internal sources)
- Test Purpose: Validates boundary condition preprocessing and application
"""

from rompy.model import ModelRun
from rompy.core.time import TimeRange
from rompy_ww3.core.data import WW3DataBlob

from rompy_ww3.config import NMLConfig

from rompy_ww3.components import Shel, Grid, Bound

from rompy_ww3.namelists import (
    Domain,
    Spectrum,
    Run,
    Timesteps,
    OutputType,
    HomogCount,
    Input,
    Rect,
    Depth,
)
from rompy_ww3.namelists.output_date import OutputDate
from rompy_ww3.namelists.grid import Grid as GRID_NML
from rompy_ww3.namelists.bound import Bound as BoundNML


def create_ww3_tp2_14_config():
    """Create rompy-ww3 configuration for ww3_tp2.14 regression test."""

    # Shell component - main WW3 configuration
    shell_component = Shel(
        domain=Domain(
            start="20080522 000000",
            stop="20080522 030000",
            iostyp=1,
        ),
        input_nml=Input(),
        output_type=OutputType(
            field={"list": "DPT HS FP DIR SPR"},
            point={"file": WW3DataBlob(source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.14/input/points.list")},
        ),
        output_date=OutputDate(
            field={
                "start": "20080522 000000",
                "stride": "3600",
                "stop": "20080525 000000",
            },
            point={
                "start": "20080522 000000",
                "stride": "360",
                "stop": "20080523 000000",
            },
        ),
        homog_count=HomogCount(
            n_wnd=0,  # No wind input
            n_lev=0,
            n_cur=0,
            n_ice=0,
        ),
    )

    # Grid component - grid preprocessing configuration
    grid_component = Grid(
        spectrum=Spectrum(
            xfr=1.1,
            freq1=0.03679,
            nk=3,
            nth=12,
            thoff=0.0,
        ),
        run=Run(
            fldry=False,
            flcx=True,
            flcy=True,
            flcth=True,
            flck=False,
            flsou=False,  # No source terms - boundary forcing only
        ),
        timesteps=Timesteps(
            dtmax=3300.0,
            dtxy=1100.0,
            dtkth=1650.0,
            dtmin=10.0,
        ),
        grid=GRID_NML(
            name="2-D PROPAGATION TEST 2.14 - BOUNDARY CONDITIONS",
            nml="../input/namelists_2-D.nml",
            type="RECT",
            coord="SPHE",
            clos="NONE",  # Regional domain with open boundaries
            zlim=-0.1,
            dmin=7.50,
        ),
        rect=Rect(
            nx=225,
            ny=106,
            sx=0.35457,
            sy=0.35457,
            x0=183.4,
            y0=25.1,
        ),
        depth=Depth(
            filename=WW3DataBlob(
                source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.14/input/depth.225x106.IDLA1.dat"
            ),
            sf=-1.0,
            idf=50,
            idla=1,
        ),
    )

    # Bound component - boundary condition preprocessing
    bound_component = Bound(
        bound=BoundNML(
            mode="READ",  # Read boundary data from file
            interp=2,  # Linear interpolation
            verbose=1,  # Standard verbosity
            file="regtests/ww3_tp2.14/input/spec.nc",
        )
    )

    return NMLConfig(
        shell_component=shell_component,
        grid_component=grid_component,
        bound_component=bound_component,  # Add boundary component
    )


def main():
    """Main function to demonstrate the WW3 configuration with boundary conditions."""
    print("Creating WW3 configuration for ww3_tp2.14 regression test...")
    print("Boundary conditions test with spectral boundary forcing")

    config = create_ww3_tp2_14_config()
    period = TimeRange(start="2008-05-22T00:00:00", duration="3H", interval="1H")

    model_run = ModelRun(
        run_id="ww3_tp2_14",
        config=config,
        period=period,
        output_dir="rompy",
    )
    model_run.generate()

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nThis configuration includes:")
    print("  - Regional spherical grid (225x106)")
    print("  - Bound component for boundary conditions")
    print("  - Spectral boundary data (spec.nc)")
    print("  - No internal source terms (boundary forcing only)")
    print("  - 3-hour simulation with 1-hour output interval")


if __name__ == "__main__":
    main()
