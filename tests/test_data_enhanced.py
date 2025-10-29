"""Tests for the enhanced Data assimilation class."""

import pytest
import tempfile
from pathlib import Path

from rompy_ww3.data import DataAssimilation


def test_dataassimilation_creation():
    """Test data assimilation creation."""
    data = DataAssimilation(
        model_type="assimilation",
        assimilation_values=[1.0, 2.0, 3.0],
    )

    # This should not raise an exception
    assert data.model_type == "assimilation"
    assert data.assimilation_values == [1.0, 2.0, 3.0]


def test_dataassimilation_assimilation_flag():
    """Test assimilation flag method."""
    data = DataAssimilation(
        model_type="assimilation",
        assimilation_values=[1.0, 2.0, 3.0],
    )

    flag = data.assimilation_flag()
    assert flag == "T"


def test_dataassimilation_description():
    """Test description method."""
    data = DataAssimilation(
        model_type="assimilation",
        assimilation_values=[1.0, 2.0, 3.0],
    )

    description = data.description()
    assert "assimilation" in description
    assert "WW3" in description


def test_dataassimilation_get_method():
    """Test get method raises NotImplementedError."""
    data = DataAssimilation(
        model_type="assimilation",
        assimilation_values=[1.0, 2.0, 3.0],
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(NotImplementedError):
            data.get(Path(tmpdir))


def test_dataassimilation_with_none_values():
    """Test data assimilation with None values."""
    data = DataAssimilation(
        model_type="assimilation",
        assimilation_values=None,
    )

    assert data.model_type == "assimilation"
    assert data.assimilation_values is None


if __name__ == "__main__":
    test_dataassimilation_creation()
    test_dataassimilation_assimilation_flag()
    test_dataassimilation_description()
    test_dataassimilation_with_none_values()
    print("All data assimilation tests passed!")
