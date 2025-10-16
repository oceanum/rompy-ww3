"""
Test cases for WW3 Config class.
"""

import tempfile
from pathlib import Path
from rompy_ww3.config import Config
from rompy_ww3.namelists import Domain, Input, HomogInput, Timesteps


def test_config_with_namelists():
    """Test Config class with namelist components."""

    # Create a config with some namelist components
    config = Config(
        domain=Domain(start="20230101 000000", stop="20230102 000000", iostyp=1),
        input_nml=Input(forcing={"winds": "T", "water_levels": "T"}),
        timesteps=Timesteps(dtmax=2700.0, dtxy=900.0, dtkth=1350.0, dtmin=10.0),
        homog_input=[
            HomogInput(name="WND", date="20230101 000000", value1=10.0, value2=90.0),
            HomogInput(name="WND", date="20230101 060000", value1=15.0, value2=120.0),
        ],
    )

    # Test rendering namelists as strings (for template rendering)
    namelists = config.render_namelists()

    assert "domain.nml" in namelists
    assert "input.nml" in namelists
    assert "homog_input.nml" in namelists

    print("Domain namelist:")
    print(namelists["domain.nml"])

    print("\nInput namelist:")
    print(namelists["input.nml"])

    print("\nHomog input namelist:")
    print(namelists["homog_input.nml"])

    # Test writing to files - new behavior generates WW3 control files
    with tempfile.TemporaryDirectory() as tmpdir:
        runtime_mock = type("Runtime", (), {"staging_dir": tmpdir})()
        config(runtime_mock)

        # Check that the WW3 control namelists directory was created
        namelists_dir = Path(tmpdir) / "namelists"
        assert namelists_dir.exists()

        # Check that WW3 control files were created (not individual namelist files)
        shel_file = namelists_dir / "ww3_shel.nml"
        grid_file = namelists_dir / "ww3_grid.nml"
        bound_file = namelists_dir / "ww3_bound.nml"

        assert shel_file.exists(), f"ww3_shel.nml was not created in {namelists_dir}"
        assert grid_file.exists(), f"ww3_grid.nml was not created in {namelists_dir}"
        assert bound_file.exists(), f"ww3_bound.nml was not created in {namelists_dir}"

        # Verify the shell file contains the expected namelist sections
        with open(shel_file, "r") as f:
            shel_content = f.read()
            assert "&DOMAIN_NML" in shel_content
            assert "&INPUT_NML" in shel_content
            assert "&HOMOG_INPUT_NML" in shel_content

        print(f"\nCreated WW3 control files in {namelists_dir}")


if __name__ == "__main__":
    test_config_with_namelists()
    print("\nConfig test passed!")
