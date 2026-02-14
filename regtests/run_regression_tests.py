#!/usr/bin/env python
"""
WW3 Regression Test Runner CLI

Command-line interface for running WW3 regression tests with various options.
"""

import sys
import logging
import argparse
from pathlib import Path

# Add regtests to path to allow imports
sys.path.insert(0, str(Path(__file__).parent))

from runner import TestRunner
from runner.backends import LocalBackend, DockerBackend
from runner.core.result import TestStatus


def setup_logging(verbose: bool = False):
    """Configure logging for test runner.

    Args:
        verbose: Enable debug-level logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run WW3 regression tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python run_regression_tests.py --all

  # Run specific test series
  python run_regression_tests.py --series tp1.x

  # Run specific test
  python run_regression_tests.py --test tp2.4

  # Use Docker backend
  python run_regression_tests.py --all --backend docker

  # Enable verbose logging
  python run_regression_tests.py --test tp2.4 --verbose

  # Check what inputs would be downloaded (dry run)
  python run_regression_tests.py --test tp2.4 --dry-run

  # Run without downloading inputs (use existing files only)
  python run_regression_tests.py --test tp2.4 --no-download-inputs
        """,
    )

    # Test selection
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument(
        "--all",
        action="store_true",
        help="Run all discovered tests",
    )
    selection.add_argument(
        "--series",
        metavar="SERIES",
        help="Run all tests in series (e.g., tp1.x, tp2.x)",
    )
    selection.add_argument(
        "--test",
        metavar="TEST",
        help="Run specific test (e.g., tp1.1, tp2.4)",
    )

    # Backend selection
    parser.add_argument(
        "--backend",
        choices=["local", "docker"],
        default="local",
        help="Execution backend (default: local)",
    )
    parser.add_argument(
        "--docker-image",
        default="rompy/ww3:latest",
        help="Docker image for docker backend (default: rompy/ww3:latest)",
    )

    # Output options
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./test_outputs"),
        help="Output directory for test results (default: ./test_outputs)",
    )

    # Input handling
    parser.add_argument(
        "--download-inputs",
        action="store_true",
        default=True,
        help="Automatically download missing input files (default: True)",
    )
    parser.add_argument(
        "--no-download-inputs",
        action="store_false",
        dest="download_inputs",
        help="Skip downloading input files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be downloaded without downloading",
    )

    # Logging
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    # Test discovery path
    parser.add_argument(
        "--regtests-dir",
        type=Path,
        default=Path(__file__).parent,
        help="Path to regtests directory (default: script directory)",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(verbose=args.verbose)
    logger = logging.getLogger(__name__)

    # Initialize backend
    logger.info(f"Initializing {args.backend} backend")
    if args.backend == "docker":
        backend = DockerBackend(image=args.docker_image)
    else:
        backend = LocalBackend()

    # Validate backend environment
    if not backend.validate_env():
        logger.error("Backend validation failed - check environment setup")
        return 1

    # Display backend version info
    version_info = backend.get_version_info()
    if version_info:
        logger.info(f"Backend versions: {version_info}")

    # Initialize test runner
    runner = TestRunner(backend=backend, output_dir=args.output_dir)

    # Discover tests based on selection
    if args.all:
        pattern = "ww3_tp*"
        logger.info("Discovering all tests")
    elif args.series:
        # Convert tp1.x -> ww3_tp1.*
        series = args.series.replace(".x", ".*")
        pattern = f"ww3_{series}"
        logger.info(f"Discovering tests in series {args.series}")
    else:  # args.test
        # Convert tp1.1 -> ww3_tp1.1
        pattern = f"ww3_{args.test}"
        logger.info(f"Discovering test {args.test}")

    tests = runner.discover_tests(args.regtests_dir, pattern=pattern)

    if not tests:
        logger.error(f"No tests found matching pattern: {pattern}")
        return 1

    logger.info(f"Found {len(tests)} test(s)")

    # Handle dry-run for input downloading
    if args.dry_run:
        from runner import InputFileManager

        input_manager = InputFileManager()
        print("\n" + "=" * 70)
        print("DRY RUN - Input Files to Download")
        print("=" * 70)
        for test in tests:
            missing = input_manager.get_missing_inputs(test)
            if missing:
                print(f"\n{test.name}:")
                for path in missing:
                    print(f"  - {path.name}")
        print("=" * 70)
        return 0

    # Run tests
    if len(tests) == 1:
        # Run single test
        result = runner.run_test(tests[0], download_inputs=args.download_inputs)

        # Print result
        print("\n" + "=" * 70)
        print(f"Test: {result.test_name}")
        print(f"Status: {result.status.value}")
        if result.execution_time:
            print(f"Execution time: {result.execution_time:.2f}s")
        if result.error_message:
            print(f"Error: {result.error_message}")
        print("=" * 70)

        return 0 if result.status == TestStatus.SUCCESS else 1
    else:
        # Run multiple tests
        suite_result = runner.run_all(tests, download_inputs=args.download_inputs)

        # Print summary
        print("\n" + "=" * 70)
        print("TEST SUITE SUMMARY")
        print("=" * 70)
        print(suite_result.summary())
        print("=" * 70)
        print(f"\nIndividual Results:")
        for result in suite_result.results:
            status_symbol = "✓" if result.status == TestStatus.SUCCESS else "✗"
            print(f"  {status_symbol} {result.test_name}: {result.status.value}")
            if result.error_message:
                print(f"    Error: {result.error_message}")
        print("=" * 70)

        return 0 if suite_result.is_success() else 1


if __name__ == "__main__":
    sys.exit(main())
