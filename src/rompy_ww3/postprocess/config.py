"""Configuration classes for WW3 postprocessors.

This module provides Pydantic-based configuration classes for WW3-specific
postprocessor types, following the rompy postprocessor configuration framework.
"""

from typing import Any, Dict, List, Literal, Optional

from pydantic import Field, field_validator
from rompy.postprocess.config import BasePostprocessorConfig


class WW3TransferConfig(BasePostprocessorConfig):
    """Configuration for WW3 output transfer postprocessor.

    This configuration handles transferring WW3 model outputs (restart files,
    field outputs, point outputs) to multiple destination prefixes using the
    rompy transfer backend system.

    Features:
    - Multi-destination fan-out: transfer to multiple destinations in one operation
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

    start_date: Optional[str] = Field(
        None,
        description="Optional date string (YYYYMMDD HHMMSS format) used for generating datestamped target names. "
        "If not provided, filenames will not be datestamped.",
    )

    output_stride: Optional[int] = Field(
        None,
        ge=1,
        description="Optional stride in seconds used by compute_target_name to generate "
        "versioned/rotated target names for restart files. "
        "Required for restart file datestamping.",
    )

    @field_validator("destinations")
    @classmethod
    def validate_destinations(cls, v):
        """Validate destinations list is non-empty."""
        if not v:
            raise ValueError("destinations must be a non-empty list")
        return v

    @field_validator("start_date")
    @classmethod
    def validate_start_date(cls, v):
        """Validate start_date format if provided."""
        if v is not None:
            # Basic validation - should be "YYYYMMDD HHMMSS" format
            parts = v.strip().split()
            if len(parts) != 2:
                raise ValueError(
                    f"start_date must be in 'YYYYMMDD HHMMSS' format, got: {v}"
                )
            date_part, time_part = parts
            if len(date_part) != 8 or not date_part.isdigit():
                raise ValueError(
                    f"start_date date part must be 8 digits (YYYYMMDD), got: {date_part}"
                )
            if len(time_part) != 6 or not time_part.isdigit():
                raise ValueError(
                    f"start_date time part must be 6 digits (HHMMSS), got: {time_part}"
                )
        return v

    def get_postprocessor_class(self):
        """Return the WW3TransferPostprocessor class."""
        from .processor import WW3TransferPostprocessor

        return WW3TransferPostprocessor
