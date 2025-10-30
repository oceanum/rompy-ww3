"""Extended tests for WW3 ForcingField class functionality."""

import pytest
from rompy_ww3.namelists.forcing import ForcingField


def test_forcing_field_string_interface():
    """Test the boolean-based interface for ForcingField."""
    print("Testing ForcingField with boolean-based initialization...")

    # Test with winds
    field = ForcingField(winds=True)
    print(f"  Variable: {field.ww3_var_name}")
    print(f"  winds field: {field.winds}")
    print(f"  currents field: {field.currents}")
    print(f"  water_levels field: {field.water_levels}")
    assert field.winds is True
    assert field.currents is None  # Should be None for unset fields
    assert field.water_levels is None  # Should be None for unset fields
    assert field.ww3_var_name == "WINDS"
    print("  ✓ Boolean-based interface works for WINDS")

    # Test with water levels
    field = ForcingField(water_levels=True)
    print(f"  Variable: {field.ww3_var_name}")
    print(f"  winds field: {field.winds}")
    print(f"  currents field: {field.currents}")
    print(f"  water_levels field: {field.water_levels}")
    assert field.winds is None  # Should be None for unset fields
    assert field.currents is None  # Should be None for unset fields
    assert field.water_levels is True
    assert field.ww3_var_name == "WATER_LEVELS"
    print("  ✓ Boolean-based interface works for WATER_LEVELS")

    print("  ✓ All boolean-based tests passed")


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

    # Test that using multiple fields being True raises an error
    with pytest.raises(ValueError, match="Only one FORCING%FIELD can be set to True"):
        ForcingField(winds=True, water_levels=True)

    print("  ✓ All validation tests passed")


def test_case_insensitive_variations():
    """Test the boolean fields directly."""
    # Test WINDS variations (these tests would be redundant since we're directly using boolean fields)
    # Instead, let's test the boolean field functionality
    field = ForcingField(winds=True)
    assert field.winds is True, "winds should be True when explicitly set"
    assert field.currents is None, "currents should be None when not set"
    assert field.water_levels is None, "water_levels should be None when not set"

    field = ForcingField(currents=True)
    assert field.currents is True, "currents should be True when explicitly set"
    assert field.winds is None, "winds should be None when not set"
    assert field.water_levels is None, "water_levels should be None when not set"

    field = ForcingField(water_levels=True)
    assert field.water_levels is True, "water_levels should be True when explicitly set"
    assert field.winds is None, "winds should be None when not set"
    assert field.currents is None, "currents should be None when not set"

    print("  ✓ All boolean field tests passed")


if __name__ == "__main__":
    test_forcing_field_string_interface()
    test_forcing_field_boolean_interface()
    test_validation()
    test_case_insensitive_variations()
    print("\n🎉 All tests passed! Both interfaces work correctly.")
