"""Main test runner orchestration."""

from pathlib import Path
from typing import List, Optional
import logging

from .test import TestCase
from .result import TestResult, TestSuiteResult, TestStatus
from .validator import Validator
from ..backends.base import Backend


logger = logging.getLogger(__name__)


class TestRunner:
    """Orchestrates WW3 regression test discovery, execution, and reporting.

    The TestRunner is the main entry point for running regression tests. It:
    - Discovers test cases matching patterns
    - Validates test configurations
    - Executes tests via backend systems
    - Aggregates and reports results

    Example:
        >>> from regtests.runner import TestRunner
        >>> from regtests.runner.backends import DockerBackend
        >>>
        >>> backend = DockerBackend(image="rompy/ww3:latest")
        >>> runner = TestRunner(backend=backend)
        >>>
        >>> tests = runner.discover_tests("regtests/", pattern="ww3_tp1.*")
        >>> results = runner.run_all(tests)
        >>> print(f"Passed: {results.passed}/{results.total_tests}")
    """

    def __init__(
        self,
        backend: Backend,
        output_dir: Optional[Path] = None,
        reference_dir: Optional[Path] = None,
        validator: Optional[Validator] = None,
    ):
        """Initialize test runner with execution backend.

        Args:
            backend: Backend instance for test execution (local/Docker)
            output_dir: Optional directory for test outputs (default: ./test_outputs)
            reference_dir: Optional directory containing reference outputs for validation
            validator: Optional Validator instance (created if not provided)
        """
        self.backend = backend
        self.output_dir = output_dir or Path("./test_outputs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.reference_dir = reference_dir
        self.validator = validator or Validator()

    def discover_tests(self, path: Path, pattern: str = "ww3_tp*") -> List[TestCase]:
        """Discover test cases in directory matching pattern.

        Scans the specified directory for test case directories matching the pattern.
        Each test case directory should contain a YAML configuration file.

        Args:
            path: Root directory to search for tests
            pattern: Glob pattern for test directories (default: "ww3_tp*")

        Returns:
            List of discovered TestCase objects

        Example:
            >>> runner = TestRunner(backend)
            >>> tests = runner.discover_tests("regtests/", pattern="ww3_tp1.*")
            >>> print(f"Found {len(tests)} tests")
        """
        path = Path(path)
        test_cases = []

        logger.info(f"Discovering tests in {path} with pattern {pattern}")

        # Find all directories matching pattern
        for test_dir in sorted(path.glob(pattern)):
            if not test_dir.is_dir():
                continue

            # Look for YAML config file
            config_files = list(test_dir.glob("rompy_ww3_*.yaml"))
            if not config_files:
                logger.warning(f"No config file found in {test_dir}")
                continue

            # Create TestCase for first config found
            test_case = TestCase(config_path=config_files[0])
            test_cases.append(test_case)
            logger.debug(f"Discovered test: {test_case.name}")

        logger.info(f"Discovered {len(test_cases)} tests")
        return test_cases

    def run_test(self, test: TestCase, validate: bool = False) -> TestResult:
        """Execute a single test case and return result.

        Validates the test configuration, executes it via the backend,
        and collects the results. Optionally validates against reference outputs.

        Args:
            test: TestCase to execute
            validate: If True and reference_dir is set, validate outputs

        Returns:
            TestResult with execution outcome

        Example:
            >>> result = runner.run_test(test_case, validate=True)
            >>> if result.status == TestStatus.SUCCESS:
            ...     print(f"Test passed in {result.execution_time:.2f}s")
        """
        logger.info(f"Running test: {test.name}")

        test_output_dir = self.output_dir / test.name
        test_output_dir.mkdir(parents=True, exist_ok=True)

        validation = test.validate()
        if not validation.is_valid:
            logger.error(f"Test validation failed: {validation.message}")
            return TestResult(
                test_name=test.name,
                status=TestStatus.ERROR,
                error_message=f"Validation failed: {validation.message}",
            )

        try:
            result = self.backend.execute(test, workdir=test_output_dir)

            if validate and self.reference_dir and result.status == TestStatus.SUCCESS:
                logger.info(f"Validating outputs for test: {test.name}")
                test_reference_dir = self.reference_dir / test.name

                if test_reference_dir.exists():
                    validation_report = self.validator.validate(
                        output_dir=test_output_dir,
                        reference_dir=test_reference_dir,
                    )
                    result.validation_results = validation_report

                    if not validation_report.is_valid():
                        result.status = TestStatus.FAILURE
                        logger.warning(
                            f"Test {test.name} validation failed: "
                            f"{validation_report.files_matched}/{validation_report.files_compared} files matched"
                        )
                    else:
                        logger.info(f"Test {test.name} validation passed")
                else:
                    logger.warning(f"No reference directory found for {test.name}")

            logger.info(f"Test {test.name} completed: {result.status}")
            return result
        except Exception as e:
            logger.exception(f"Test {test.name} failed with exception")
            return TestResult(
                test_name=test.name,
                status=TestStatus.ERROR,
                error_message=str(e),
            )

    def run_all(self, tests: List[TestCase], validate: bool = False) -> TestSuiteResult:
        """Execute multiple test cases and aggregate results.

        Runs all tests sequentially and aggregates the results into a
        TestSuiteResult for reporting. Optionally validates against references.

        Args:
            tests: List of TestCase objects to execute
            validate: If True and reference_dir is set, validate outputs

        Returns:
            TestSuiteResult with aggregated outcomes

        Example:
            >>> results = runner.run_all(tests, validate=True)
            >>> print(f"Passed: {results.passed}/{results.total_tests}")
            >>> print(f"Failed: {results.failed}")
        """
        logger.info(f"Running {len(tests)} tests")

        results = []
        for test in tests:
            result = self.run_test(test, validate=validate)
            results.append(result)

        suite_result = TestSuiteResult.from_results(results)
        logger.info(f"Test suite completed: {suite_result.summary()}")

        return suite_result

    def validate_test(self, test: TestCase) -> bool:
        """Validate test configuration before execution.

        Args:
            test: TestCase to validate

        Returns:
            True if test is valid, False otherwise
        """
        validation = test.validate()
        if not validation.is_valid:
            logger.error(f"Test {test.name} validation failed: {validation.message}")
            return False
        return True
