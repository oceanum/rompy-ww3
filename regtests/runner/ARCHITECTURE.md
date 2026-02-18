# Test Runner Architecture

## Overview

The WW3 regression test runner provides automated execution, validation, and reporting for rompy-ww3 regression tests. It discovers test configurations, executes them via backend systems (local/Docker), compares outputs against reference data, and generates comprehensive reports.

## Design Principles

1. **Separation of Concerns**: TestRunner orchestrates, TestCase encapsulates, Backend executes
2. **Backend Abstraction**: Pluggable execution backends (local, Docker) via unified interface
3. **Extensibility**: Easy to add new test cases, backends, or validation strategies
4. **Fail-Fast**: Early validation of test configurations before execution
5. **Observable**: Progress reporting, logging, and detailed result tracking
6. **Idempotent**: Re-running tests produces consistent results

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         TestRunner                               │
│  • discover_tests()    • run_test()    • run_all()              │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ manages
             │
    ┌────────▼─────────┐          ┌──────────────────┐
    │    TestCase      │          │   TestResult     │
    │  • config_path   │◄────────►│  • status        │
    │  • load_config() │ produces │  • outputs       │
    │  • validate()    │          │  • validation    │
    └────────┬─────────┘          └──────────────────┘
             │
             │ uses
             │
    ┌────────▼─────────────────────────────────────────┐
    │              Backend (ABC)                        │
    │  • execute()    • validate_env()                  │
    └────────┬──────────────────────────┬───────────────┘
             │                          │
     ┌───────▼──────────┐      ┌────────▼──────────────┐
     │  LocalBackend    │      │   DockerBackend       │
     │  • WW3_DIR path  │      │   • Image management  │
     │  • Direct exec   │      │   • Volume mounting   │
     └──────────────────┘      └───────────────────────┘
```

## Core Components

### 1. TestRunner

**Purpose**: Orchestration of test discovery, execution, and reporting.

**Key Responsibilities**:
- Discover test configurations in regtests/ directory
- Manage test execution lifecycle
- Aggregate and report results
- Handle parallel execution (future)

**Interface**:
```python
class TestRunner:
    def __init__(self, backend: Backend, config: RunnerConfig):
        """Initialize with execution backend and configuration."""
        
    def discover_tests(self, path: Path, pattern: str = "ww3_tp*") -> List[TestCase]:
        """Discover test cases matching pattern in path."""
        
    def run_test(self, test: TestCase) -> TestResult:
        """Execute a single test case and return result."""
        
    def run_all(self, tests: List[TestCase]) -> TestSuiteResult:
        """Execute multiple test cases and aggregate results."""
        
    def validate_test(self, test: TestCase) -> ValidationResult:
        """Validate test configuration before execution."""
```

**Configuration**:
- Backend selection (local/Docker)
- Output directories
- Validation tolerance levels
- Timeout settings
- Logging verbosity

### 2. TestCase

**Purpose**: Encapsulation of individual regression test configuration and metadata.

**Key Responsibilities**:
- Load test configuration (YAML/Python)
- Provide test metadata (name, series, purpose)
- Track input/output file requirements
- Validate configuration completeness

**Interface**:
```python
class TestCase:
    def __init__(self, config_path: Path):
        """Initialize from configuration file path."""
        
    @property
    def name(self) -> str:
        """Test identifier (e.g., 'tp1.1')."""
        
    @property
    def series(self) -> str:
        """Test series (e.g., 'tp1.x')."""
        
    def load_config(self) -> Config:
        """Load and parse rompy-ww3 configuration."""
        
    def get_required_inputs(self) -> List[Path]:
        """List required input files."""
        
    def validate(self) -> ValidationResult:
        """Validate configuration completeness."""
```

**Attributes**:
- `config_path`: Path to YAML/Python config
- `test_dir`: Directory containing test files
- `reference_output`: Path to reference output (optional)
- `metadata`: Test description, physics, expected outputs

### 3. Backend (Abstract Base)

**Purpose**: Abstract interface for test execution environments.

**Key Responsibilities**:
- Execute WW3 model runs
- Manage execution environment
- Capture outputs and logs
- Provide execution status

**Interface**:
```python
from abc import ABC, abstractmethod

class Backend(ABC):
    @abstractmethod
    def execute(self, test: TestCase, workdir: Path) -> ExecutionResult:
        """Execute test case and return execution result."""
        
    @abstractmethod
    def validate_env(self) -> bool:
        """Check if backend environment is ready."""
        
    @abstractmethod
    def get_version_info(self) -> Dict[str, str]:
        """Return backend and WW3 version information."""
```

### 4. LocalBackend

**Purpose**: Execute tests using local WW3 installation.

**Implementation Details**:
- Requires WW3_DIR environment variable
- Direct subprocess execution
- Fast but requires local WW3 compilation
- Limited portability

**Configuration**:
```python
class LocalBackend(Backend):
    def __init__(self, ww3_dir: Path):
        """Initialize with WW3 installation directory."""
```

### 5. DockerBackend

**Purpose**: Execute tests in Docker container.

**Implementation Details**:
- Uses rompy-ww3 Docker image
- Volume mounting for inputs/outputs
- Slower but highly portable
- Consistent environment

**Configuration**:
```python
class DockerBackend(Backend):
    def __init__(self, image: str, docker_client: docker.DockerClient):
        """Initialize with Docker image and client."""
```

### 6. TestResult

**Purpose**: Encapsulate execution result and validation outcome.

**Attributes**:
```python
@dataclass
class TestResult:
    test_name: str
    status: TestStatus  # SUCCESS, FAILURE, ERROR, SKIPPED
    execution_time: float
    outputs_generated: List[Path]
    validation_results: Optional[ValidationReport]
    error_message: Optional[str]
    logs: str
```

### 7. TestSuiteResult

**Purpose**: Aggregate results for multiple test executions.

**Attributes**:
```python
@dataclass
class TestSuiteResult:
    total_tests: int
    passed: int
    failed: int
    errors: int
    skipped: int
    total_time: float
    results: List[TestResult]
```

## Execution Flow

### Discovery Phase

```
1. TestRunner.discover_tests(path)
   ↓
2. Scan for directories matching pattern (ww3_tp*)
   ↓
3. For each directory:
   • Find YAML config (rompy_ww3_tp*.yaml)
   • Create TestCase instance
   • Load metadata from config
   ↓
4. Return list of TestCase objects
```

### Execution Phase

```
1. TestRunner.run_test(test_case)
   ↓
2. Validate test configuration
   • Check required inputs exist
   • Validate config syntax
   • Check backend availability
   ↓
3. Backend.execute(test_case, workdir)
   • Setup execution environment
   • Run WW3 components (grid, shel, ounf, etc.)
   • Capture outputs and logs
   ↓
4. Collect outputs
   • Identify generated files
   • Copy to results directory
   ↓
5. Validate outputs (if reference available)
   • Compare NetCDF variables
   • Check log for errors
   • Generate validation report
   ↓
6. Return TestResult
```

### Validation Phase

```
1. Load reference outputs
   ↓
2. For each output file:
   • NetCDF: Compare dimensions, variables, values
   • Binary: Checksum comparison
   • Text: Line-by-line diff
   ↓
3. Apply tolerance levels:
   • Strict: 1e-9 relative tolerance
   • Normal: 1e-6 relative tolerance
   • Loose: 1e-3 relative tolerance
   ↓
4. Generate ValidationReport
   • Files compared
   • Differences found
   • Pass/fail status
```

## Integration with rompy-ww3

The test runner integrates with existing rompy-ww3 infrastructure:

1. **Configuration Loading**: Uses rompy-ww3 `Config` class to parse YAML
2. **Backend System**: Leverages rompy execution backends (local/Docker)
3. **Data Management**: Uses existing data download infrastructure
4. **Component Execution**: Invokes rompy-ww3 component rendering and execution

## Directory Structure

```
regtests/
├── runner/
│   ├── __init__.py
│   ├── ARCHITECTURE.md         # This document
│   ├── core/
│   │   ├── __init__.py
│   │   ├── runner.py           # TestRunner class
│   │   ├── test.py             # TestCase class
│   │   ├── result.py           # TestResult, TestSuiteResult
│   │   └── validator.py        # Output validation logic
│   └── backends/
│       ├── __init__.py
│       ├── base.py             # Backend ABC
│       ├── local.py            # LocalBackend
│       └── docker.py           # DockerBackend
├── ww3_tp1.1/                  # Test case directories
├── ww3_tp2.4/
└── run_regression_tests.py     # CLI entry point
```

## CLI Interface

**Proposed command-line interface**:

```bash
# Run all tests
python run_regression_tests.py --all

# Run specific test series
python run_regression_tests.py --series tp1.x

# Run specific test
python run_regression_tests.py --test tp1.1

# With specific backend
python run_regression_tests.py --all --backend docker

# With validation
python run_regression_tests.py --all --validate

# With custom tolerance
python run_regression_tests.py --all --validate --tolerance 1e-6

# Parallel execution (future)
python run_regression_tests.py --all --parallel 4

# Generate HTML report
python run_regression_tests.py --all --report html
```

## Future Enhancements

### Phase 1: Core Functionality (Current)
- Test discovery
- Sequential execution
- Basic validation
- Console reporting

### Phase 2: Advanced Features
- Parallel test execution
- HTML report generation
- Progress bars and real-time updates
- Test result caching

### Phase 3: CI/CD Integration
- GitHub Actions integration
- Automated reference update
- Performance tracking over time
- Coverage analysis

### Phase 4: Switch Compilation
- Switch file parsing
- Dynamic WW3 compilation
- Binary caching
- Multi-configuration testing

## Design Decisions

### Why Abstract Backend?
- Allows easy addition of new execution environments (HPC, cloud)
- Consistent interface regardless of execution method
- Simplifies testing of runner itself

### Why TestCase Class?
- Encapsulates test-specific logic
- Makes adding new tests straightforward
- Provides clear contract for test requirements

### Why Not pytest?
- Regression tests are integration tests, not unit tests
- Need custom execution flow (grid → shel → ounf sequence)
- Require specialized validation (NetCDF comparison)
- Benefit from custom reporting (WW3-specific metrics)

### Backend Selection Strategy
- **Local**: Fast, for development and quick validation
- **Docker**: Portable, for CI and reproducible results
- Default to Docker in CI, local otherwise

## Error Handling

- **Configuration errors**: Fail fast during validation phase
- **Execution errors**: Capture logs, report as FAILED
- **Backend unavailable**: Report as SKIPPED with reason
- **Missing references**: Run without validation, report WARNING

## Logging Strategy

- **Test Runner**: INFO level for progress, DEBUG for details
- **Backend**: Capture all stdout/stderr
- **Components**: Use existing rompy-ww3 logging
- **Output**: Console + log file per test

## Performance Considerations

- **Test Discovery**: Fast (file system scan)
- **Execution**: Depends on backend (local: ~1-5 min, Docker: ~2-10 min per test)
- **Validation**: Fast (NetCDF library is efficient)
- **Parallel Execution**: Future enhancement to reduce total time

## Testing the Test Runner

The test runner itself should be tested:
- Unit tests for TestCase, Backend classes
- Integration tests with mock WW3 execution
- End-to-end tests with actual tp1.1 test
- Backend availability detection tests
