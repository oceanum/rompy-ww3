#!/usr/bin/env python3
"""
WW3 tp2.17 regression test: Output Post-Processing Test.

This test validates WW3's output post-processing capabilities with both field (Ounf)
and point (Ounp) output components.

Test Purpose:
- Validate field output post-processing (ww3_ounf)
- Validate point output post-processing (ww3_ounp)
- Test NetCDF output formatting and configuration
- Verify output timing and field selection

Grid Configuration:
- Grid type: RECT (rectangular, spherical coordinates)
- Coordinates: SPHE (spherical)
- Size: Nested domain configuration
- Resolution: Variable resolution for nesting
- Region: Test domain for output validation

Physics:
- Basic propagation with source terms
- Focus on output generation rather than physics complexity
- Boundary nesting configuration

Output Configuration:
- Field outputs: Multiple parameters via Ounf component
- Point outputs: Station time series via Ounp component
- NetCDF format: Version 4 for modern compatibility
- Multiple output types: spectra, parameters, and diagnostics

Run with:
    python rompy_ww3_tp2_17.py
"""

from rompy.model import ModelRun
from rompy.core.time import TimeRange
from rompy_ww3.core.data import WW3DataBlob

from rompy_ww3.config import NMLConfig

from rompy_ww3.components import Shel, Grid, Namelists, Ounf, Ounp
from rompy_ww3.components.namelists import PRO2, PRO3, PRO4

from rompy_ww3.namelists import (
    Domain,
    Spectrum,
    Run,
    Timesteps,
    OutputType,
    HomogCount,
    Input,
    HomogInput,
)
from rompy_ww3.namelists.input import InputForcing
from rompy_ww3.namelists.output_date import OutputDate
from rompy_ww3.namelists.grid import Grid as GRID_NML, Rect
from rompy_ww3.namelists.depth import Depth
from rompy_ww3.namelists.field import Field
from rompy_ww3.namelists.point import Point, PointFile
from rompy_ww3.namelists.spectra import Spectra
from rompy_ww3.namelists.param import Param
from rompy_ww3.namelists.output_file import File as FileNml


def create_ww3_tp2_17_config():
    """Create rompy-ww3 configuration for ww3_tp2.17 regression test.

    This test validates output post-processing capabilities with both
    field output (Ounf) and point output (Ounp) components.
    """

    # Shell component for ww3_shel.nml with output generation
    shell_component = Shel(
        domain=Domain(
            start="20100101 000000",
            stop="20100103 000000",  # 48 hours simulation
            iostyp=1,
        ),
        input_nml=Input(forcing=InputForcing(winds="T")),
        output_type=OutputType(
            field={
                "list": "HS T02 T01 FP DIR SPR DP PHS PTP PDIR WND CUR"
            },  # Comprehensive field output
            point={"file": WW3DataBlob(source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.17/input/points.list")},
        ),
        output_date=OutputDate(
            field={
                "start": "20100101 000000",
                "stride": "3600",  # 1 hour field output
                "stop": "20100103 000000",
            },
            point={
                "start": "20100101 000000",
                "stride": "1800",  # 30 minute point output
                "stop": "20100103 000000",
            },
        ),
        homog_count=HomogCount(
            n_wnd=1,  # One wind field
            n_lev=0,
            n_cur=0,
            n_ice=0,
        ),
        homog_input=[
            HomogInput(
                name="WND",
                date="20100101 000000",
                value1=10.0,
                value2=270.0,
                value3=0.0,
            )
        ],
    )

    # Grid component for ww3_grid.nml with nested domain
    grid_component = Grid(
        spectrum=Spectrum(
            xfr=1.1,
            freq1=0.04,  # 0.04 Hz first frequency
            nk=25,  # 25 frequency bins
            nth=24,  # 24 directional bins
            thoff=0.0,
        ),
        run=Run(
            flcx=True,  # X-direction propagation
            flcy=True,  # Y-direction propagation
            flcth=True,  # Refraction enabled
            flck=False,
            flsou=True,  # Enable source terms
        ),
        timesteps=Timesteps(
            dtmax=900.0,  # 15 minutes max timestep
            dtxy=300.0,  # 5 minutes spatial step
            dtkth=300.0,  # 5 minutes spectral step
            dtmin=10.0,
        ),
        grid=GRID_NML(
            name="OUTPUT POST-PROCESSING TEST NESTED 200x200",
            type="RECT",
            coord="SPHE",
            clos="NONE",
            zlim=-0.10,
            dmin=2.50,
        ),
        rect=Rect(
            nx=200,
            ny=200,
            sx=0.5,  # 0.5 degree spacing
            sy=0.5,
            x0=-10.0,  # Start longitude
            y0=30.0,  # Start latitude
        ),
        depth=Depth(
            sf=-1.0,
            filename=WW3DataBlob(
                source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.17/input/depth.nested.IDLA1.dat"
            ),
            idla=1,
        ),
    )

    # Parameters component for namelists.nml
    parameters_component = Namelists(
        pro2=PRO2(dtime=64800.0),
        pro3=PRO3(wdthcg=1.5, wdthth=1.5),
        pro4=PRO4(rnfac=1.0, rsfac=0.5),
    )

    # Field output component for ww3_ounf.nml
    # This handles post-processing of field outputs
    field_output_component = Ounf(
        field=Field(
            timestart="20100101 000000",
            timestride="3600",  # 1 hour output
            timecount="1000000000",
            list="HS T02 T01 FP DIR SPR DP PHS PTP PDIR WND CUR",  # All wave parameters
            partition="0 1 2 3",  # All partitions
            type=4,  # NetCDF4
            samefile=True,  # All variables in same file
        ),
        file=FileNml(
            prefix="ww3.",
            netcdf=4,  # NetCDF4 format
            ix0=1,
            ixn=1000000000,
            iy0=1,
            iyn=1000000000,
        ),
    )

    # Point output component for ww3_ounp.nml
    # This handles post-processing of point outputs
    point_output_component = Ounp(
        point_nml=Point(
            timestart="20100101 000000",
            timestride="1800",  # 30 minute output
            timecount="1000000000",
            list="all",  # All points from points.list
            samefile=True,  # All points in same file
            buffer=100,  # Points per pass
            type=2,  # Mean parameters (type 2)
            dimorder=True,  # Standard dimension ordering
        ),
        file_nml=PointFile(
            prefix="ww3_points.",
            netcdf=4,  # NetCDF4 format
        ),
        spectra_nml=Spectra(
            output=1,  # Basic spectra output
            scale_fac=1,
            output_fac=0,
        ),
        param_nml=Param(
            output=2,  # Mean parameters (matches type=2 above)
        ),
    )

    # Combine all components into configuration
    config = NMLConfig(
        shell_component=shell_component,
        grid_component=grid_component,
        parameters_component=parameters_component,
        field_output_component=field_output_component,
        point_output_component=point_output_component,
    )

    return config


if __name__ == "__main__":
    print("=" * 70)
    print("WW3 tp2.17: Output Post-Processing Test")
    print("=" * 70)
    print("\nCreating WW3 configuration for output post-processing test...")
    print("Grid: 200×200 nested domain (0.5-degree spacing)")
    print("Physics: Propagation + source terms")
    print("Output: Both field (Ounf) and point (Ounp) post-processing")

    config = create_ww3_tp2_17_config()

    # Create model run
    period = TimeRange(
        start="20100101T000000",
        duration="48H",
        interval="1H",
    )

    model = ModelRun(
        run_id="ww3_tp2_17",
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
    print("  - Nested rectangular grid (200×200) with 0.5-degree spacing")
    print("  - Spherical coordinates for output test domain")
    print("  - Wind forcing with homogeneous 10 m/s from west")
    print("  - 48-hour simulation with multiple output intervals")
    print("\nOutput Post-Processing Components:")
    print("  - Ounf: Field output (ww3_ounf.nml)")
    print("    • 1-hour interval")
    print("    • NetCDF4 format")
    print("    • All wave parameters and partitions")
    print("  - Ounp: Point output (ww3_ounp.nml)")
    print("    • 30-minute interval")
    print("    • NetCDF4 format")
    print("    • Mean parameters (type 2)")
    print("    • All points in single file")
    print("\nInput files required in regtests/ww3_tp2.17/input/:")
    print("  - depth.nested.IDLA1.dat (bathymetry data)")
    print("  - points.list (point output locations)")
    print("\nOutput Processing Notes:")
    print("  - Field outputs: Comprehensive wave parameters")
    print("  - Point outputs: Station time series at specific locations")
    print("  - NetCDF4 format: Modern, compressed, self-describing")
    print("  - Partition output: Separate wind sea and swell components")
    print("  - Verify: Check output file structure and variable names")
