"""Extended tests for WW3 ForcingField class functionality."""

import pytest
from rompy_ww3.namelists.forcing import ForcingField


def test_forcing_field_string_interface():
    """Test the string-based interface for ForcingField."""
    print("Testing ForcingField with string-based initialization...")

    # Test with winds
    field = ForcingField(variable="WINDS")
    print(f"  Variable: {field.ww3_var_name}")
    print(f"  winds field: {field.winds}")
    print(f"  currents field: {field.currents}")
    print(f"  water_levels field: {field.water_levels}")
    assert field.winds is True
    assert field.currents is False
    assert field.water_levels is False
    assert field.ww3_var_name == "WINDS"
    print("  ✓ String-based interface works for WINDS")

    # Test with water levels
    field = ForcingField(variable="WATER_LEVELS")
    print(f"  Variable: {field.ww3_var_name}")
    print(f"  winds field: {field.winds}")
    print(f"  currents field: {field.currents}")
    print(f"  water_levels field: {field.water_levels}")
    assert field.winds is False
    assert field.currents is False
    assert field.water_levels is True
    assert field.ww3_var_name == "WATER_LEVELS"
    print("  ✓ String-based interface works for WATER_LEVELS")

    print("  ✓ All string-based tests passed")


def test_forcing_field_boolean_interface():
    """Test the original boolean-based interface for ForcingField."""
    print("\nTesting ForcingField with boolean-based initialization...")

    # Test with winds
    field = ForcingField(winds=True)
    print(f"  Variable: {field.ww3_var_name}")
    print(f"  winds field: {field.winds}")
    print(f"  currents field: {field.currents}")
    print(f"  water_levels field: {field.water_levels}")
    assert field.winds is True
    assert field.currents is None  # Should be None, not False
    assert field.water_levels is None  # Should be None, not False
    assert field.ww3_var_name == "WINDS"
    print("  ✓ Boolean-based interface works for WINDS")

    # Test with water levels
    field = ForcingField(water_levels=True)
    print(f"  Variable: {field.ww3_var_name}")
    print(f"  winds field: {field.winds}")
    print(f"  currents field: {field.currents}")
    print(f"  water_levels field: {field.water_levels}")
    assert field.winds is None  # Should be None, not False
    assert field.currents is None  # Should be None, not False
    assert field.water_levels is True
    assert field.ww3_var_name == "WATER_LEVELS"
    print("  ✓ Boolean-based interface works for WATER_LEVELS")

    print("  ✓ All boolean-based tests passed")


def test_validation():
    """Test that validation still works properly."""
    print("\nTesting validation...")

    # Test that only one field can be True at a time
    with pytest.raises(ValueError, match="Only one FORCING%FIELD can be set to True"):
        ForcingField(winds=True, currents=True)

    # Test that using variable with another field being True raises an error
    with pytest.raises(ValueError, match="Only one FORCING%FIELD can be set to True"):
        ForcingField(variable="WINDS", currents=True)

    print("  ✓ All validation tests passed")


def test_case_insensitive_variations():
    """Test case-insensitive variable names."""
    # Test WINDS variations
    for var in ["WINDS", "winds", "WIND", "wind"]:
        field = ForcingField(variable=var)
        assert field.winds is True, f"winds should be True for variable '{var}'"
        assert field.currents is False, f"currents should be False for variable '{var}'"
        assert field.water_levels is False, (
            f"water_levels should be False for variable '{var}'"
        )

    # Test CURRENTS variations
    for var in ["CURRENTS", "currents", "CURRENT", "current"]:
        field = ForcingField(variable=var)
        assert field.currents is True, f"currents should be True for variable '{var}'"
        assert field.winds is False, f"winds should be False for variable '{var}'"
        assert field.water_levels is False, (
            f"water_levels should be False for variable '{var}'"
        )

    # Test WATER_LEVELS variations
    for var in ["WATER_LEVELS", "water_levels", "LEVEL", "level"]:
        field = ForcingField(variable=var)
        assert field.water_levels is True, (
            f"water_levels should be True for variable '{var}'"
        )
        assert field.winds is False, f"winds should be False for variable '{var}'"
        assert field.currents is False, f"currents should be False for variable '{var}'"

    print("  ✓ All case-insensitive tests passed")


if __name__ == "__main__":
    test_forcing_field_string_interface()
    test_forcing_field_boolean_interface()
    test_validation()
    test_case_insensitive_variations()
    print("\n🎉 All tests passed! Both interfaces work correctly.")
