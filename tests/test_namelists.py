"""
Test cases for WW3 namelist classes.
"""

import tempfile
from pathlib import Path
from rompy_ww3.namelists import Domain, Input, OutputType, OutputDate, HomogCount
from datetime import datetime


def test_domain_nml():
    """Test DOMAIN_NML creation and rendering."""
    domain = Domain(
        start=datetime(2023, 1, 1, 0, 0, 0),
        stop=datetime(2023, 1, 2, 0, 0, 0),
        iostyp=1,
    )

    rendered = domain.render()
    print("Rendered DOMAIN_NML:")
    print(rendered)

    assert "&DOMAIN_NML" in rendered
    assert "START" in rendered
    assert "STOP" in rendered
    assert "IOSTYP" in rendered
    assert "/" in rendered

    print("DOMAIN_NML test passed")


def test_input_nml():
    """Test INPUT_NML creation and rendering."""
    input_nml = Input(forcing={"winds": "T", "water_levels": "T"})

    rendered = input_nml.render()
    print("\nRendered INPUT_NML:")
    print(rendered)

    assert "&INPUT_NML" in rendered
    assert "FORCING%WINDS" in rendered
    assert "FORCING%WATER_LEVELS" in rendered
    assert "/" in rendered

    print("INPUT_NML test passed")


def test_output_type_nml():
    """Test OUTPUT_TYPE_NML creation and rendering."""
    output_type = OutputType(field={"list": "HS DIR SPR"})

    rendered = output_type.render()
    print("\nRendered OUTPUT_TYPE_NML:")
    print(rendered)

    assert "&OUTPUT_TYPE_NML" in rendered
    assert "FIELD%LIST" in rendered
    assert "/" in rendered

    print("OUTPUT_TYPE_NML test passed")


def test_output_date_nml():
    """Test OUTPUT_DATE_NML creation and rendering."""
    output_date = OutputDate(
        field={
            "start": datetime(2023, 1, 1, 0, 0, 0),
            "stride": 3600,
            "stop": datetime(2023, 1, 2, 0, 0, 0),
        }
    )

    rendered = output_date.render()
    print("\nRendered OUTPUT_DATE_NML:")
    print(rendered)

    assert "&OUTPUT_DATE_NML" in rendered
    assert "FIELD%START" in rendered
    assert "FIELD%STRIDE" in rendered
    assert "FIELD%STOP" in rendered
    assert "/" in rendered

    print("OUTPUT_DATE_NML test passed")


def test_homog_count_nml():
    """Test HOMOG_COUNT_NML creation and rendering."""
    homog_count = HomogCount(n_wnd=2, n_lev=1)

    rendered = homog_count.render()
    print("\nRendered HOMOG_COUNT_NML:")
    print(rendered)

    assert "&HOMOG_COUNT_NML" in rendered
    assert "N_WND" in rendered
    assert "N_LEV" in rendered
    assert "/" in rendered

    print("HOMOG_COUNT_NML test passed")


def test_file_writing():
    """Test writing namelists to files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        domain = Domain(
            start=datetime(2023, 1, 1, 0, 0, 0), stop=datetime(2023, 1, 2, 0, 0, 0)
        )

        tmp_path = Path(tmpdir)
        domain.write_nml(tmp_path)

        nml_file = tmp_path / "domain.nml"
        assert nml_file.exists()

        content = nml_file.read_text()
        assert "&DOMAIN_NML" in content
        assert "START" in content
        assert "STOP" in content
        assert "/" in content

    print("File writing test passed")


if __name__ == "__main__":
    test_domain_nml()
    test_input_nml()
    test_output_type_nml()
    test_output_date_nml()
    test_homog_count_nml()
    test_file_writing()
    print("\nAll tests passed!")
