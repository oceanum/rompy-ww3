"""Postprocess package for rompy_ww3.

This package provides postprocessor configurations and implementations for
WW3 model output processing.
"""

from .config import WW3TransferConfig
from .processor import WW3TransferPostprocessor

__all__ = [
    "WW3TransferConfig",
    "WW3TransferPostprocessor",
]
