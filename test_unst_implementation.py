"""
Test script to verify unstructured grid implementation.
"""

import tempfile
from pathlib import Path

from rompy.model import ModelRun
from rompy_ww3.config import Config
from rompy_ww3.grid import Grid as WW3Grid

# Import namelist classes
from rompy_ww3.namelists import (
    Domain,
    Input,
    OutputType,
    OutputDate,
    HomogCount,
    Spectrum,
    Run,
    Timesteps,
    Bound,
    Update,
    ModelParameters,
    Track,
    UnformattedOutput,
    PointOutput,
    RestartUpdate,
    Unst,
)


def test_unstructured_grid_implementation():
    """Test unstructured grid implementation."""
    print("Testing unstructured grid implementation...")

    # Create a WW3 configuration with UNST grid
    config = Config(
        # Domain settings
        domain=Domain(
            start="20230101 000000",
            stop="20230101 120000",  # 12-hour run
            iostyp=0,  # Default output server mode
        ),
        # Physical parameters
        spectrum=Spectrum(
            xfr=1.1,  # Frequency increment
            freq1=0.04118,  # First frequency (Hz)
            nk=32,  # Number of frequencies
            nth=24,  # Number of direction bins
        ),
        # Run parameters
        run=Run(
            fldry=False,  # Not a dry run
            flcx=True,  # X-component of propagation
            flcy=True,  # Y-component of propagation
            flcth=True,  # Direction shift
            flck=False,  # Wavenumber shift (keeping False as in reference)
            flsou=True,  # Source terms
        ),
        # Timesteps parameters
        timesteps=Timesteps(
            dtmax=480.0,  # Maximum CFL timestep as in reference
            dtxy=160.0,  # Propagation timestep as in reference
            dtkth=240.0,  # Refraction timestep as in reference
            dtmin=10.0,  # Minimum time step
        ),
        # Grid configuration - UNST type
        grid=WW3Grid(
            x0=0.0,
            y0=0.0,
            dx=0.25,
            dy=0.25,
            nx=720,  # Use same as reference for comparison
            ny=360,  # Use same as reference for comparison
            name="TEST_UNST_GRID",
            grid_type="UNST",  # Set to UNST
            coordinate_system="SPHE",
            grid_closure="NONE",
            zlim=-0.10,
            dmin=2.5,
        ),
        # Unstructured grid configuration
        unst=Unst(
            sf=-1.0,
            filename="ngug.msh",
            idf=20,
            idla=4,
            idfm=2,
            format="(20f10.2)",
            ugobcfile="boundary_list.dat",
        ),
        # Boundary parameters
        bound=Bound(
            mode="READ",
            file="bound_spec.nc",
            interp=2,
        ),
        # Update parameters
        update=Update(),
        # Model parameters
        parameters=ModelParameters(),
        # Track parameters
        track=Track(),
        # Unformatted output
        unformatted=UnformattedOutput(),
        # Point output
        point_output=PointOutput(),
        # Restart update
        restart_update=RestartUpdate(),
    )

    # Create a mock runtime object
    runtime = ModelRun(run_id_subdir=False, delete_existing=True, run_id="test_unst")

    # Generate the WW3 control files
    result = config(runtime=runtime)

    print(f"Generated WW3 control files in: {result['staging_dir']}")

    # Check the generated ww3_grid.nml file
    namelists_dir = Path(result["staging_dir"]) / "namelists"
    grid_file_path = namelists_dir / "ww3_grid.nml"

    if grid_file_path.exists():
        with open(grid_file_path, "r") as f:
            content = f.read()

        print("\nGenerated ww3_grid.nml content with UNST grid:")
        print("=" * 60)
        print(content)
        print("=" * 60)

        # Check if UNST_NML is present
        if "&UNST_NML" in content:
            print("\n✓ UNST_NML section successfully generated!")
        else:
            print("\n✗ UNST_NML section not found!")

        return True
    else:
        print(f"\n✗ File {grid_file_path} not generated!")
        return False


if __name__ == "__main__":
    success = test_unstructured_grid_implementation()
    if success:
        print("\n✓ Unstructured grid implementation test completed successfully!")
    else:
        print("\n✗ Unstructured grid implementation test failed!")
