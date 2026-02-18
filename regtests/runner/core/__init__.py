"""Core test runner components.

This module contains the core classes for test execution:

- TestRunner: Main orchestrator
- TestCase: Test encapsulation
- TestResult: Result representation
- Validator: Output validation logic
- ReportGenerator: Test result reporting
"""

from .runner import TestRunner
from .test import TestCase, ValidationResult
from .result import TestResult, TestSuiteResult, TestStatus
from .validator import Validator
from .report import ReportGenerator
from .namelist_comparator import (
    NamelistComparator,
    NamelistComparisonReport,
    NamelistDiff,
    NamelistMismatchError,
)

__all__ = [
    "TestRunner",
    "TestCase",
    "TestResult",
    "TestSuiteResult",
    "TestStatus",
    "Validator",
    "ValidationResult",
    "ReportGenerator",
    "NamelistComparator",
    "NamelistComparisonReport",
    "NamelistDiff",
    "NamelistMismatchError",
]
