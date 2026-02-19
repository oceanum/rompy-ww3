#!/usr/bin/env python3
"""
Example demonstrating how to use rompy-ww3 to generate WW3 namelist files
for the ww3_tp2.4 regression test case using the new component-based architecture.

This example shows how to configure a WW3 model run that tests two-dimensional
propagation on a spherical lat/lon grid in the Eastern Pacific region.
Config class uses direct component configuration, while the component-level
approach uses high-level grid/data objects to automatically generate the
appropriate component configurations.
"""

from rompy.model import ModelRun
from rompy.core.time import TimeRange
from rompy_ww3.core.data import WW3DataBlob

from rompy_ww3.config import ShelConfig

# Import component models
from rompy_ww3.components import (
    Shel,
    Grid,
    Namelists,
    Ounf,
)
from rompy_ww3.components.namelists import PRO2, PRO3, PRO4

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


def create_ww3_tp2_4_components():
    """Create rompy-ww3 components matching the ww3_tp2.4 regression test."""

    # Shell component for ww3_shel.nml (main model configuration)
    shell_component = Shel(
        domain=Domain(
            start="20080522 000000",
            stop="20080522 030000",
            iostyp=1,  # Output server type from reference
        ),
        input_nml=Input(),
        output_type=OutputType(
            field={"list": "DPT HS FP DIR SPR"},  # Output fields from reference
            point={
                "file": WW3DataBlob(
                    source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.4/input/points.list"
                )
            },  # Point output file
        ),
        output_date=OutputDate(
            field={
                "start": "20080522 000000",
                "stride": "3600",
                "stop": "20080525 000000",
            },  # Field output every hour
            point={
                "start": "20080522 000000",
                "stride": "360",
                "stop": "20080523 000000",
            },  # Point output every 6 min
        ),
        homog_count=HomogCount(
            n_wnd=0,  # No wind input for the tp2.4 test (no source terms)
            n_lev=0,
            n_cur=0,
            n_ice=0,
        ),
        homog_input=[],
    )

    # Grid component for ww3_grid.nml (grid preprocessing configuration)
    grid_component = Grid(
        spectrum=Spectrum(
            xfr=1.1,  # Frequency increment from reference
            freq1=0.03679,  # First frequency (Hz) from reference for tp2.4
            nk=3,  # Number of frequencies from reference for tp2.4
            nth=12,  # Number of direction bins from reference for tp2.4
            thoff=0.0,  # Relative offset of first direction
        ),
        run=Run(
            fldry=False,  # Not a dry run
            flcx=True,  # X-component of propagation from reference
            flcy=True,  # Y-component of propagation from reference
            flcth=True,  # Direction shift from reference
            flck=False,  # Wavenumber shift from reference
            flsou=False,  # No source terms for this test case (LN0 ST0 NL0 BT0 DB0 TR0 BS0 XX0)
        ),
        timesteps=Timesteps(
            dtmax=3300.0,  # Maximum CFL timestep (should be ~3 times dtxy)
            dtxy=1100.0,  # Propagation timestep from reference
            dtkth=1650.0,  # Refraction timestep (should be between dtmax/10 and dtmax/2)
            dtmin=10.0,  # Minimum time step for source terms
        ),
        grid_nml=GRID_NML(
            name="2-D PROPAGATION TEST 2.4",  # Grid name from reference
            type="RECT",  # Rectilinear grid from reference
            coord="SPHE",  # Spherical coordinates from reference
            clos="NONE",  # No closure from reference
            zlim=-0.1,  # Minimum depth from reference
            dmin=7.50,  # Minimum water depth from reference
        ),
        rect_nml=Rect(
            nx=225,  # Number of points along x-axis from reference
            ny=106,  # Number of points along y-axis from reference
            sx=0.35457,  # Grid increment along x-axis from reference
            sy=0.35457,  # Grid increment along y-axis from reference
            x0=183.4,  # Western boundary from reference
            y0=25.1,  # Southern boundary from reference
        ),
        depth=Depth(
            # filename="./../input/depth.225x106.IDLA1.dat",
            filename=WW3DataBlob(
                source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.4/input/depth.225x106.IDLA1.dat",
            ),
            sf=-1.0,  # Scale factor from reference
            idf=50,  # IDF
            idla=1,  # IDLA
        ),
    )

    # Parameters component for namelists.nml (model parameters configuration)
    namelists_component = Namelists(
        pro2=PRO2(dtime=64800.0),  # From namelists_2-D.nml
        pro3=PRO3(wdthcg=1.5, wdthth=1.5),  # From namelists_2-D.nml
        pro4=PRO4(rnfac=0.0, rsfac=0.0),  # From namelists_2-D.nml
    )

    # Field output component for ww3_ounf.nml (field output post-processing)
    # This configuration handles the output of field data after model execution
    field_output_component = Ounf(
        field=Field(
            timestart="20080522 000000",  # Start time from reference
            timestride=3600,  # Time stride from reference (1 hour)
            timecount="999",  # Number of time steps from reference
            list="DPT HS",  # Output fields from reference: water depth and wave height
            partition="0 1 2",  # Wave partitions from reference
            type=4,  # Data type: REAL from reference
            samefile=True,  # All variables in same file from reference
        ),
        file=FileNml(  # Using FileNml alias to avoid name conflicts
            prefix="ww3.",
            netcdf=3,  # NetCDF version from reference
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
        "field_output_component": field_output_component,  # Field output component for postprocessing
    }


def demonstrate_config_approach():
    """Demonstrate using the Config class with components."""
    print("=== Demonstrating Config Class with Components ===")

    # Create components
    components = create_ww3_tp2_4_components()

    # Create Config with components
    config = ShelConfig(**components)

    return config


def demonstrate_ww3config_approach():
    """Demonstrate using components with enhanced namelist objects."""
    print("\n=== Demonstrating Component-Level Approach with Enhanced Namelists ===")

    # Import the enhanced namelist classes that support data fetching
    from rompy_ww3.namelists.grid import Grid as GRID_NML, Rect
    from rompy_ww3.namelists.depth import Depth
    from rompy_ww3.namelists.spectrum import Spectrum
    from rompy_ww3.namelists.run import Run
    from rompy_ww3.namelists.timesteps import Timesteps

    # Create enhanced namelist objects that can accept either filenames or rompy.data objects
    grid_nml = GRID_NML(
        name="2-D PROPAGATION TEST 2.4",  # Grid name from reference
        type="RECT",  # Rectilinear grid from reference
        coord="SPHE",  # Spherical coordinates from reference
        clos="NONE",  # No closure from reference
        zlim=-0.1,  # Minimum depth from reference
        dmin=7.50,  # Minimum water depth from reference
    )

    rect_nml = Rect(
        nx=225,  # Number of points along x-axis from reference
        ny=106,  # Number of points along y-axis from reference
        sx=0.35457,  # Grid increment along x-axis from reference
        sy=0.35457,  # Grid increment along y-axis from reference
        x0=183.4,  # Western boundary from reference
        y0=25.1,  # Southern boundary from reference
    )

    depth_nml = Depth(
        filename="./../input/depth.225x106.IDLA1.dat",
        sf=-1.0,  # Scale factor from reference
        idf=50,  # IDF
        idla=1,  # IDLA
    )

    spectrum_nml = Spectrum(
        xfr=1.1,  # Frequency increment from reference
        freq1=0.03679,  # First frequency (Hz) from reference for tp2.4
        nk=3,  # Number of frequencies from reference for tp2.4
        nth=12,  # Number of direction bins from reference for tp2.4
        thoff=0.0,  # Relative offset of first direction
    )

    run_nml = Run(
        fldry=False,  # Not a dry run
        flcx=True,  # X-component of propagation from reference
        flcy=True,  # Y-component of propagation from reference
        flcth=True,  # Direction shift from reference
        flck=False,  # Wavenumber shift from reference
        flsou=False,  # No source terms for this test case (LN0 ST0 NL0 BT0 DB0 TR0 BS0 XX0)
    )

    timesteps_nml = Timesteps(
        dtmax=3300.0,  # Maximum CFL timestep (should be ~3 times dtxy)
        dtxy=1100.0,  # Propagation timestep from reference
        dtkth=1650.0,  # Refraction timestep (should be between dtmax/10 and dtmax/2)
        dtmin=10.0,  # Minimum time step for source terms
    )

    # Create components with the enhanced namelist objects
    grid_component = Grid(
        grid_nml=grid_nml,
        rect_nml=rect_nml,
        depth=depth_nml,
        spectrum=spectrum_nml,
        run=run_nml,
        timesteps=timesteps_nml,
    )

    # Create Config with the enhanced components
    config = ShelConfig(
        grid_component=grid_component,
    )

    # Show what namelists are generated from the enhanced components
    namelists = config.render_namelists()
    print(f"Generated {len(namelists)} namelist files from enhanced components:")
    for filename in sorted(namelists.keys()):
        print(f"  - {filename}")

    print(
        "Note: Components now work with enhanced namelist objects that can accept rompy.data objects."
    )
    print(
        "This enables seamless integration of high-level workflows with component-based architecture."
    )

    return config


def main():
    """Main function to demonstrate the WW3 configuration approaches."""
    print("Creating WW3 configuration for ww3_tp2.4 regression test...")
    print("Using the new component-based architecture")

    # Demonstrate Config approach
    config = demonstrate_config_approach()
    period = TimeRange(start="2008-05-22T00:00:00", duration="3H", interval="1H")

    model_run = ModelRun(
        run_id="direct_components",
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
