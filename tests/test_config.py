"""
Test cases for WW3 Config class.
"""

import tempfile
from pathlib import Path
from rompy_ww3.config import Config
from rompy_ww3.namelists import Domain, Input, HomogInput


def test_config_with_namelists():
    """Test Config class with namelist components."""
    
    # Create a config with some namelist components
    config = Config(
        domain=Domain(
            start="20230101 000000",
            stop="20230102 000000",
            iostyp=1
        ),
        input_nml=Input(
            forcing={
                "winds": "T",
                "water_levels": "T"
            }
        ),
        homog_input=[
            HomogInput(
                name="WND",
                date="20230101 000000",
                value1=10.0,
                value2=90.0
            ),
            HomogInput(
                name="WND",
                date="20230101 060000",
                value1=15.0,
                value2=120.0
            )
        ]
    )
    
    # Test rendering namelists as strings
    namelists = config.render_namelists()
    
    assert "domain.nml" in namelists
    assert "input.nml" in namelists
    assert "homog_input.nml" in namelists
    
    print("Domain namelist:")
    print(namelists["domain.nml"])
    
    print("\\nInput namelist:")
    print(namelists["input.nml"])
    
    print("\\nHomog input namelist:")
    print(namelists["homog_input.nml"])
    
    # Test writing to files
    with tempfile.TemporaryDirectory() as tmpdir:
        runtime_mock = type('Runtime', (), {'staging_dir': tmpdir})()
        result = config(runtime_mock)
        
        # Check that the namelists were created
        namelists_dir = Path(tmpdir) / "namelists"
        assert namelists_dir.exists()
        
        domain_file = namelists_dir / "domain.nml"
        input_file = namelists_dir / "input.nml"
        homog_input_file = namelists_dir / "homog_input.nml"
        
        assert domain_file.exists()
        assert input_file.exists()
        assert homog_input_file.exists()
        
        print(f"\\nCreated namelist files in {namelists_dir}")


if __name__ == "__main__":
    test_config_with_namelists()
    print("\\nConfig test passed!")
