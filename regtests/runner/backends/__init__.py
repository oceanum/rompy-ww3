"""Backend execution systems.

This module provides backend implementations for executing WW3 regression tests
in different environments.

Available backends:
- LocalBackend: Execute using local WW3 installation
- DockerBackend: Execute in Docker container
"""

from .base import Backend
from .local import LocalBackend
from .docker import DockerBackend

__all__ = ["Backend", "LocalBackend", "DockerBackend"]
