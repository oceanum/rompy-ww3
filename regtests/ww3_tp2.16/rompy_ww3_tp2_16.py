#!/usr/bin/env python3
"""
WW3 tp2.16 regression test: Data Assimilation Test.

This test validates WW3's data assimilation capabilities with mean wave parameters.

Test Purpose:
- Validate data assimilation functionality
- Test mean wave parameter assimilation
- Verify observation ingestion and state updates

Grid Configuration:
- Grid type: RECT (rectangular, spherical coordinates)
- Coordinates: SPHE (spherical)
- Size: 200 × 200 grid points
- Resolution: Regular lat-lon spacing
- Region: Test domain for assimilation validation

Physics:
- Minimal source terms for testing assimilation updates
- Focus on data assimilation rather than full physics
- Mean wave parameter updates from observations

Assimilation Configuration:
- Mean wave parameters: Enabled
- 1D spectrum assimilation: Optional
- 2D spectrum assimilation: Optional
- Observation data format: External files

Run with:
    python rompy_ww3_tp2_16.py
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
from rompy_ww3.namelists.input import InputAssim
from rompy_ww3.namelists.output_date import OutputDate
from rompy_ww3.namelists.grid import Grid as GRID_NML, Rect
from rompy_ww3.namelists.depth import Depth
from rompy_ww3.namelists.field import Field
from rompy_ww3.namelists.output_file import File as FileNml


def create_ww3_tp2_16_config():
    """Create rompy-ww3 configuration for ww3_tp2.16 regression test.

    This test validates data assimilation capabilities with mean wave
    parameter updates from external observation data.
    """

    # Shell component for ww3_shel.nml with assimilation enabled
    shell_component = Shel(
        domain=Domain(
            start="20100101 000000",
            stop="20100102 000000",  # 24 hours simulation
            iostyp=1,
        ),
        input_nml=Input(
            forcing={
                "winds": "F",  # No wind forcing (focus on assimilation)
            },
            assim=InputAssim(
                mean="T",  # Enable mean wave assimilation
                spec1d="F",  # No 1D spectrum assimilation
                spec2d="F",  # No 2D spectrum assimilation
            ),
        ),
        output_type=OutputType(
            field={
                "list": "HS T02 DP DIR FP WND"
            },  # Basic wave parameters + assimilation diagnostics
            point={"file": "../input/points.list"},
        ),
        output_date=OutputDate(
            field={
                "start": "20100101 000000",
                "stride": "3600",  # 1 hour output
                "stop": "20100102 000000",
            },
            point={
                "start": "20100101 000000",
                "stride": "3600",  # 1 hour point output
                "stop": "20100102 000000",
            },
        ),
        homog_count=HomogCount(
            n_wnd=0,  # No homogeneous forcing
            n_lev=0,
            n_cur=0,
            n_ice=0,
        ),
        homog_input=[],
    )

    # Grid component for ww3_grid.nml with rectangular grid
    grid_component = Grid(
        spectrum=Spectrum(
            xfr=1.1,
            freq1=0.04,  # 0.04 Hz first frequency
            nk=25,  # 25 frequency bins (typical for assimilation tests)
            nth=24,  # 24 directional bins
            thoff=0.0,  # No direction offset
        ),
        run=Run(
            flcx=True,  # X-direction propagation
            flcy=True,  # Y-direction propagation
            flcth=False,  # No spectral refraction (simple test)
            flck=False,  # No wavenumber shift
            flsou=False,  # No source terms (pure assimilation test)
        ),
        timesteps=Timesteps(
            dtmax=900.0,  # 15 minutes max timestep
            dtxy=300.0,  # 5 minutes spatial step
            dtkth=300.0,  # 5 minutes spectral step
            dtmin=10.0,  # 10 seconds minimum
        ),
        grid=GRID_NML(
            name="ASSIMILATION TEST DOMAIN 200x200",
            nml=None,  # No external namelists
            type="RECT",  # Rectangular grid
            coord="SPHE",  # Spherical coordinates
            clos="NONE",  # Regional domain (no closure)
            zlim=-0.10,  # Depth limit
            dmin=2.50,  # Minimum depth
        ),
        rect=Rect(
            nx=200,  # 200 points in x-direction
            ny=200,  # 200 points in y-direction
            sx=1.0,  # 1 degree spacing in x
            sy=1.0,  # 1 degree spacing in y
            sf=1.0,  # Scale factor
            x0=0.0,  # Start longitude
            y0=-45.0,  # Start latitude
        ),
        depth=Depth(
            sf=1.0,  # Scale factor (meters)
            filename=WW3DataBlob(
                source="regtests/ww3_tp2.16/input/depth.200x200.IDLA1.dat"
            ),
            idla=1,  # IDLA format 1
        ),
    )

    # Parameters component for namelists.nml
    parameters_component = Namelists(
        pro2=PRO2(dtime=0.0),
        pro3=PRO3(wdthcg=0.0, wdthth=0.0),
        pro4=PRO4(rnfac=0.0, rsfac=0.0),
    )

    # Field output component for ww3_ounf.nml
    field_output_component = Ounf(
        field=Field(
            timestart="20100101 000000",
            timestride="3600",  # 1 hour output
            timecount="1000000000",
            list="HS T02 DP DIR FP WND",
            partition="0 1 2",
            type="4",  # NetCDF4
            samefile=True,
        ),
        file=FileNml(
            prefix="ww3.",
            netcdf=3,
        ),
    )

    # Combine all components into configuration
    config = NMLConfig(
        shell_component=shell_component,
        grid_component=grid_component,
        parameters_component=parameters_component,
        field_output_component=field_output_component,
    )

    return config


if __name__ == "__main__":
    print("=" * 70)
    print("WW3 tp2.16: Data Assimilation Test")
    print("=" * 70)
    print("\nCreating WW3 configuration for data assimilation test...")
    print("Grid: 200×200 rectangular (1-degree spacing)")
    print("Physics: No source terms (focus on assimilation)")
    print("Assimilation: Mean wave parameters from observations")

    config = create_ww3_tp2_16_config()

    # Create model run
    period = TimeRange(
        start="20100101T000000",
        duration="24H",
        interval="1H",
    )

    model = ModelRun(
        run_id="ww3_tp2_16",
        output_dir="rompy_runs",
        period=period,
        config=config,
    )

    # Generate configuration files
    print("\nGenerating namelist files...")
    model.generate()

    print("\n" + "=" * 70)
    print("✓ CONFIGURATION COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\nThis configuration includes:")
    print("  - Rectangular grid (200×200) with 1-degree spacing")
    print("  - Spherical coordinates for assimilation test domain")
    print("  - Data assimilation for mean wave parameters")
    print("  - 24-hour simulation with 1-hour output intervals")
    print("\nAssimilation Parameters:")
    print("  - MEAN: T (mean wave parameter assimilation enabled)")
    print("  - SPEC1D: F (no 1D spectrum assimilation)")
    print("  - SPEC2D: F (no 2D spectrum assimilation)")
    print("\nInput files required in regtests/ww3_tp2.16/input/:")
    print("  - depth.200x200.IDLA1.dat (bathymetry data)")
    print("  - points.list (point output locations)")
    print("  - assimilation data files (mean wave observations)")
    print("\nData Assimilation Notes:")
    print("  - Observation files should contain mean wave parameters")
    print("  - Assimilation updates applied at model timesteps")
    print("  - Output includes both model and assimilated states")
    print("  - Verify observation ingestion and state corrections")
