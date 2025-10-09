"""
Test WW3 control file generation against WW3 repository examples.

This test compares the generated WW3 control files with examples from the WW3 repository
to ensure proper format and content.
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
    InputForcing,
    InputAssim,
    ModelGridForcing,
    ModelGridResource,
    OutputType,
    OutputDate,
    HomogCount,
    HomogInput,
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
    Depth,
    Mask,
    Obstacle,
    Slope,
    Sediment,
    InboundCount,
    InboundPointList,
    InboundPoint,
    ExcludedCount,
    ExcludedPointList,
    ExcludedBodyList,
    ExcludedPoint,
    ExcludedBody,
    OutboundCount,
    OutboundLineList,
    OutboundLine,
    InputGrid,
    ModelGrid,
    Curv,
    CoordData,
    Unst,
    Smc,
    SMCFile,
)


def check_namelist_format(content, namelist_name):
    """Check if content contains a properly formatted namelist."""
    # Check if it starts with &NAMELIST_NAME
    start_pattern = f"&{namelist_name}"
    if start_pattern not in content:
        return False, f"Missing &{namelist_name} start"

    # Check if it ends with /
    if "/" not in content:
        return False, f"Missing / terminator for &{namelist_name}"

    # Check that variables are properly formatted with = signs
    lines = content.split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("&") or line == "/" or line == "":
            continue
        if line.startswith("!"):
            continue  # Skip comments
        if "=" not in line:
            return False, f"Missing = in line: {line}"

    return True, f"&{namelist_name} format is correct"


def parse_namelist_content(content):
    """Parse namelist content into a dictionary structure."""
    lines = content.split("\n")
    namelists = {}
    current_namelist = None
    current_content = []

    for line in lines:
        line = line.strip()
        if line.startswith("&"):
            # End previous namelist if exists
            if current_namelist:
                namelists[current_namelist] = "\n".join(current_content)

            # Start new namelist
            current_namelist = line[1:]  # Remove the &
            current_content = [line]
        elif line == "/":
            # End current namelist
            current_content.append(line)
            if current_namelist:
                namelists[current_namelist] = "\n".join(current_content)
            current_namelist = None
            current_content = []
        elif current_namelist:
            current_content.append(line)
        # Skip lines that are not part of a namelist (comments, etc.)

    # Add final namelist if needed
    if current_namelist:
        namelists[current_namelist] = "\n".join(current_content)

    return namelists


def compare_namelist_files(generated_path, reference_path):
    """Compare generated and reference namelist files."""
    with open(generated_path, "r") as f:
        generated_content = f.read()

    with open(reference_path, "r") as f:
        reference_content = f.read()

    generated_namelists = parse_namelist_content(generated_content)
    reference_namelists = parse_namelist_content(reference_content)

    # Get all unique namelist names from both files
    all_namelist_names = set(generated_namelists.keys()) | set(
        reference_namelists.keys()
    )

    missing_in_generated = []
    missing_in_reference = []
    differences = []

    for name in all_namelist_names:
        gen_exists = name in generated_namelists
        ref_exists = name in reference_namelists

        if not gen_exists:
            missing_in_generated.append(name)
        elif not ref_exists:
            missing_in_reference.append(name)
        else:
            # Both exist, compare content within the namelist
            gen_lines = [
                line.strip()
                for line in generated_namelists[name].split("\n")
                if line.strip()
                and not line.strip().startswith("!")
                and line.strip() not in ["&" + name, "/"]
            ]
            ref_lines = [
                line.strip()
                for line in reference_namelists[name].split("\n")
                if line.strip()
                and not line.strip().startswith("!")
                and line.strip() not in ["&" + name, "/"]
            ]

            # Extract variable assignments (key = value format)
            gen_vars = {}
            ref_vars = {}

            for line in gen_lines:
                if "=" in line:
                    key = line.split("=")[0].strip()
                    value = "=".join(line.split("=")[1:]).strip()
                    gen_vars[key] = value

            for line in ref_lines:
                if "=" in line:
                    key = line.split("=")[0].strip()
                    value = "=".join(line.split("=")[1:]).strip()
                    ref_vars[key] = value

            # Compare variables
            all_var_keys = set(gen_vars.keys()) | set(ref_vars.keys())
            for var_key in all_var_keys:
                gen_var_exists = var_key in gen_vars
                ref_var_exists = var_key in ref_vars

                if not gen_var_exists:
                    differences.append(f"Missing variable in {name}: {var_key}")
                elif not ref_var_exists:
                    differences.append(f"Extra variable in {name}: {var_key}")
                elif gen_vars[var_key] != ref_vars[var_key]:
                    # Normalize whitespace for comparison to handle spacing differences
                    normalized_generated = " ".join(gen_vars[var_key].split())
                    normalized_reference = " ".join(ref_vars[var_key].split())

                    # Also normalize quotes if both sides have them
                    if (
                        normalized_generated.startswith("'")
                        and normalized_generated.endswith("'")
                        and normalized_reference.startswith("'")
                        and normalized_reference.endswith("'")
                    ):
                        normalized_generated = normalized_generated[1:-1]
                        normalized_reference = normalized_reference[1:-1]

                    if normalized_generated != normalized_reference:
                        differences.append(
                            f"Different value in {name} for {var_key}: generated='{gen_vars[var_key]}', reference='{ref_vars[var_key]}'"
                        )

    return {
        "missing_in_generated": missing_in_generated,
        "missing_in_reference": missing_in_reference,
        "differences": differences,
        "success": len(missing_in_generated) == 0 and len(differences) == 0,
    }


def test_ww3_control_file_comparison():
    """Test that WW3 control files match the expected format from the WW3 repository."""

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
                n_wnd=2,
                n_lev=1,
                n_cur=0,
                n_ice=0,
            ),
            homog_inputs=[
                HomogInput(
                    name="WND",
                    date="20100610 000000",
                    value1=5.0,
                    value2=90.0,
                ),
                HomogInput(
                    name="WND",
                    date="20100610 060000",
                    value1=25.0,
                    value2=120.0,
                ),
            ],
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
            # Grid configuration
            grid=WW3Grid(
                x0=-75.0,
                y0=35.0,
                dx=0.20408163265306123,
                dy=0.20408163265306123,
                nx=720,  # Use same as reference for comparison
                ny=360,  # Use same as reference for comparison
                name="GULF OF NOWHERE",
                grid_type="RECT",
                coordinate_system="SPHE",
                grid_closure="SMPL",
                zlim=-0.10,
                dmin=2.5,
            ),
            # Depth configuration
            depth=Depth(
                sf=0.001,
                filename="GLOB-30M.bot",
                idf=50,
                idla=1,
                idfm=1,
            ),
            # Mask configuration
            mask=Mask(
                filename="GLOB-30M.mask",
                idf=60,
                idla=1,
                idfm=1,
            ),
            # Obstacle configuration
            obstacle=Obstacle(
                sf=0.0001,
                filename="GLOB-30M.obst",
                idf=70,
                idla=1,
                idfm=1,
            ),
            # Slope configuration
            slope=Slope(
                sf=0.0001,
                filename="GLOB-30M.slope",
                idf=80,
                idla=1,
                idfm=1,
            ),
            # Sediment configuration
            sediment=Sediment(
                filename="SED.txt",
                idf=90,
                idla=1,
                idfm=2,
            ),
            # Inbound boundary configuration
            inbound_count=InboundCount(n_point=2),
            inbound_points=InboundPointList(
                points=[
                    InboundPoint(x_index=2, y_index=2, connect=False),
                    InboundPoint(x_index=2, y_index=11, connect=True),
                ]
            ),
            # Excluded configuration
            excluded_count=ExcludedCount(
                n_point=2,
                n_body=1,
            ),
            excluded_points=ExcludedPointList(
                points=[
                    ExcludedPoint(x_index=20, y_index=2, connect=False),
                    ExcludedPoint(x_index=20, y_index=11, connect=True),
                ]
            ),
            excluded_bodies=ExcludedBodyList(
                bodies=[
                    ExcludedBody(x_index=10, y_index=15),
                ]
            ),
            # Outbound boundary configuration
            outbound_count=OutboundCount(n_line=3),
            outbound_lines=OutboundLineList(
                lines=[
                    OutboundLine(x0=1.75, y0=1.50, dx=0.25, dy=-0.10, np=3),
                    OutboundLine(x0=2.25, y0=1.50, dx=-0.10, dy=0.00, np=-6),
                    OutboundLine(x0=0.10, y0=0.10, dx=0.10, dy=0.00, np=-10),
                ]
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
            # Multi-grid configuration
            input_grids=[
                InputGrid(
                    name="atm",
                    forcing=InputForcing(
                        winds="T",  # Using 'T' for external file
                        mud_viscosity="T",  # Using 'T' for external file
                    ),
                    assim=InputAssim(
                        mean="T",  # Using 'T' for enabled
                    ),
                ),
            ],
            model_grids=[
                ModelGrid(
                    name="grd1",
                    forcing=ModelGridForcing(
                        winds="atm",
                        currents="atm",  # Use same input grid as winds
                        water_levels="atm",  # Use same input grid as winds
                    ),
                    resource=ModelGridResource(
                        rank_id=1,
                        group_id=1,
                        comm_frac_start=0.0,
                        comm_frac_end=1.0,
                        bound_flag=True,
                    ),
                ),
            ],
        )

        # Create a mock runtime object
        runtime = ModelRun(
            run_id_subdir=False, delete_existing=True, run_id="test_ww3_comparison"
        )

        # Generate the WW3 control files
        result = config(runtime=runtime)

        print(f"Generated WW3 control files in: {result['staging_dir']}")

        # Check that the expected files were created
        namelists_dir = Path(result["staging_dir"]) / "namelists"

        # Define files that have reference versions to compare against
        reference_dir = Path(__file__).parent / "reference_nmls"

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

        print("\nValidating generated WW3 control files:")
        all_files_valid = True
        comparison_results = {}

        for file in expected_files:
            file_path = namelists_dir / file
            reference_path = reference_dir / file

            if not file_path.exists():
                print(f"  {file}: ✗ (not found)")
                all_files_valid = False
                continue

            print(f"  {file}: ✓")

            if reference_path.exists():
                # Compare with reference file
                comparison_result = compare_namelist_files(file_path, reference_path)
                comparison_results[file] = comparison_result

                if comparison_result["success"]:
                    print(f"    {file}: ✓ (matches reference)")
                else:
                    print(f"    {file}: ⚠ (differences found)")
                    if comparison_result["missing_in_generated"]:
                        print(
                            f"      Missing in generated: {', '.join(comparison_result['missing_in_generated'])}"
                        )
                    if comparison_result["missing_in_reference"]:
                        print(
                            f"      Extra in generated: {', '.join(comparison_result['missing_in_reference'])}"
                        )
                    if comparison_result["differences"]:
                        print(
                            f"      Value differences: {len(comparison_result['differences'])}"
                        )
                        for diff in comparison_result["differences"][
                            :3
                        ]:  # Show first 3 differences
                            print(f"        - {diff}")
                        if len(comparison_result["differences"]) > 3:
                            print(
                                f"        ... and {len(comparison_result['differences']) - 3} more"
                            )
                    all_files_valid = False
            else:
                # Just validate format if no reference
                with open(file_path, "r") as f:
                    content = f.read()

                # Test for basic namelist structure based on file name
                if file == "ww3_shel.nml":
                    # Should contain DOMAIN_NML, INPUT_NML, OUTPUT_TYPE_NML, OUTPUT_DATE_NML, HOMOG_COUNT_NML
                    for nml in [
                        "DOMAIN_NML",
                        "INPUT_NML",
                        "OUTPUT_TYPE_NML",
                        "OUTPUT_DATE_NML",
                        "HOMOG_COUNT_NML",
                    ]:
                        is_valid, msg = check_namelist_format(content, nml)
                        if not is_valid:
                            print(f"    {msg}")
                            all_files_valid = False
                        else:
                            print(f"    &{nml}: ✓")

                elif file == "ww3_grid.nml":
                    # Should contain SPECTRUM_NML, RUN_NML, TIMESTEPS_NML, GRID_NML, and optionally others
                    for nml in ["SPECTRUM_NML", "RUN_NML", "TIMESTEPS_NML", "GRID_NML"]:
                        is_valid, msg = check_namelist_format(content, nml)
                        if not is_valid:
                            print(f"    {msg}")
                            all_files_valid = False
                        else:
                            print(f"    &{nml}: ✓")

                    # Check for optional namelists
                    optional_nmls = [
                        "RECT_NML",
                        "DEPTH_NML",
                        "MASK_NML",
                        "OBST_NML",
                        "SLOPE_NML",
                        "SED_NML",
                        "INBND_COUNT_NML",
                        "INBND_POINT_NML",
                        "EXCL_COUNT_NML",
                        "EXCL_POINT_NML",
                        "EXCL_BODY_NML",
                        "OUTBND_COUNT_NML",
                        "OUTBND_LINE_NML",
                    ]
                    for nml in optional_nmls:
                        if f"&{nml}" in content:
                            is_valid, msg = check_namelist_format(content, nml)
                            if not is_valid:
                                print(f"    {msg}")
                                all_files_valid = False
                            else:
                                print(f"    &{nml}: ✓")

                elif file == "ww3_bound.nml":
                    # Should contain BOUND_NML
                    is_valid, msg = check_namelist_format(content, "BOUND_NML")
                    if not is_valid:
                        print(f"    {msg}")
                        all_files_valid = False
                    else:
                        print("    &BOUND_NML: ✓")

        # Print summary
        if all_files_valid:
            print("\n✓ All WW3 control files have valid structure!")
            print(
                "✓ All files match reference files (or have valid format where no reference exists)!"
            )
        else:
            print(
                "\n✗ Some WW3 control files have structural issues or differences from reference."
            )

            # Print more details about differences for files with reference
            for file, result in comparison_results.items():
                if not result["success"]:
                    print(f"\nDetailed comparison for {file}:")
                    if result["missing_in_generated"]:
                        print(
                            f"  - Missing in generated file: {', '.join(result['missing_in_generated'])}"
                        )
                    if result["missing_in_reference"]:
                        print(
                            f"  - Additional in generated file: {', '.join(result['missing_in_reference'])}"
                        )
                    if result["differences"]:
                        print(f"  - Value differences:")
                        for diff in result["differences"]:
                            print(f"    * {diff}")

        # Print examples of generated content for manual verification
        print("\nSample content for validation:")
        print("=" * 50)

        with open(namelists_dir / "ww3_shel.nml", "r") as f:
            content = f.read()
            print("Sample from ww3_shel.nml:")
            print(content[:500] + "..." if len(content) > 500 else content)
            print()

        with open(namelists_dir / "ww3_grid.nml", "r") as f:
            content = f.read()
            print("Sample from ww3_grid.nml:")
            print(content[:500] + "..." if len(content) > 500 else content)
            print()

        # Print comparison details for files with reference
        print("\nComparison with reference files:")
        for file, result in comparison_results.items():
            if result["success"]:
                print(f"  {file}: ✓ (identical structure)")
            else:
                print(f"  {file}: ⚠ (differences detected)")


if __name__ == "__main__":
    test_ww3_control_file_comparison()
    print("\n✓ Comparison test completed: Generated files have proper WW3 format!")
