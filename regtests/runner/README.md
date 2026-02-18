# WW3 Regression Test Runner

This package provides infrastructure for automated execution, validation, and reporting of WW3 regression tests. The test runner enables you to discover test cases, execute them against WW3 models, validate outputs against reference data, and generate comprehensive reports in multiple formats.

## Overview

The test runner architecture consists of several core components that work together to provide a complete regression testing solution. The **TestRunner** class orchestrates the entire process, from discovering test cases to generating final reports. **Backend** implementations provide abstraction for executing tests in different environments, whether locally or within Docker containers. The **TestCase** class encapsulates individual test configuration and metadata, while **TestResult** and **TestSuiteResult** classes track execution outcomes and validation results. The **Validator** component compares test outputs against reference data to ensure numerical accuracy, and the **ReportGenerator** creates human-readable and machine-parseable reports in text, JSON, and HTML formats.

## Quick Start

For those eager to get started immediately, the following example demonstrates the basic workflow of discovering tests, executing them, and generating a report. This example assumes you have rompy-ww3 installed and a local WW3 installation available.

```python
from pathlib import Path
from regtests.runner import TestRunner
from regtests.runner.backends import LocalBackend
from regtests.runner.core.report import ReportGenerator

# Initialize the backend (LocalBackend uses rompy CLI)
backend = LocalBackend(ww3_dir=Path("/path/to/ww3"))

# Create the test runner with reference outputs for validation
runner = TestRunner(
    backend=backend,
    output_dir=Path("test_outputs"),
    reference_dir=Path("reference_outputs"),
)

# Discover all tests in the regtests directory
tests = runner.discover_tests(Path("regtests/"), pattern="ww3_tp*")
print(f"Discovered {len(tests)} tests")

# Execute all tests with validation against reference outputs
results = runner.run_all(tests, validate=True)

# Generate and print a text report
generator = ReportGenerator()
text_report = generator.generate_text_report(results)
print(text_report)

# Save reports in multiple formats
generator.save_report(text_report, Path("test_report.txt"))
generator.save_json_report(generator.generate_json_report(results), Path("test_report.json"))
generator.save_report(generator.generate_html_report(results), Path("test_report.html"))
```

For users who prefer command-line interaction, the test runner can be invoked as a Python module. The following command runs a specific test case and generates an HTML report for easy visualization in a web browser.

```bash
python -m regtests.runner --test ww3_tp2.4 --output test_outputs --report html
```

## Installation and Setup

Before using the test runner, ensure that rompy-ww3 is properly installed and that you have access to either a local WW3 installation or Docker. The test runner requires Python 3.9 or later and depends on the rompy-ww3 package for configuration parsing and model execution.

### Prerequisites

The test runner requires several components to be available in your environment. First, you need rompy-ww3 installed with the test dependencies, which can be achieved by running `pip install -e ".[test]"` in the package directory. For local execution, ensure that the `rompy` command is available in your PATH and that WW3 binaries are properly installed. For Docker-based execution, you need Docker installed and running, along with the `rompy/ww3:latest` image or a custom WW3 Docker image. Reference outputs should be downloaded and organized in a directory structure matching the test case names for validation to work correctly.

### Directory Structure

The test runner expects a specific directory structure to function properly. The root directory containing test cases should have subdirectories for each test, named with the pattern `ww3_tp*` for regression tests. Each test directory must contain a YAML configuration file matching the pattern `rompy_ww3_*.yaml`. Reference outputs should be organized in a separate directory with the same structure as test outputs, where each test's reference outputs reside in a subdirectory matching the test name.

```
regtests/
├── ww3_tp1.1/
│   ├── rompy_ww3_tp1_1.yaml
│   └── input/
├── ww3_tp2.4/
│   ├── rompy_ww3_tp2_4.yaml
│   └── input/
└── ...
reference_outputs/
├── ww3_tp1.1/
│   └── (reference NetCDF/binary files)
├── ww3_tp2.4/
│   └── (reference NetCDF/binary files)
└── ...
test_outputs/
├── ww3_tp1.1/
│   └── (generated output files)
├── ww3_tp2.4/
│   └── (generated output files)
└── ...
```

## CLI Usage

The test runner provides a command-line interface for running tests without writing Python code. This interface is invoked using the Python module execution pattern and supports various options for controlling test discovery, execution, validation, and reporting.

### Basic Commands

The most common use case is running a single test case by specifying its name. The runner will discover the test configuration, execute it, and report the results. When you run a test, the output shows real-time progress including the test name, execution status, and timing information.

```bash
# Run a specific test
python -m regtests.runner --test ww3_tp2.4

# Run with validation against reference outputs
python -m regtests.runner --test ww3_tp2.4 --validate

# Run with custom output directory
python -m regtests.runner --test ww3_tp2.4 --output /path/to/outputs
```

### Test Discovery Patterns

Rather than running individual tests, you can discover and run multiple tests using glob-style patterns. This is particularly useful when you want to run an entire test series or validate all tests of a particular type. The pattern matching follows Python's pathlib glob conventions, allowing for flexible test selection.

```bash
# Run all tp1.x tests
python -m regtests.runner --pattern "ww3_tp1.*"

# Run all tests
python -m regtests.runner --all

# Run tests in a specific directory
python -m regtests.runner --path /path/to/regtests --pattern "ww3_tp2.*"
```

### Report Generation

The test runner supports generating reports in multiple formats. By default, results are printed to the console, but you can also save reports to files for later analysis or sharing with team members. The HTML format provides an interactive report with visual status indicators and formatted error messages, while the JSON format is ideal for programmatic processing and integration with CI/CD systems.

```bash
# Generate HTML report
python -m regtests.runner --test ww3_tp2.4 --report html --output report.html

# Generate JSON report for CI integration
python -m regtests.runner --all --report json --output results.json

# Generate text report
python -m regtests.runner --all --report text --output report.txt
```

### Backend Selection

The test runner supports different execution backends depending on your environment. The local backend uses the rompy CLI directly on your host system, while the Docker backend runs tests inside containers for isolation and reproducibility. You can specify which backend to use and configure backend-specific options.

```bash
# Use local backend (default)
python -m regtests.runner --test ww3_tp2.4 --backend local

# Use Docker backend
python -m regtests.runner --test ww3_tp2.4 --backend docker --image rompy/ww3:latest

# Specify WW3 directory for local backend
python -m regtests.runner --test ww3_tp2.4 --backend local --ww3-dir /path/to/ww3
```

### Input File Management

Many WW3 regression tests require external input files such as depth data, boundary conditions, and point lists. These files are stored in the NOAA-EMC/WW3 repository and are automatically downloaded by the test runner when needed.

The test runner will automatically detect required input files from test configurations and download them from the NOAA WW3 repository before executing tests. This eliminates the need to manually manage input files or commit them to your repository.

```bash
# Run test with automatic input downloading (default)
python -m regtests.runner --test ww3_tp2.4

# Check what inputs would be downloaded without downloading
python -m regtests.runner --test ww3_tp2.4 --dry-run

# Run without downloading inputs (use only existing files)
python -m regtests.runner --test ww3_tp2.4 --no-download-inputs

# Download inputs for all tests in a series
python -m regtests.runner --series tp2.x --dry-run
```

Input files are downloaded from `https://raw.githubusercontent.com/NOAA-EMC/WW3/develop/regtests` and cached locally in the test directories. Once downloaded, files are reused for subsequent test runs.

### Complete CLI Options

The following table summarizes all available command-line options with their descriptions and default values. These options provide fine-grained control over every aspect of test execution and reporting.

| Option | Description | Default |
|--------|-------------|---------|
| `--test` | Run a specific test by name | None |
| `--pattern` | Glob pattern for test discovery | "ww3_tp*" |
| `--path` | Root directory for test discovery | "regtests/" |
| `--all` | Run all discovered tests | False |
| `--output` | Directory for test outputs | "./test_outputs" |
| `--reference` | Directory containing reference outputs | None |
| `--validate` | Validate outputs against references | False |
| `--backend` | Execution backend (local or docker) | "local" |
| `--image` | Docker image for backend | "rompy/ww3:latest" |
| `--ww3-dir` | Path to local WW3 installation | None |
| `--report` | Report format (text, json, html) | "text" |
| `--output-file` | File path for report output | None |
| `--download-inputs` | Automatically download missing input files | True |
| `--no-download-inputs` | Skip downloading input files | False |
| `--dry-run` | Show what would be downloaded without downloading | False |
| `--verbose` | Enable verbose logging | False |
| `--quiet` | Suppress non-essential output | False |

## Python API

For more complex testing scenarios or integration with other tools, the test runner provides a comprehensive Python API. This API gives you full programmatic control over test discovery, execution, validation, and reporting.

### TestRunner Class

The TestRunner class is the main entry point for the test runner functionality. It coordinates all aspects of the testing workflow and provides methods for discovering tests, executing individual tests or test suites, and validating results.

#### Initialization

When creating a TestRunner instance, you configure the execution backend, output directory, reference directory for validation, and validator configuration. The backend is responsible for actually executing the tests and must be an instance of a Backend subclass. The output directory is where test outputs will be stored, and the reference directory is used for validating test outputs against known correct results.

```python
from pathlib import Path
from regtests.runner import TestRunner, Validator, ComparisonMode
from regtests.runner.backends import LocalBackend, DockerBackend

# Using local backend
backend = LocalBackend(ww3_dir=Path("/path/to/ww3"))

# Using Docker backend
backend = DockerBackend(image="rompy/ww3:latest")

# Create validator with specific tolerance
validator = Validator(tolerance=1e-6, mode=ComparisonMode.RELATIVE)

# Initialize the runner
runner = TestRunner(
    backend=backend,
    output_dir=Path("test_outputs"),
    reference_dir=Path("reference_outputs"),
    validator=validator,
)
```

#### Discovering Tests

The discover_tests method scans a directory for test cases matching a specified pattern and returns a list of TestCase objects. Each TestCase contains the path to its configuration file and metadata about the test. The pattern uses glob syntax, so you can use wildcards to match multiple tests.

```python
# Discover all tests
all_tests = runner.discover_tests(Path("regtests/"), pattern="ww3_tp*")
print(f"Found {len(all_tests)} tests")

# Discover only tp1.x tests
tp1_tests = runner.discover_tests(Path("regtests/"), pattern="ww3_tp1.*")
print(f"Found {len(tp1_tests)} tp1.x tests")

# Discover specific test
specific_test = runner.discover_tests(Path("regtests/"), pattern="ww3_tp2.4")
if specific_test:
    test_case = specific_test[0]
    print(f"Test: {test_case.name}, Config: {test_case.config_path}")
```

#### Running Tests

There are two methods for executing tests depending on whether you want to run a single test or multiple tests. The run_test method executes a single TestCase and returns a TestResult with the outcome. The run_all method executes a list of tests and returns a TestSuiteResult that aggregates all results.

```python
# Run a single test
from regtests.runner import TestCase
from pathlib import Path

test = TestCase(config_path=Path("regtests/ww3_tp2.4/rompy_ww3_tp2_4.yaml"))
result = runner.run_test(test, validate=True)

print(f"Test: {result.test_name}")
print(f"Status: {result.status}")
print(f"Duration: {result.execution_time:.2f}s")
if result.error_message:
    print(f"Error: {result.error_message}")

# Run multiple tests
results = runner.run_all(tp1_tests, validate=True)

print(f"\nSuite Summary:")
print(f"Total Tests: {results.total_tests}")
print(f"Passed: {results.passed}")
print(f"Failed: {results.failed}")
print(f"Errors: {results.errors}")
print(f"Total Duration: {results.total_time:.2f}s")
print(f"Success: {results.is_success()}")
```

#### Validating Tests

The validate_test method checks whether a test configuration is valid without actually executing it. This is useful for catching configuration errors early or for pre-flight checks before running a full test suite.

```python
# Validate a test configuration
test = TestCase(config_path=Path("regtests/ww3_tp2.4/rompy_ww3_tp2_4.yaml"))
is_valid = runner.validate_test(test)
print(f"Test configuration valid: {is_valid}")
```

### InputFileManager Class

The InputFileManager class handles automatic discovery and downloading of input files required by WW3 regression tests. It parses test configurations to identify required input files and downloads them from the NOAA WW3 repository.

#### Automatic Input Management

By default, the TestRunner automatically manages input files through its internal InputFileManager instance. However, you can also use the InputFileManager directly for custom workflows.

```python
from pathlib import Path
from regtests.runner import InputFileManager, TestCase

# Initialize the input manager
manager = InputFileManager()

# Create a test case
test = TestCase(config_path=Path("regtests/ww3_tp2.4/rompy_ww3_tp2_4.yaml"))

# Check which inputs are missing
missing = manager.get_missing_inputs(test)
print(f"Missing inputs: {[p.name for p in missing]}")

# Download missing inputs
results = manager.download_inputs(test)
print(f"Downloaded: {len(results['downloaded'])}")
print(f"Failed: {len(results['failed'])}")

# Ensure all inputs are available (downloads if needed)
if manager.ensure_inputs(test):
    print("All inputs ready")
else:
    print("Failed to obtain some inputs")
```

#### Dry Run Mode

You can use dry-run mode to check what would be downloaded without actually downloading:

```python
# Check what would be downloaded
results = manager.download_inputs(test, dry_run=True)
print(f"Would download: {len(results['skipped'])} files")
for path_str in results['skipped']:
    print(f"  - {Path(path_str).name}")
```

#### Custom Source Repository

By default, input files are downloaded from the NOAA WW3 repository. You can specify a different base URL if needed:

```python
# Use a custom repository
manager = InputFileManager(
    base_url="https://raw.githubusercontent.com/myfork/WW3/develop/regtests"
)
```

### Backend Classes

The backend system provides abstraction for different execution environments. Currently, two backend implementations are available: LocalBackend for executing tests on the host system using the rompy CLI, and DockerBackend for running tests inside Docker containers.

#### LocalBackend

The LocalBackend executes tests using the rompy CLI directly on the host system. This backend requires rompy to be installed and available in the PATH, along with a working WW3 installation. It supports configuration of the WW3 directory for locating binaries and input files.

```python
from pathlib import Path
from regtests.runner.backends import LocalBackend

# Basic initialization (uses rompy from PATH)
backend = LocalBackend()

# Specify WW3 directory
backend = LocalBackend(ww3_dir=Path("/opt/WW3"))

# Check environment readiness
if backend.validate_env():
    print("Local environment ready")
else:
    print("Local environment not ready - check rompy installation")

# Get version information
version_info = backend.get_version_info()
print(f"rompy version: {version_info.get('rompy', 'unknown')}")
```

#### DockerBackend

The DockerBackend runs tests inside Docker containers, providing isolation and reproducibility. This backend is particularly useful when you need to ensure consistent execution environments across different machines or when the local system cannot run WW3 directly. The backend requires Docker to be installed and running, and it uses the specified Docker image for execution.

```python
from regtests.runner.backends import DockerBackend

# Basic initialization with default image
backend = DockerBackend(image="rompy/ww3:latest")

# Custom image
backend = DockerBackend(image="my-registry/ww3:custom")

# Check Docker availability
if backend.validate_env():
    print("Docker environment ready")
else:
    print("Docker not available")

# Get version information
version_info = backend.get_version_info()
print(f"Docker version: {version_info.get('docker', 'unknown')}")
print(f"Image: {version_info.get('image', 'unknown')}")
```

### ReportGenerator Class

The ReportGenerator class creates reports in multiple formats from TestSuiteResult objects. It provides methods for generating text, JSON, and HTML reports, as well as comparing results with previous runs for trend analysis.

#### Generating Text Reports

Text reports provide human-readable output suitable for console display or saving to text files. The report includes summary statistics, per-test results grouped by status, execution timing, and validation information.

```python
from regtests.runner.core.report import ReportGenerator

generator = ReportGenerator()

# Generate text report
text_report = generator.generate_text_report(
    results,
    title="WW3 Regression Test Results",
    show_skipped=True,
)

# Print to console
generator.print_report(text_report)

# Save to file
generator.save_report(text_report, Path("report.txt"))
```

#### Generating JSON Reports

JSON reports provide structured data suitable for programmatic processing, CI/CD integration, or storing results in a database. The JSON output includes all test metadata, status information, timing data, and validation results.

```python
import json

# Generate JSON report (without logs to reduce size)
json_report = generator.generate_json_report(
    results,
    include_logs=False,
)

# Save to file
generator.save_json_report(json_report, Path("report.json"))

# Access specific data programmatically
print(f"Total tests: {json_report['summary']['total_tests']}")
print(f"Success rate: {json_report['summary']['passed'] / json_report['summary']['total_tests']:.1%}")

# Process individual test results
for test in json_report['tests']:
    if test['status'] == 'failure':
        print(f"Failed: {test['name']}")
```

#### Generating HTML Reports

HTML reports provide an interactive, visually appealing format suitable for sharing results via web browsers or embedding in documentation. The HTML output includes styled summary cards, color-coded test status indicators, and collapsible error details.

```python
# Generate HTML report
html_report = generator.generate_html_report(
    results,
    title="WW3 Regression Test Report",
)

# Save to file
generator.save_report(html_report, Path("report.html"))

# The HTML report includes:
# - Gradient header with title and timestamp
# - Summary cards showing pass/fail/error/skipped counts
# - Color-coded test list with status icons
# - Validation info for each test
# - Formatted error messages
```

#### Trend Analysis

The compare_with_previous method generates a trend analysis report comparing current results with a previous run. This is useful for tracking test suite health over time and identifying regressions or improvements.

```python
# Assume we have results from previous runs
previous_results = ...  # TestSuiteResult from previous run
current_results = ...   # TestSuiteResult from current run

# Generate comparison report
trend_report = generator.compare_with_previous(current_results, previous_results)
print(trend_report)

# The trend report shows:
# - Summary comparison (total tests, passed, failed, errors, duration)
# - Per-test status changes (NEW, CHANGED, REMOVED)
# - Trend indicators (↑↓→) for each metric
```

### Validator Class

The Validator class compares test outputs against reference data to ensure numerical accuracy. It supports different comparison modes and tolerance levels for handling floating-point comparisons.

```python
from regtests.runner import Validator, ComparisonMode

# Create validator with default settings
validator = Validator()

# Custom tolerance and mode
validator = Validator(
    tolerance=1e-6,  # Relative tolerance of 1e-6
    mode=ComparisonMode.RELATIVE,  # Use relative comparison
)

# Strict validation
strict_validator = Validator(
    tolerance=1e-9,
    mode=ComparisonMode.ABSOLUTE,
)

# Validate outputs
validation_result = validator.validate(
    output_dir=Path("test_outputs/ww3_tp2.4"),
    reference_dir=Path("reference_outputs/ww3_tp2.4"),
)

print(f"Valid: {validation_result.is_valid()}")
print(f"Files compared: {validation_result.files_compared}")
print(f"Files matched: {validation_result.files_matched}")
if validation_result.differences:
    print("Differences found:")
    for diff in validation_result.differences[:5]:
        print(f"  - {diff}")
```

### Result Classes

The test runner uses several classes to represent test execution results. The TestStatus enum defines the possible statuses for individual tests: SUCCESS indicates the test ran and passed, FAILURE indicates the test ran but did not pass validation, ERROR indicates the test failed to execute due to an error, and SKIPPED indicates the test was not executed.

The TestResult class encapsulates the result of a single test execution, including the test name, status, execution time, optional error message, validation results, and generated output files. The TestSuiteResult class aggregates results from multiple tests and provides summary statistics and aggregate status checks.

```python
from regtests.runner import TestStatus, TestResult, TestSuiteResult

# Working with individual TestResult
result = TestResult(
    test_name="ww3_tp2.4",
    status=TestStatus.SUCCESS,
    execution_time=45.67,
    validation_results=validation_result,
)

print(f"Status: {result.status}")
print(f"Duration: {result.execution_time}s")
print(f"Passed validation: {result.status == TestStatus.SUCCESS}")

# Working with TestSuiteResult
suite = TestSuiteResult.from_results([result1, result2, result3])

print(f"Total: {suite.total_tests}")
print(f"Passed: {suite.passed}")
print(f"All passed: {suite.is_success()}")
print(f"Summary: {suite.summary()}")
```

## Test Configuration

Test cases are defined using YAML configuration files that follow the rompy-ww3 configuration format. Each test directory should contain a YAML file named `rompy_ww3_<test_name>.yaml` that defines the WW3 model configuration for that test.

### Configuration File Structure

A typical test configuration file includes several key sections. The domain section defines the temporal extent of the model run, including start and stop times and the output interval type. The grid section defines the spatial domain, including grid type, dimensions, and coordinates. The input section specifies forcing data such as winds, water levels, and other environmental conditions. The output section configures the desired output fields and their format.

```yaml
# Example test configuration: rompy_ww3_tp2_4.yaml
domain:
  start: "20200101 000000"
  stop: "20200102 000000"
  iostyp: 1

grid:
  type: rect
  nx: 72
  ny: 36
  dx: 5.0
  dy: 5.0
  coordinates:
    - [0.0, 0.0]
    - [5.0, 0.0]
    - [5.0, 5.0]
    - [0.0, 5.0]

input_nml:
  forcing:
    winds: "T"
    water_levels: "T"

components:
  - type: shel
```

### Input Data Requirements

Many tests require additional input data files such as depth files, wind fields, boundary conditions, and point lists. These files should be placed in an `input/` subdirectory within the test directory. The test runner automatically includes these files when executing tests.

```
regtests/ww3_tp2.4/
├── rompy_ww3_tp2_4.yaml
└── input/
    ├── depth.dat
    ├── points.list
    └── wind.nc
```

## Report Formats

The test runner generates reports in three formats, each optimized for different use cases. Understanding these formats helps you choose the right one for your needs.

### Text Report Format

Text reports provide a clean, readable format suitable for console output or logging. The report begins with a header showing the title and generation timestamp. Summary statistics follow, showing total tests, pass/fail/error/skipped counts with percentages, and execution timing. Individual test results are grouped by status (passed, failed, errors, skipped), with each entry showing the test name, execution time, and validation information.

```
================================================================================
                    WW3 Regression Test Report                  
================================================================================
Generated: 2026-02-11 14:30:45

SUMMARY
--------------------------------------------------------------------------------
Total Tests:      5
Passed:           4 (80.0%)
Failed:           1 (20.0%)
Errors:           0 (0.0%)
Skipped:          0 (0.0%)
Total Duration:   234.56s
Average Duration: 46.91s

✗ TESTS FAILED

TEST DETAILS
--------------------------------------------------------------------------------

PASSED TESTS:
  ✓ ww3_tp1.1                    12.34s (validated: 5/5 files)
  ✓ ww3_tp1.2                    45.67s (validated: 5/5 files)
  ✓ ww3_tp2.1                    23.45s (validated: 5/5 files)
  ✓ ww3_tp2.4                    67.89s (validated: 5/5 files)

FAILED TESTS:
  ✗ ww3_tp2.5                    85.21s
     Validation: 3/5 files matched
     Differences:
       - Variable 'hs' at (10, 20): 2.34 vs 2.35 (relative diff: 0.4%)
       - Variable 'hs' at (11, 20): 2.45 vs 2.46 (relative diff: 0.4%)
       - Variable 'hs' at (12, 20): 2.56 vs 2.57 (relative diff: 0.4%)
       ... and 2 more differences

================================================================================
```

### JSON Report Format

JSON reports provide structured data suitable for programmatic processing and integration with CI/CD systems. The JSON structure includes metadata with generation timestamp, a summary object with statistics, and an array of individual test results. Each test result includes the name, status, execution time, validation results (if available), error messages (if any), and paths to generated outputs.

```json
{
  "metadata": {
    "generated_at": "2026-02-11T14:30:45.000000",
    "timestamp": 1707661845.0
  },
  "summary": {
    "total_tests": 5,
    "passed": 4,
    "failed": 1,
    "errors": 0,
    "skipped": 0,
    "total_time": 234.56,
    "average_time": 46.912,
    "success": false
  },
  "tests": [
    {
      "name": "ww3_tp2.4",
      "status": "success",
      "execution_time": 67.89,
      "validation": {
        "files_compared": 5,
        "files_matched": 5,
        "is_valid": true,
        "tolerance": 1e-6,
        "differences": []
      },
      "outputs": [
        "/path/to/outputs/ww3_tp2.4/ww3_shel.nc"
      ]
    }
  ]
}
```

### HTML Report Format

HTML reports provide an interactive, visually rich format suitable for web browsers. The report includes a gradient header with the title and generation timestamp. Summary cards display key statistics with color coding (green for passed, red for failed, yellow for errors, gray for skipped). The test list shows each test with a status indicator, name, metadata, execution time, validation information, and error messages. The HTML includes embedded CSS styling for clean presentation without external dependencies.

## Troubleshooting

This section addresses common issues and their solutions when using the test runner. If you encounter problems not covered here, check the error messages carefully and verify your environment setup.

### Common Issues

**No tests discovered**: When the test runner reports zero discovered tests, verify that your test directory structure is correct. Test directories must be named with the pattern `ww3_tp*` and must contain YAML configuration files matching `rompy_ww3_*.yaml`. Also ensure that the path you provide to discover_tests points to the correct directory containing the test subdirectories.

**Validation failures**: If tests pass execution but fail validation, first check that reference outputs exist in the expected directory structure. The reference directory must have the same structure as the output directory, with reference files in subdirectories matching test names. If files exist but validation still fails, you may need to adjust the tolerance level or check for known numerical differences between WW3 versions.

**Local backend not available**: If the local backend fails validation, ensure that `rompy` is installed and available in your PATH. Run `rompy --version` manually to verify. Also ensure that WW3 is properly installed and that configuration files reference correct paths for WW3 binaries and input data.

**Docker backend not available**: If Docker backend validation fails, ensure that Docker is installed and running. On Linux, you may need to add your user to the `docker` group or run with sudo. Verify that the specified Docker image exists by running `docker pull rompy/ww3:latest` or your custom image name.

**Timeouts during test execution**: Tests that timeout may require more time or may be stuck. Check the test configuration for reasonable time limits. For long-running tests, consider increasing the timeout or running tests in the background. Also verify that input data files are correctly specified and accessible.

**Missing input data**: Tests requiring external input data (depth files, wind fields, boundary conditions) will fail if those files are missing. Download required input data from the NOAA-EMC/WW3 repository and place them in the appropriate `input/` subdirectory within each test directory.

### Debug Mode

Enable verbose logging to see detailed information about test execution:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now run tests with debug output
runner = TestRunner(backend=backend)
results = runner.run_all(tests, validate=True)
```

### Environment Verification

Use the backend validation methods to check your environment before running tests:

```python
from regtests.runner.backends import LocalBackend, DockerBackend

# Check local backend
local_backend = LocalBackend()
if local_backend.validate_env():
    print("Local backend ready")
    print(local_backend.get_version_info())
else:
    print("Local backend not ready")

# Check Docker backend
docker_backend = DockerBackend()
if docker_backend.validate_env():
    print("Docker backend ready")
    print(docker_backend.get_version_info())
else:
    print("Docker backend not ready")
```

### Log Analysis

When tests fail, examine the execution logs for details. The TestResult includes stdout and stderr from the rompy execution:

```python
result = runner.run_test(test_case)

if result.status.value in ["failure", "error"]:
    print("Execution logs:")
    if result.logs:
        print(result.logs)
    if result.error_message:
        print(f"Error message: {result.error_message}")
```

## Advanced Usage

### Parallel Test Execution

For large test suites, you can execute tests in parallel using Python's concurrent.futures. This can significantly reduce total execution time on multi-core systems.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from regtests.runner import TestRunner
from regtests.runner.backends import LocalBackend
from pathlib import Path

backend = LocalBackend()
runner = TestRunner(backend=backend)

# Discover tests
tests = runner.discover_tests(Path("regtests/"), pattern="ww3_tp*")

# Execute in parallel
results = []
with ThreadPoolExecutor(max_workers=4) as executor:
    future_to_test = {executor.submit(runner.run_test, test): test for test in tests}
    for future in as_completed(future_to_test):
        result = future.result()
        results.append(result)
        print(f"Completed: {result.test_name} - {result.status}")

# Create suite result from parallel results
from regtests.runner import TestSuiteResult
suite_result = TestSuiteResult.from_results(results)
```

### Custom Backends

Create custom backends by subclassing the Backend base class for specialized execution environments. This is useful for cloud-based execution, HPC clusters, or other specialized infrastructure.

```python
from regtests.runner.backends.base import Backend
from regtests.runner.core.test import TestCase
from regtests.runner.core.result import TestResult, TestStatus
from pathlib import Path

class CustomBackend(Backend):
    def __init__(self, config):
        self.config = config
    
    def execute(self, test: TestCase, workdir: Path) -> TestResult:
        # Implement custom execution logic
        # ...
        return TestResult(
            test_name=test.name,
            status=TestStatus.SUCCESS,
            execution_time=0.0,
        )
    
    def validate_env(self) -> bool:
        # Check environment readiness
        return True
    
    def get_version_info(self) -> dict:
        return {"custom": "1.0"}

# Use custom backend
backend = CustomBackend(config={"endpoint": "https://api.example.com"})
runner = TestRunner(backend=backend)
```

### CI/CD Integration

Integrate test runner results with CI/CD systems using JSON reports. Here's an example GitHub Actions workflow step:

```yaml
- name: Run WW3 Regression Tests
  run: |
    python -m regtests.runner \
      --all \
      --path regtests \
      --validate \
      --reference reference_outputs \
      --report json \
      --output test_results.json

- name: Parse Results
  run: |
    import json
    with open("test_results.json") as f:
        results = json.load(f)
    
    if not results["summary"]["success"]:
        print(f"Tests failed: {results['summary']['failed']}")
        exit(1)
    print("All tests passed")
```

## API Reference

### regtests.runner

| Class | Description |
|-------|-------------|
| `TestRunner` | Main orchestrator for test discovery, execution, and reporting |
| `TestCase` | Encapsulates test configuration and metadata |
| `TestResult` | Result of a single test execution |
| `TestSuiteResult` | Aggregated results from multiple tests |
| `TestStatus` | Enum: SUCCESS, FAILURE, ERROR, SKIPPED |
| `Validator` | Compares test outputs against reference data |
| `ComparisonMode` | Enum: RELATIVE, ABSOLUTE for comparisons |
| `Backend` | Abstract base class for execution backends |
| `InputFileManager` | Discovers and downloads input files from NOAA WW3 repository |

### regtests.runner.backends

| Class | Description |
|-------|-------------|
| `LocalBackend` | Executes tests via rompy CLI on host system |
| `DockerBackend` | Executes tests inside Docker containers |

### regtests.runner.core.report

| Class | Description |
|-------|-------------|
| `ReportGenerator` | Generates reports in text, JSON, and HTML formats |

## Contributing

When contributing to the test runner, ensure that new functionality is documented with clear docstrings and that the documentation in this README is updated to reflect any new features or changed behavior. All code should pass formatting checks and include appropriate error handling.
