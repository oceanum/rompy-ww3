"""Test execution result representation."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .namelist_comparator import NamelistComparisonReport


class TestStatus(Enum):
    """Status of a test execution."""

    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class TestResult:
    """Result of a single test execution.

    Encapsulates all information about a test run including:
    - Status (success/failure/error/skipped)
    - Execution time
    - Generated outputs
    - Validation results (if applicable)
    - Error messages
    - Execution logs

    Example:
        >>> result = TestResult(
        ...     test_name="tp1.1",
        ...     status=TestStatus.SUCCESS,
        ...     execution_time=45.3,
        ... )
        >>> print(f"Test {result.test_name}: {result.status.value}")
    """

    test_name: str
    status: TestStatus
    execution_time: float = 0.0
    outputs_generated: List[Path] = field(default_factory=list)
    validation_results: Optional["ValidationReport"] = None
    namelist_report: Optional["NamelistComparisonReport"] = None
    error_message: Optional[str] = None
    logs: str = ""

    def is_success(self) -> bool:
        """Check if test passed successfully."""
        return self.status == TestStatus.SUCCESS

    def is_failure(self) -> bool:
        """Check if test failed validation."""
        return self.status == TestStatus.FAILURE

    def is_error(self) -> bool:
        """Check if test had execution error."""
        return self.status == TestStatus.ERROR

    def is_skipped(self) -> bool:
        """Check if test was skipped."""
        return self.status == TestStatus.SKIPPED


@dataclass
class TestSuiteResult:
    """Aggregated results for multiple test executions.

    Provides summary statistics and individual results for a test suite run.

    Attributes:
        total_tests: Total number of tests executed
        passed: Number of tests that passed
        failed: Number of tests that failed validation
        errors: Number of tests that had execution errors
        skipped: Number of tests that were skipped
        total_time: Total execution time in seconds
        results: List of individual TestResult objects

    Example:
        >>> suite = TestSuiteResult.from_results(results)
        >>> print(f"Passed: {suite.passed}/{suite.total_tests}")
        >>> print(f"Total time: {suite.total_time:.2f}s")
    """

    total_tests: int
    passed: int
    failed: int
    errors: int
    skipped: int
    total_time: float
    results: List[TestResult]

    @classmethod
    def from_results(cls, results: List[TestResult]) -> "TestSuiteResult":
        """Create TestSuiteResult from list of individual results.

        Args:
            results: List of TestResult objects

        Returns:
            Aggregated TestSuiteResult
        """
        total = len(results)
        passed = sum(1 for r in results if r.status == TestStatus.SUCCESS)
        failed = sum(1 for r in results if r.status == TestStatus.FAILURE)
        errors = sum(1 for r in results if r.status == TestStatus.ERROR)
        skipped = sum(1 for r in results if r.status == TestStatus.SKIPPED)
        total_time = sum(r.execution_time for r in results)

        return cls(
            total_tests=total,
            passed=passed,
            failed=failed,
            errors=errors,
            skipped=skipped,
            total_time=total_time,
            results=results,
        )

    def summary(self) -> str:
        """Generate human-readable summary string.

        Returns:
            Summary string with statistics
        """
        return (
            f"{self.passed}/{self.total_tests} passed, "
            f"{self.failed} failed, "
            f"{self.errors} errors, "
            f"{self.skipped} skipped "
            f"({self.total_time:.2f}s)"
        )

    def is_success(self) -> bool:
        """Check if all tests passed."""
        return self.failed == 0 and self.errors == 0


@dataclass
class ValidationReport:
    """Report from output validation against reference data.

    Contains detailed information about comparison between test outputs
    and reference outputs.

    Attributes:
        files_compared: Number of files compared
        files_matched: Number of files that matched within tolerance
        differences: List of differences found
        tolerance_used: Tolerance level used for comparison
    """

    files_compared: int
    files_matched: int
    differences: List[str] = field(default_factory=list)
    tolerance_used: float = 1e-6

    def is_valid(self) -> bool:
        """Check if validation passed (all files matched)."""
        return self.files_compared == self.files_matched
