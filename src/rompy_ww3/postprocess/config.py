"""Configuration classes for WW3 postprocessors.

This module provides Pydantic-based configuration classes for WW3-specific
postprocessor types, following the rompy postprocessor configuration framework.
"""

from typing import Any, Dict, List, Literal

from pydantic import Field, field_validator
from rompy.postprocess.config import BasePostprocessorConfig


class WW3TransferConfig(BasePostprocessorConfig):
    """Configuration for WW3 output transfer postprocessor.

    This configuration handles transferring WW3 model outputs (restart files,
    field outputs, point outputs) to multiple destination prefixes using the
    rompy transfer backend system.

    The postprocessor automatically extracts timing information (start_date and
    output_stride) from the model configuration, eliminating the need to specify
    these values manually.

    Features:
    - Multi-destination fan-out: transfer to multiple destinations in one operation
    - Auto-extracted timing: reads start_date and output_stride from model config
    - Datestamped filenames: automatic YYYYMMDD_HHMMSS_filename format
    - Special restart handling: uses valid-date computation for restart files
    - Failure policies: continue on error or fail-fast
    - Backend-agnostic: works with any rompy.transfer backend (file://, s3://, gs://, etc.)
    """

    type: Literal["ww3_transfer"] = "ww3_transfer"

    destinations: List[str] = Field(
        ...,
        min_length=1,
        description="List of destination URIs where outputs will be transferred. "
        "Supports any rompy.transfer backend (file://, s3://, gs://, az://, etc.)",
    )

    output_types: Dict[str, Any] = Field(
        default_factory=dict,
        description="Manifest filter describing which WW3 output types to include. "
        "Accepted by generate_manifest. Example: {'restart': {'extra': 'DW'}, 'field': {'list': [1, 2, 3]}}",
    )

    failure_policy: Literal["CONTINUE", "FAIL_FAST"] = Field(
        "CONTINUE",
        description="How to react to transfer failures. "
        "CONTINUE: log errors but keep transferring. "
        "FAIL_FAST: stop on first error.",
    )

    @field_validator("destinations")
    @classmethod
    def validate_destinations(cls, v):
        """Validate destinations list is non-empty."""
        if not v:
            raise ValueError("destinations must be a non-empty list")
        return v

    def get_postprocessor_class(self):
        """Return the WW3TransferPostprocessor class."""
        from .processor import WW3TransferPostprocessor

        return WW3TransferPostprocessor
