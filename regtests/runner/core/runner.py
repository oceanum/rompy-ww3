"""Main test runner orchestration."""

import re
from pathlib import Path
from typing import List, Optional
import logging

from typing import TYPE_CHECKING

from .test import TestCase
from .result import TestResult, TestSuiteResult, TestStatus
from .validator import Validator
from .namelist_comparator import NamelistComparator
from ..backends.base import Backend

if TYPE_CHECKING:
    from .namelist_comparator import NamelistComparisonReport


logger = logging.getLogger(__name__)


def _parse_grdset_from_pattern(pattern: str) -> tuple[str, Optional[str]]:
    """Parse test pattern to extract base name and optional grdset.

    Args:
        pattern: Test pattern (e.g., 'mww3_test_02' or 'mww3_test_02_grdset_a')

    Returns:
        Tuple of (base_pattern, grdset_suffix or None)
    """
    grdset_match = re.match(r"(.+)_(grdset_[a-z0-9]+)$", pattern)
    if grdset_match:
        return grdset_match.group(1), grdset_match.group(2)
    return pattern, None


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
        namelist_comparator: Optional[NamelistComparator] = None,
    ):
        """Initialize test runner with execution backend.

        Args:
            backend: Backend instance for test execution (local/Docker)
            output_dir: Optional directory for test outputs (default: ./test_outputs)
            reference_dir: Optional directory containing reference outputs for validation
            validator: Optional Validator instance (created if not provided)
            namelist_comparator: Optional NamelistComparator for validating namelists
        """
        self.backend = backend
        self.output_dir = output_dir or Path("./test_outputs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.reference_dir = reference_dir
        self.validator = validator or Validator()
        self.namelist_comparator = namelist_comparator

    def discover_tests(self, path: Path, pattern: str = "ww3_tp*") -> List[TestCase]:
        """Discover test cases in directory matching pattern.

        Scans the specified directory for test case directories matching the pattern.
        Each test case directory should contain a YAML configuration file.
        Supports grdset variants (e.g., mww3_test_02_grdset_a).

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

        # Check if pattern includes grdset suffix
        base_pattern, grdset = _parse_grdset_from_pattern(pattern)

        if grdset:
            # Look for specific grdset config in base directory
            test_dir = path / base_pattern
            if test_dir.is_dir():
                # Look for specific grdset config file
                config_file = test_dir / f"rompy_ww3_{pattern}.yaml"
                if config_file.exists():
                    test_case = TestCase(config_path=config_file)
                    test_cases.append(test_case)
                    logger.debug(f"Discovered grdset test: {test_case.name}")
                else:
                    logger.warning(f"Grdset config not found: {config_file}")
            else:
                logger.warning(f"Base test directory not found: {test_dir}")
        else:
            # Standard discovery - find all directories matching pattern
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

    def run_test(
        self,
        test: TestCase,
        validate: bool = False,
        validate_namelists: bool = False,
        skip_model_execution: bool = False,
    ) -> TestResult:
        """Execute a single test case and return result.

        Validates the test configuration, executes it via the backend,
        and collects the results. Optionally validates against reference outputs
        and/or reference namelists.

        Args:
            test: TestCase to execute
            validate: If True and reference_dir is set, validate outputs
            validate_namelists: If True, validate generated namelists against NOAA references
            skip_model_execution: If True, skip WW3 execution (only generate/validate namelists)

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
            if skip_model_execution and not validate_namelists:
                logger.info(f"Skipping model execution for test: {test.name}")
                result = TestResult(
                    test_name=test.name,
                    status=TestStatus.SUCCESS,
                    error_message="Model execution skipped (--skip-model-execution)",
                )
            else:
                result = self.backend.execute(test, workdir=test_output_dir)

            if validate_namelists:
                logger.info(f"Validating namelists for test: {test.name}")
                namelist_report = self.validate_test_namelists(test)

                if not namelist_report.is_valid():
                    result.status = TestStatus.FAILURE
                    mismatches = namelist_report.get_mismatches()
                    result.error_message = (
                        f"Namelist validation failed: {len(mismatches)}/{namelist_report.namelists_compared} "
                        f"namelists differ from NOAA references"
                    )
                    logger.warning(
                        f"Test {test.name} namelist validation failed: "
                        f"{namelist_report.namelists_matched}/{namelist_report.namelists_compared} matched"
                    )
                    result.namelist_report = namelist_report
                else:
                    logger.info(
                        f"Test {test.name} namelist validation passed: "
                        f"{namelist_report.namelists_matched}/{namelist_report.namelists_compared} matched"
                    )

            # Validate outputs if requested
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
                            f"Test {test.name} output validation failed: "
                            f"{validation_report.files_matched}/{validation_report.files_compared} files matched"
                        )
                    else:
                        logger.info(f"Test {test.name} output validation passed")
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

    def run_all(
        self,
        tests: List[TestCase],
        validate: bool = False,
        validate_namelists: bool = False,
        skip_model_execution: bool = False,
    ) -> TestSuiteResult:
        """Execute multiple test cases and aggregate results.

        Runs all tests sequentially and aggregates the results into a
        TestSuiteResult for reporting. Optionally validates against references
        and/or namelists.

        Args:
            tests: List of TestCase objects to execute
            validate: If True and reference_dir is set, validate outputs
            validate_namelists: If True, validate generated namelists against NOAA references
            skip_model_execution: If True, skip WW3 execution (only generate/validate namelists)

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
            result = self.run_test(
                test,
                validate=validate,
                validate_namelists=validate_namelists,
                skip_model_execution=skip_model_execution,
            )
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

    def validate_test_namelists(self, test: TestCase) -> "NamelistComparisonReport":
        """Validate generated namelists against NOAA references.

        Args:
            test: TestCase to validate

        Returns:
            NamelistComparisonReport with comparison results
        """
        if self.namelist_comparator is None:
            self.namelist_comparator = NamelistComparator()

        test_name_normalized = test.name.replace(".", "_")
        test_dir = test.config_path.parent
        regtests_dir = test_dir.parent  # Parent of test directory (regtests/)

        # Possible locations for generated namelists
        rompy_run_dir = (
            test_dir / "rompy_runs" / f"ww3_{test_name_normalized}_regression"
        )
        regtests_run_dir = (
            regtests_dir / "rompy_runs" / f"ww3_{test_name_normalized}_regression"
        )
        fallback_dir = (
            self.output_dir
            / test.name
            / "rompy_runs"
            / f"ww3_{test_name_normalized}_regression"
        )
        output_root = self.output_dir / test.name

        possible_dirs = [rompy_run_dir, regtests_run_dir, fallback_dir, output_root]

        test_output_dir = None
        for d in possible_dirs:
            if d.exists() and any(d.glob("*.nml")):
                test_output_dir = d
                break

        if test_output_dir is None:
            test_output_dir = possible_dirs[0]  # Default to first option

        return self.namelist_comparator.compare_test_namelists(
            test_name=test.name,
            generated_dir=test_output_dir,
            download_missing=True,
        )
