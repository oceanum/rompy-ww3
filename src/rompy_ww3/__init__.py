"""Top-level package for rompy-ww3."""

__author__ = """Rompy Developers"""
__email__ = "developers@rompy.com"
__version__ = "0.1.0"

# Delay import to avoid circular dependency during package initialization
from .config import NMLConfig


Config = NMLConfig  # Create an alias for backward compatibility
__all__ = ["NMLConfig", "Config"]
