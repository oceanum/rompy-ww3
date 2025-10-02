"""
Test cases for WW3 Grid class.
"""

import tempfile
from pathlib import Path
from rompy_ww3.grid import Grid


def test_grid_with_ww3_parameters():
    """Test Grid class with WW3-specific parameters."""

    # Create a grid with WW3-specific parameters
    # Using parameters compatible with RegularGrid
    grid = Grid(x0=-10.0, y0=20.0, dx=0.1, dy=0.1, nx=100, ny=50)

    # Set WW3-specific attributes
    grid.name = "Test Gulf"
    grid.grid_type = "RECT"
    grid.coordinate_system = "SPHE"

    # Test generating namelists
    grid_nml = grid.generate_grid_nml()
    rect_nml = grid.generate_rect_nml()

    print("GRID_NML content:")
    print(grid_nml)

    print("\nRECT_NML content:")
    print(rect_nml)

    assert "&GRID_NML" in grid_nml
    assert "GRID%NAME" in grid_nml
    assert "GRID%TYPE" in grid_nml
    assert "&RECT_NML" in rect_nml
    assert "RECT%NX" in rect_nml
    assert "RECT%NY" in rect_nml

    # Test writing files
    with tempfile.TemporaryDirectory() as tmpdir:
        grid_dir = Path(tmpdir) / "grid"
        grid.write_grid_files(grid_dir)

        grid_file = grid_dir / "grid.nml"
        rect_file = grid_dir / "rect.nml"

        assert grid_file.exists()
        assert rect_file.exists()

        print(f"\nCreated grid files in {grid_dir}")


if __name__ == "__main__":
    test_grid_with_ww3_parameters()
    print("\nGrid test passed!")
