# TESTS KNOWLEDGE BASE

**Generated:** 2026-01-13 01:12:15
**Commit:** Unknown
**Branch:** main

## OVERVIEW
Comprehensive test suite for rompy-ww3 with 15 test files covering all components, automatic data management, and Docker-aware execution.

## STRUCTURE
```
tests/
├── conftest.py              # Central test configuration and fixtures
├── test_*.py                 # 15 component-specific test files
├── test_utils/                 # Test utilities
└── reference_nmls/            # Reference namelist files
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Test configuration | `conftest.py` | Auto data download, Docker detection, CI handling |
| Component tests | `test_*.py` | Comprehensive coverage of all components |
| Test utilities | `test_utils/logging.py` | Logging configuration for tests |
| Reference namelists | `reference_nmls/` | Expected output for validation |

## CONVENTIONS

**Test-specific patterns:**

- **Automatic Data Management**: Tests auto-download from `rom-py/rompy-test-data` GitHub releases
- **Docker-Aware Testing**: Conditional execution based on CI environment
- **Minimal Mocking**: Direct integration testing with real data
- **Pytest Configuration**: Custom options for logging levels and slow tests
- **Environment Detection**: CI platform detection (GitHub Actions, Travis, etc.)

## ANTI-PATTERNS (TESTING)

**Critical prohibitions for test development:**

- **No Manual Setup**: Never assume test data exists - use auto-download
- **Docker Assumptions**: Don't assume Docker is available - use `should_skip_docker_builds()`
- **CI Environment**: Always detect CI environment before enabling Docker
- **Test Data Location**: Use configured DATA_DIR, never hardcode paths
- **Slow Tests**: Use `@pytest.mark.slow` for integration tests
- **Isolation**: Use `tempfile.TemporaryDirectory()` for all file operations

## LOCAL DEVELOPMENT ENVIRONMENT

**Virtual Environment Setup:**
```bash
# Create and activate local virtual environment
python -m venv .venv
source .venv/bin/activate  # On Unix/Mac
# or .venv\Scripts\activate  # On Windows

# Install with uv (recommended)
uv venv .venv
source .venv/bin/activate
uv pip install -e .[dev,test]

# Run tests in virtual environment
pytest tests/
```

**Requirements:**
- **Virtual Environment**: All Python testing must be done in `.venv` in root directory
- **Python Management**: Python is managed with `uv` for package management
- **Development Dependencies**: Install with `[dev,test]` extras
- **Isolation**: Never use system Python or global packages

**Testing Workflow:**
1. Create/activate `.venv` virtual environment
2. Install dependencies with `uv pip install -e .[dev,test]`
3. Run tests with `pytest tests/` from virtual environment
4. Ensure all test data is auto-downloaded by conftest fixtures