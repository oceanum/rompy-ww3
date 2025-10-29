"""Tests for WW3 Data assimilation object."""

import pytest
from pathlib import Path
import tempfile

from rompy_ww3.data import DataAssimilation


class TestDataAssimilation:
    """Test WW3 Data Assimilation class functionality."""

    def test_dataassimilation_creation(self):
        """Test basic data assimilation creation with required parameters."""
        data = DataAssimilation(
            model_type="assimilation",
            assimilation_values=[1.0, 2.0, 3.0],
        )

        assert data.model_type == "assimilation"
        assert data.assimilation_values == [1.0, 2.0, 3.0]

    def test_assimilation_flag(self):
        """Test assimilation flag method."""
        data = DataAssimilation(
            model_type="assimilation",
            assimilation_values=[1.0, 2.0, 3.0],
        )

        assert data.assimilation_flag() == "T"

    def test_description_method(self):
        """Test description method."""
        data = DataAssimilation(
            model_type="assimilation",
            assimilation_values=[1.0, 2.0, 3.0],
        )

        description = data.description()
        assert "assimilation" in description
        assert "WW3" in description

    def test_get_method_raises_not_implemented(self):
        """Test that get method raises NotImplementedError."""
        data = DataAssimilation(
            model_type="assimilation",
            assimilation_values=[1.0, 2.0, 3.0],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(NotImplementedError):
                data.get(Path(temp_dir))
