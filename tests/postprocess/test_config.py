"""Tests for WW3TransferConfig validation."""

import pytest
from pydantic import ValidationError

from rompy_ww3.postprocess.config import WW3TransferConfig
from rompy_ww3.postprocess.processor import WW3TransferPostprocessor


def test_config_valid_minimal():
    """Test config validates with minimal required fields."""
    config = WW3TransferConfig(
        destinations=["file:///tmp/dest"],
        output_types={"restart": {"extra": "DW"}},
    )
    assert config.type == "ww3_transfer"
    assert config.destinations == ["file:///tmp/dest"]
    assert config.output_types == {"restart": {"extra": "DW"}}
    assert config.failure_policy == "CONTINUE"


def test_config_valid_full():
    """Test config validates with all fields specified."""
    config = WW3TransferConfig(
        destinations=["s3://bucket/prefix", "gs://bucket/prefix"],
        output_types={"restart": {"extra": "DW"}, "field": {"list": [1, 2, 3]}},
        failure_policy="FAIL_FAST",
        timeout=7200,
        env_vars={"AWS_PROFILE": "default"},
    )
    assert config.destinations == ["s3://bucket/prefix", "gs://bucket/prefix"]
    assert config.failure_policy == "FAIL_FAST"
    assert config.timeout == 7200


def test_config_empty_destinations():
    """Test config validation fails with empty destinations list."""
    with pytest.raises(ValidationError, match="at least 1 item"):
        WW3TransferConfig(
            destinations=[],
            output_types={},
        )


def test_config_invalid_failure_policy():
    """Test config validation fails with invalid failure policy."""
    with pytest.raises(ValidationError):
        WW3TransferConfig(
            destinations=["file:///tmp/dest"],
            output_types={},
            failure_policy="INVALID_POLICY",
        )


def test_config_get_postprocessor_class():
    """Test config returns correct postprocessor class."""
    config = WW3TransferConfig(
        destinations=["file:///tmp/dest"],
        output_types={},
    )
    processor_class = config.get_postprocessor_class()
    assert processor_class == WW3TransferPostprocessor


def test_config_instantiate_postprocessor():
    """Test config can instantiate postprocessor."""
    config = WW3TransferConfig(
        destinations=["file:///tmp/dest"],
        output_types={"restart": {"extra": "DW"}},
    )
    processor_class = config.get_postprocessor_class()
    processor = processor_class()
    assert isinstance(processor, WW3TransferPostprocessor)


def test_config_base_fields():
    """Test config inherits base postprocessor fields."""
    config = WW3TransferConfig(
        destinations=["file:///tmp/dest"],
        output_types={},
        timeout=1800,
        env_vars={"DEBUG": "1"},
    )
    assert config.timeout == 1800
    assert config.env_vars == {"DEBUG": "1"}
    assert config.working_dir is None


def test_config_multiple_destinations():
    """Test config accepts multiple destinations."""
    config = WW3TransferConfig(
        destinations=[
            "file:///local/backup",
            "s3://my-bucket/outputs",
            "gs://another-bucket/data",
        ],
        output_types={"restart": {"extra": "DW"}},
    )
    assert len(config.destinations) == 3
    assert "file:///local/backup" in config.destinations
    assert "s3://my-bucket/outputs" in config.destinations
    assert "gs://another-bucket/data" in config.destinations
