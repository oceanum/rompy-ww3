"""
Test cases for WW3 namelist composition system.
"""

import tempfile
from pathlib import Path
from rompy_ww3.namelist_composer import NamelistComposition, compose_namelists
from rompy_ww3.namelists import Domain, Input, HomogCount, HomogInput, Timesteps
from rompy_ww3.config import Config


def test_namelist_composition():
    """Test namelist composition system."""

    # Create namelist components
    domain = Domain(start="20230101 000000", stop="20230102 000000", iostyp=1)

    input_nml = Input(forcing={"winds": "T", "water_levels": "T"})

    homog_count = HomogCount(n_wnd=2, n_lev=1)

    homog_input = [
        HomogInput(name="WND", date="20230101 000000", value1=10.0, value2=90.0),
        HomogInput(name="WND", date="20230101 060000", value1=15.0, value2=120.0),
        HomogInput(name="LEV", date="20230101 060000", value1=2.0),
    ]

    # Create composition
    composition = NamelistComposition(
        domain=domain,
        input_nml=input_nml,
        homog_count=homog_count,
        homog_input=homog_input,
    )

    # Test validation
    completeness_issues = composition.validate_completeness()
    consistency_issues = composition.validate_consistency()

    print("Completeness issues:")
    print(completeness_issues)

    print("\nConsistency issues:")
    print(consistency_issues)

    # Should have no issues
    assert len(completeness_issues) == 0
    assert len(consistency_issues) == 0

    # Test rendering
    namelists = composition.render_all_namelists()

    print(f"\nRendered {len(namelists)} namelists:")
    for name in namelists.keys():
        print(f"  - {name}")

    assert "domain.nml" in namelists
    assert "input.nml" in namelists
    assert "homog_count.nml" in namelists
    assert "homog_input.nml" in namelists

    # Test writing files
    with tempfile.TemporaryDirectory() as tmpdir:
        workdir = Path(tmpdir) / "namelists"
        composition.write_all_namelists(workdir)

        # Check that files were created
        domain_file = workdir / "domain.nml"
        input_file = workdir / "input.nml"
        homog_count_file = workdir / "homog_count.nml"
        homog_input_file = workdir / "homog_input.nml"

        assert domain_file.exists()
        assert input_file.exists()
        assert homog_count_file.exists()
        assert homog_input_file.exists()

        print(f"\nCreated namelist files in {workdir}")


def test_composition_from_config():
    """Test creating composition from Config object."""

    # Create a config with namelist components
    config = Config(
        domain=Domain(start="20230101 000000", stop="20230102 000000"),
        input_nml=Input(forcing={"winds": "T"}),
        timesteps=Timesteps(dtmax=2700.0, dtxy=900.0, dtkth=1350.0, dtmin=10.0),
    )

    # Create composition from config
    composition = compose_namelists(config)

    # Test that components were transferred
    assert composition.domain is not None
    assert composition.input_nml is not None
    assert composition.domain.start == "20230101 000000"
    assert composition.input_nml.forcing.winds == "T"

    print("Composition from config test passed!")


if __name__ == "__main__":
    test_namelist_composition()
    test_composition_from_config()
    print("\nNamelist composition tests passed!")
