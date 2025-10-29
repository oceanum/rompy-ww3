"""
Test cases for WW3 Config class.
"""

import tempfile
from pathlib import Path
from rompy_ww3.config import NMLConfig
from rompy_ww3.namelists import Domain, HomogInput, Timesteps
from rompy_ww3.components import Shel, Grid


def test_config_with_namelists():
    """Test Config class with namelist components."""

    # Create components instead of individual namelist objects
    from rompy_ww3.namelists.input import Input

    shell_component = Shel(
        domain=Domain(start="20230101 000000", stop="20230102 000000", iostyp=1),
        input_nml=Input(),
        homog_input=[
            HomogInput(name="WND", date="20230101 000000", value1=10.0, value2=90.0),
            HomogInput(name="WND", date="20230101 060000", value1=15.0, value2=120.0),
        ],
    )

    grid_component = Grid(
        timesteps=Timesteps(dtmax=2700.0, dtxy=900.0, dtkth=1350.0, dtmin=10.0),
    )

    # Create a config with components
    config = NMLConfig(
        ww3_shel=shell_component,
        ww3_grid=grid_component,
    )

    # Test that config can be created and has the expected components
    assert config.ww3_shel is not None
    assert config.ww3_grid is not None

    print("Config created successfully with shell and grid components")


def test_nml_config_integration():
    """Test NMLConfig integration with runtime."""
    from rompy_ww3.namelists.input import Input

    shell_component = Shel(
        domain=Domain(start="20230101 000000", stop="20230102 000000", iostyp=1),
        input_nml=Input(),
        homog_input=[
            HomogInput(name="WND", date="20230101 000000", value1=10.0, value2=90.0),
        ],
    )

    grid_component = Grid(
        timesteps=Timesteps(dtmax=2700.0, dtxy=900.0, dtkth=1350.0, dtmin=10.0),
    )

    # Create config
    config = NMLConfig(
        ww3_shel=shell_component,
        ww3_grid=grid_component,
    )

    # Test writing to files - new behavior generates WW3 control files
    with tempfile.TemporaryDirectory() as tmpdir:
        runtime_mock = type(
            "Runtime", (), {"staging_dir": Path(tmpdir), "period": None}
        )()

        # Call the config with runtime (this will write control files)
        config(runtime_mock)

        # Check that WW3 control files were created in the staging directory
        shel_file = Path(tmpdir) / "ww3_shel.nml"
        grid_file = Path(tmpdir) / "ww3_grid.nml"

        # The files should exist
        assert shel_file.exists(), f"ww3_shel.nml was not created in {tmpdir}"
        assert grid_file.exists(), f"ww3_grid.nml was not created in {tmpdir}"

        # Verify the shell file contains the expected namelist sections
        with open(shel_file, "r") as f:
            shel_content = f.read()
            assert "&DOMAIN_NML" in shel_content

        print(f"\nCreated WW3 control files in {tmpdir}")


if __name__ == "__main__":
    test_config_with_namelists()
    test_nml_config_integration()
    print("\nConfig tests passed!")
