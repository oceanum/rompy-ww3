"""Tests for WW3 boundary update component (bounc)."""

import pytest
from rompy_ww3.components.bounc import Bounc
from rompy_ww3.namelists.bound import Bound


def test_bound_nml():
    """Test BOUND_NML namelist creation."""
    bound = Bound(mode="WRITE", interp=2, verbose=1, file="spec.list")
    content = bound.render()
    assert "&BOUND_NML" in content
    assert "BOUND%MODE = 'WRITE'" in content
    assert "BOUND%INTERP = 2" in content
    assert "BOUND%VERBOSE = 1" in content
    assert "BOUND%FILE = 'spec.list'" in content
    assert "/" in content


def test_bounc_component():
    """Test Bounc component with boundary configuration."""
    bounc = Bounc(bound_nml=Bound(mode="READ", file="my_spec.list"))

    assert bounc.bound_nml is not None
    assert bounc.bound_nml.mode == "READ"
    assert bounc.bound_nml.file == "my_spec.list"


def test_bounc_render():
    """Test that Bounc component can render the namelist."""
    bounc = Bounc(bound_nml=Bound(mode="WRITE", interp=2, verbose=1, file="spec.list"))

    content = bounc.bound_nml.render()
    assert "&BOUND_NML" in content
    assert "BOUND%MODE = 'WRITE'" in content
    assert "/" in content


if __name__ == "__main__":
    pytest.main([__file__])
