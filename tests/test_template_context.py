"""
Test cases for WW3 template context generation.
"""

import tempfile
from pathlib import Path
from rompy_ww3.config import ShelConfig
from rompy_ww3.namelists import Domain
from rompy_ww3.components import Shel as ShellComponent
from rompy_ww3.namelists.input import Input


def test_template_context_generation():
    """Test template context generation."""
    # Create shell component
    shell_component = ShellComponent(
        domain=Domain(start="20230101 000000", stop="20230102 000000", iostyp=1),
        input_nml=Input(),
    )

    # Create config with component
    config = ShelConfig(
        ww3_shel=shell_component,
    )

    # Generate template context
    context = config.get_template_context()

    print("Template context keys:")
    for key in context.keys():
        print(f"  - {key}")

    # Check that expected keys are present
    assert "config" in context
    assert "namelists" in context

    print("\nTemplate context generation test passed!")


def test_run_script_generation():
    """Test run script generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workdir = Path(tmpdir)

        # Generate run scripts
        config = ShelConfig(
            ww3_shel=ShellComponent(
                domain=Domain(
                    start="20230101 000000", stop="20230102 000000", iostyp=0
                ),
                input_nml=Input(),
            ),
            ww3_grid=None,
            multi_component=None,
            ww3_bounc=None,
            ww3_prnc=None,
            ww3_track=None,
            ww3_ounf=None,
            ww3_ounp=None,
            ww3_upstr=None,
            namelists=None,
        )

        config.generate_run_script(workdir)

        # Check that scripts were created
        run_script = workdir / "run_ww3.sh"
        preprocess_script = workdir / "preprocess_ww3.sh"
        postprocess_script = workdir / "postprocess_ww3.sh"
        full_script = workdir / "full_ww3.sh"

        assert run_script.exists()
        assert preprocess_script.exists()
        assert postprocess_script.exists()
        assert full_script.exists()

        print(f"Generated run scripts in {workdir}")
        print("\nRun script generation test passed!")


if __name__ == "__main__":
    test_template_context_generation()
    test_run_script_generation()
    print("\nAll template context tests passed!")
