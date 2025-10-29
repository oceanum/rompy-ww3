"""Tests for WW3 namelist rendering with nested objects."""

from rompy_ww3.namelists.forcing import Forcing, ForcingField, ForcingGrid


def test_nested_objects_render():
    """Test that nested BaseModel objects render correctly using their own render methods."""

    # Create nested objects - only one field can be True due to validation
    forcing_field = ForcingField(winds=True)

    forcing_grid = ForcingGrid(asis=True, latlon=False)

    # Create main object with nested objects - skip tidal for winds (tidal requires water_levels or currents)
    forcing = Forcing(field=forcing_field, grid=forcing_grid)

    # Render the namelist
    rendered = forcing.render()

    print("Rendered FORCING_NML with nested objects:")
    print(rendered)
    print()

    # Check that the output contains expected nested parameters
    expected_params = [
        "FORCING%FIELD%WINDS",
        "FORCING%GRID%ASIS",
        "FORCING%GRID%LATLON",
    ]

    # These should be present but the others should not be since only one field can be True
    unwanted_params = [
        "FORCING%FIELD%CURRENTS",
        "FORCING%FIELD%WATER_LEVELS",
        "FORCING%TIDAL",
    ]

    success = True
    for param in expected_params:
        if param not in rendered:
            print(f"MISSING parameter: {param}")
            success = False
        else:
            print(f"FOUND parameter: {param}")

    for param in unwanted_params:
        if param in rendered:
            print(f"UNEXPECTED parameter (should not be present): {param}")
            success = False
        else:
            print(f"CORRECTLY ABSENT parameter: {param}")

    print()
    if success:
        print(
            "✓ All expected parameters found and unwanted parameters absent in rendered output"
        )
    else:
        print("✗ Some parameters are missing or unexpected in rendered output")

    assert success, (
        "Nested objects should render all expected parameters and avoid invalid ones"
    )


def test_nested_with_dictionaries():
    """Test that the old dictionary approach still works."""

    # Create main object with nested dictionaries (old way) - only one field can be True
    forcing = Forcing(
        field={"winds": True},  # Only one field can be True due to validation
        grid={"asis": True, "latlon": False},
    )

    # Render the namelist
    rendered = forcing.render()

    print("Rendered FORCING_NML with nested dictionaries:")
    print(rendered)
    print()

    # Check that the output contains expected nested parameters
    expected_params = [
        "FORCING%FIELD%WINDS",
        "FORCING%GRID%ASIS",
        "FORCING%GRID%LATLON",
    ]

    # These should be absent since only one field can be True
    unwanted_params = [
        "FORCING%FIELD%CURRENTS",
        "FORCING%FIELD%WATER_LEVELS",
        "FORCING%TIDAL",
    ]

    success = True
    for param in expected_params:
        if param not in rendered:
            print(f"MISSING parameter: {param}")
            success = False
        else:
            print(f"FOUND parameter: {param}")

    for param in unwanted_params:
        if param in rendered:
            print(f"UNEXPECTED parameter (should not be present): {param}")
            success = False
        else:
            print(f"CORRECTLY ABSENT parameter: {param}")

    print()
    if success:
        print(
            "✓ All expected parameters found and unwanted parameters absent in rendered output (dictionary method)"
        )
    else:
        print(
            "✗ Some parameters are missing or unexpected in rendered output (dictionary method)"
        )

    assert success, (
        "Dictionaries should render all expected parameters and avoid invalid ones"
    )


def test_nested_objects_functionality():
    """Test basic functionality of nested objects."""
    forcing_field = ForcingField(winds=True)
    forcing_grid = ForcingGrid(latlon=True)

    forcing = Forcing(field=forcing_field, grid=forcing_grid)

    # Verify that nested objects are accessible
    assert forcing.field is not None
    assert forcing.grid is not None
    assert isinstance(forcing.field, ForcingField)
    assert isinstance(forcing.grid, ForcingGrid)
    assert forcing.field.winds is True
    assert forcing.grid.latlon is True

    print("✓ Nested objects are accessible and functional")


if __name__ == "__main__":
    test_nested_objects_render()
    test_nested_with_dictionaries()
    test_nested_objects_functionality()
    print("\n✓ All nested object tests passed!")
