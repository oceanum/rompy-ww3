"""WW3 Regression Test Runner.

This package provides infrastructure for automated execution, validation,
and reporting of WW3 regression tests.

The test runner architecture consists of:

- **TestRunner**: Orchestrates test discovery, execution, and reporting
- **TestCase**: Encapsulates individual test configuration and metadata
- **Backend**: Abstract interface for execution environments (local/Docker)
- **TestResult**: Encapsulates execution results and validation outcomes

Usage:
    from regtests.runner import TestRunner
    from regtests.runner.backends import DockerBackend

    backend = DockerBackend(image="rompy/ww3:latest")
    runner = TestRunner(backend=backend)

    tests = runner.discover_tests("regtests/", pattern="ww3_tp1.*")
    results = runner.run_all(tests)
"""

from .core.runner import TestRunner
from .core.test import TestCase
from .core.result import TestResult, TestSuiteResult, TestStatus
from .backends.base import Backend

__all__ = [
    "TestRunner",
    "TestCase",
    "TestResult",
    "TestSuiteResult",
    "TestStatus",
    "Backend",
]
