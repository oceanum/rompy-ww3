"""
Test cases for WW3 Config class.
"""

import tempfile
from pathlib import Path
from rompy.core.time import TimeRange
from rompy_ww3.config import ShelConfig
from rompy_ww3.namelists import Domain, HomogInput, Timesteps
from rompy_ww3.components import Shel, Grid
from rompy_ww3.namelists.field import Field
from rompy_ww3.namelists.point import Point
from datetime import datetime


def test_config_with_namelists():
    """Test Config class with namelist components."""

    # Create components instead of individual namelist objects
    from rompy_ww3.namelists.input import Input

    shell_component = Shel(
        domain=Domain(
            start=datetime(2023, 1, 1, 0, 0, 0),
            stop=datetime(2023, 1, 2, 0, 0, 0),
            iostyp=1,
        ),
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
    config = ShelConfig(
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
        domain=Domain(
            start=datetime(2023, 1, 1, 0, 0, 0),
            stop=datetime(2023, 1, 2, 0, 0, 0),
            iostyp=1,
        ),
        input_nml=Input(),
        homog_input=[
            HomogInput(name="WND", date="20230101 000000", value1=10.0, value2=90.0),
        ],
    )

    grid_component = Grid(
        timesteps=Timesteps(dtmax=2700.0, dtxy=900.0, dtkth=1350.0, dtmin=10.0),
    )

    # Create config
    config = ShelConfig(
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


def test_config_stride_functionality():
    """Test that stride values are set to period.interval when not already set."""
    # Create a TimeRange with a specific interval
    period = TimeRange(start="2023-01-01", end="2023-01-10", interval="6h")
    expected_stride = int(period.interval.total_seconds())  # 21600 seconds (6 hours)

    from rompy_ww3.components import Ounf, Ounp

    # Create point component with timestride attribute
    point_component = Point(
        timestride=None,  # Initially None
        list="all",
    )

    ounp_component = Ounp(point_nml=point_component)

    # Create field component with timestride attribute
    field_component = Field(
        timestride=None,  # Initially None
        list="hs tm01 dir",
        timeunit="S",
        timeepoch="20230101.000000",
    )

    ounf_component = Ounf(field=field_component)

    config = ShelConfig(
        ww3_ounf=ounf_component,  # Output field component
        ww3_ounp=ounp_component,  # Output point component
    )

    # Create runtime mock with period
    class MockRuntime:
        def __init__(self, period):
            self.period = period
            self.staging_dir = "/tmp"

    runtime = MockRuntime(period)

    # Before calling _set_default_dates
    assert config.ww3_ounf.field.timestride is None
    assert config.ww3_ounp.point_nml.timestride is None

    # Call the method that should set the stride
    config._set_default_dates(runtime)

    # After calling, stride values should be set to interval in seconds (as int)
    assert isinstance(config.ww3_ounf.field.timestride, int)
    assert isinstance(config.ww3_ounp.point_nml.timestride, int)
    assert config.ww3_ounf.field.timestride == expected_stride
    assert config.ww3_ounp.point_nml.timestride == expected_stride


def test_config_stride_preserves_existing_values():
    """Test that existing stride values are preserved when not None."""
    # Create a TimeRange with a specific interval
    period = TimeRange(start="2023-01-01", end="2023-01-10", interval="6h")
    existing_stride = "3600"  # 1 hour in seconds

    from rompy_ww3.components import Ounf, Ounp

    # Create point component with existing timestride value
    point_component_with_stride = Point(
        timestride=existing_stride,  # Initially set to specific value
        list="all",
    )

    ounp_component = Ounp(point_nml=point_component_with_stride)

    # Create field component with existing timestride value
    field_component_with_stride = Field(
        timestride=existing_stride,  # Initially set to specific value
        list="hs tm01 dir",
        timeunit="S",
        timeepoch="20230101.000000",
    )

    ounf_component = Ounf(field=field_component_with_stride)

    config = ShelConfig(
        ww3_ounf=ounf_component,  # Output field component
        ww3_ounp=ounp_component,  # Output point component
    )

    # Create runtime mock with period
    class MockRuntime:
        def __init__(self, period):
            self.period = period
            self.staging_dir = "/tmp"

    runtime = MockRuntime(period)

    # Before calling _set_default_dates
    assert config.ww3_ounf.field.timestride == int(existing_stride)
    assert config.ww3_ounp.point_nml.timestride == int(existing_stride)

    # Call the method that should preserve existing stride values
    config._set_default_dates(runtime)

    # After calling, existing stride values should be preserved
    assert config.ww3_ounf.field.timestride == int(existing_stride)
    assert config.ww3_ounp.point_nml.timestride == int(existing_stride)


def test_output_date_initialization_when_output_type_active():
    """Test that output_date and its nested components are initialized when output_type is active but output_date is None."""
    from rompy_ww3.components import Shel
    from rompy_ww3.namelists.output_type import OutputType, OutputTypeField

    # Create a TimeRange with specific dates
    period = TimeRange(start="2023-01-01", end="2023-01-10", interval="6h")

    # Create output type with field active
    output_type = OutputType(
        field=OutputTypeField(list="hs tm01 dir")  # Field is active with a list
    )

    # Create shell component with output_type set but output_date is None
    shell_component = Shel(
        output_type=output_type,
        output_date=None,  # This is intentionally None
    )

    config = ShelConfig(ww3_shel=shell_component)

    # Create runtime mock with period
    class MockRuntime:
        def __init__(self, period):
            self.period = period
            self.staging_dir = "/tmp"

    runtime = MockRuntime(period)

    # Before calling _set_default_dates
    assert config.ww3_shel.output_type.field.list == "hs tm01 dir"
    assert config.ww3_shel.output_date is None

    # Call the method that should initialize output_date when output_type is active
    config._set_default_dates(runtime)

    # After calling, output_date should be initialized
    assert config.ww3_shel.output_date is not None
    # And the nested field should also be initialized
    assert config.ww3_shel.output_date.field is not None
    # And it should have the start/stop/stride set from the period
    assert config.ww3_shel.output_date.field.start is not None
    assert config.ww3_shel.output_date.field.stop is not None
    assert config.ww3_shel.output_date.field.stride is not None


def test_output_date_not_initialized_when_output_type_inactive():
    """Test that output_date is not initialized when output_type is not active."""
    from rompy_ww3.components import Shel
    from rompy_ww3.namelists.output_type import OutputType

    # Create a TimeRange with specific dates
    period = TimeRange(start="2023-01-01", end="2023-01-10", interval="6h")

    # Create output type with nothing active (all None)
    output_type = OutputType()

    # Create shell component with output_type set but nothing active and output_date is None
    shell_component = Shel(
        output_type=output_type,
        output_date=None,  # This is intentionally None
    )

    config = ShelConfig(ww3_shel=shell_component)

    # Create runtime mock with period
    class MockRuntime:
        def __init__(self, period):
            self.period = period
            self.staging_dir = "/tmp"

    runtime = MockRuntime(period)

    # Before calling _set_default_dates
    assert config.ww3_shel.output_type.field is None
    assert config.ww3_shel.output_date is None

    # Call the method that should NOT initialize output_date when output_type is inactive
    config._set_default_dates(runtime)

    # After calling, output_date should still be None
    assert config.ww3_shel.output_date is None


if __name__ == "__main__":
    test_config_with_namelists()
    test_nml_config_integration()
    test_config_stride_functionality()
    test_config_stride_preserves_existing_values()
    test_output_date_initialization_when_output_type_active()
    test_output_date_not_initialized_when_output_type_inactive()
    print("\nConfig tests passed!")
