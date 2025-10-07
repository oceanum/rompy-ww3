"""
Test WW3 control file generation from the rompy_ww3 configuration.

This test validates that the Config class generates the correct WW3 control files
with appropriate namelist sections.
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
)


def test_ww3_control_file_generation():
    """Test the generation of WW3 control files."""

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create a basic WW3 configuration
        config = Config(
            # Domain settings
            domain=Domain(
                start="20230101 000000",
                stop="20230101 120000",  # 12-hour run
                iostyp=0,  # Default output server mode
            ),
            # Input configuration
            input_nml=Input(),
            # Output configuration
            output_type=OutputType(
                field={
                    "list": "HSIGN TMM10 TM02 PDIR PENT WNDIR WNDSP",  # Common output fields
                },
            ),
            output_date=OutputDate(
                field={
                    "start": "20230101 000000",
                    "stride": "3600",  # Hourly output
                    "stop": "20230101 120000",
                },
            ),
            # Homogeneous inputs
            homog_count=HomogCount(
                n_wnd=0,
                n_lev=0,
                n_cur=0,
                n_ice=0,
            ),
            # Physical parameters
            spectrum=Spectrum(
                xfr=1.1,  # Frequency increment
                freq1=0.035714,  # First frequency (Hz)
                nk=25,  # Number of frequencies
                nth=24,  # Number of direction bins
            ),
            # Run parameters
            run=Run(
                fldry=False,  # Not a dry run
                flcx=True,  # X-component of propagation
                flcy=True,  # Y-component of propagation
                flcth=True,  # Direction shift
                flck=True,  # Wavenumber shift
                flsou=True,  # Source terms
            ),
            # Timesteps parameters
            timesteps=Timesteps(
                dtmax=2700.0,  # Maximum CFL timestep (3 * dtxy)
                dtxy=900.0,  # Propagation timestep
                dtkth=1350.0,  # Refraction timestep (between dtmax/10 and dtmax/2)
                dtmin=10.0,  # Minimum time step
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
            # Grid configuration
            grid=WW3Grid(
                x0=-75.0,
                y0=35.0,
                dx=0.20408163265306123,
                dy=0.20408163265306123,
                nx=50,
                ny=50,
                name="north_atlantic_example",
                grid_type="RECT",
                coordinate_system="SPHE",
                zlim=-0.20,
                dmin=2.5,
            ),
        )

        # Create a mock runtime object
        runtime = ModelRun(
            run_id_subdir=False, delete_existing=True, run_id="test_ww3_control_files"
        )

        # Generate the WW3 control files
        result = config(runtime=runtime)

        print(f"Generated WW3 control files in: {result['staging_dir']}")

        # Check that the expected files were created
        namelists_dir = Path(result["staging_dir"]) / "namelists"

        expected_files = [
            "ww3_shel.nml",
            "ww3_multi.nml",
            "ww3_grid.nml",
            "ww3_bound.nml",
            "ww3_bounc.nml",
            "ww3_prnc.nml",
            "ww3_trnc.nml",
            "ww3_ounf.nml",
            "ww3_ounp.nml",
            "ww3_uprstr.nml",
            "namelists.nml",
        ]

        print("\nChecking for expected WW3 control files:")
        all_files_exist = True
        for file in expected_files:
            file_path = namelists_dir / file
            exists = file_path.exists()
            print(f"  {file}: {'✓' if exists else '✗'}")
            if not exists:
                all_files_exist = False

        if all_files_exist:
            print("\n✓ All expected WW3 control files were generated successfully!")
        else:
            print("\n✗ Some expected WW3 control files were not generated.")
            return False

        # Print contents of some key files for verification
        print("\nContents of generated ww3_shel.nml:")
        print("=" * 50)
        with open(namelists_dir / "ww3_shel.nml", "r") as f:
            content = f.read()
            print(content)
        print("=" * 50)

        print("\nContents of generated ww3_grid.nml:")
        print("=" * 50)
        with open(namelists_dir / "ww3_grid.nml", "r") as f:
            content = f.read()
            print(content)
        print("=" * 50)

        print("\nContents of generated ww3_bound.nml:")
        print("=" * 50)
        with open(namelists_dir / "ww3_bound.nml", "r") as f:
            content = f.read()
            print(content)
        print("=" * 50)

        return True


if __name__ == "__main__":
    success = test_ww3_control_file_generation()
    if success:
        print("\n✓ Test passed: WW3 control files generated correctly!")
    else:
        print("\n✗ Test failed: Issues found in WW3 control file generation.")
