"""
Test script to verify SMC and unstructured grid implementations.
"""

from pathlib import Path

from rompy.model import ModelRun
from rompy_ww3.config import Config
from rompy_ww3.grid import Grid as WW3Grid

# Import namelist classes
from rompy_ww3.namelists import (
    Domain,
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
    Smc,
    SMCFile,
)


def test_smc_grid_implementation():
    """Test SMC grid implementation."""
    print("Testing SMC grid implementation...")

    # Create a WW3 configuration with SMC grid
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
        # Grid configuration - SMC type
        grid=WW3Grid(
            x0=0.0,
            y0=0.0,
            dx=0.25,
            dy=0.25,
            nx=720,  # Use same as reference for comparison
            ny=360,  # Use same as reference for comparison
            name="TEST_SMC_GRID",
            grid_type="SMC",  # Set to SMC
            coordinate_system="SPHE",
            grid_closure="NONE",
            zlim=-0.10,
            dmin=2.5,
        ),
        # SMC grid configuration
        smc=Smc(
            mcel=SMCFile(
                filename="S6125MCels.dat",
                idf=31,
                idla=1,
                idfm=1,
                format="(....)",
            ),
            iside=SMCFile(
                filename="S6125ISide.dat",
                idf=32,
                idla=1,
                idfm=1,
                format="(....)",
            ),
            jside=SMCFile(
                filename="S6125JSide.dat",
                idf=33,
                idla=1,
                idfm=1,
                format="(....)",
            ),
            subtr=SMCFile(
                filename="SMC25Subtr.dat",
                idf=34,
                idla=1,
                idfm=1,
                format="(....)",
            ),
            bundy=SMCFile(
                filename="S6125Bundy.dat",
                idf=35,
                idla=1,
                idfm=1,
                format="(....)",
            ),
            mbarc=SMCFile(
                filename="S6125MBArc.dat",
                idf=36,
                idla=1,
                idfm=1,
                format="(....)",
            ),
            aisid=SMCFile(
                filename="S6125AISid.dat",
                idf=37,
                idla=1,
                idfm=1,
                format="(....)",
            ),
            ajsid=SMCFile(
                filename="S6125AJSid.dat",
                idf=38,
                idla=1,
                idfm=1,
                format="(....)",
            ),
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
    runtime = ModelRun(run_id_subdir=False, delete_existing=True, run_id="test_smc")

    # Generate the WW3 control files
    result = config(runtime=runtime)

    print(f"Generated WW3 control files in: {result['staging_dir']}")

    # Check the generated ww3_grid.nml file
    namelists_dir = Path(result["staging_dir"]) / "namelists"
    grid_file_path = namelists_dir / "ww3_grid.nml"

    if grid_file_path.exists():
        with open(grid_file_path, "r") as f:
            content = f.read()

        print("\nGenerated ww3_grid.nml content with SMC grid:")
        print("=" * 60)
        print(content)
        print("=" * 60)

        # Check if SMC_NML is present
        if "&SMC_NML" in content:
            print("\n✓ SMC_NML section successfully generated!")
        else:
            print("\n✗ SMC_NML section not found!")

        return True
    else:
        print(f"\n✗ File {grid_file_path} not generated!")
        return False


if __name__ == "__main__":
    success = test_smc_grid_implementation()
    if success:
        print("\n✓ SMC grid implementation test completed successfully!")
    else:
        print("\n✗ SMC grid implementation test failed!")
