"""Core test runner components.

This module contains the core classes for test execution:

- TestRunner: Main orchestrator
- TestCase: Test encapsulation
- TestResult: Result representation
- Validator: Output validation logic
"""

from .runner import TestRunner
from .test import TestCase, ValidationResult
from .result import TestResult, TestSuiteResult, TestStatus
from .validator import Validator

__all__ = [
    "TestRunner",
    "TestCase",
    "TestResult",
    "TestSuiteResult",
    "TestStatus",
    "Validator",
    "ValidationResult",
]
