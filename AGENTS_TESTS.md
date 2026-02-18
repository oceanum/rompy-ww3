## tests

**OVERVIEW**
Comprehensive pytest-based test suite with automatic data downloading and Docker-aware execution for WW3 model testing.

**STRUCTURE**
```
tests/
├── conftest.py              # Pytest configuration with auto data download
├── test_utils/               # Test utilities (logging helpers)
└── test_*.py                # 16+ test files covering all components
```

**WHERE TO LOOK**

| Task | Location | Notes |
|------|----------|-------|
| Pytest configuration | `conftest.py` | Auto data download, Docker detection, CI handling |
| Test utilities | `test_utils/logging.py` | Centralized test logging configuration |
| Component tests | `test_*.py` | Individual tests for namelists, components, data handling |
| Test data | `data/` (auto-downloaded) | Automatically fetched from rompy-test-data repo |

**CONVENTIONS**

**Only deviations from standard pytest patterns:**

- **Automatic Data Download**: Tests automatically fetch data from `rom-py/rompy-test-data` GitHub releases on startup
- **Docker-Aware Testing**: Conditional Docker execution with `docker_available()` fixture and CI environment detection
- **Configurable Logging**: `--rompy-log-level` option for customizing test logging output
- **Slow Test Marking**: `--run-slow` option for enabling time-intensive tests
- **Test Data Caching**: Downloaded data cached locally to avoid repeated downloads
- **Session-Level Fixtures**: Docker availability and logging configured once per test session

**ANTI-PATTERNS (THIS PROJECT)**

**Critical prohibitions for testing:**

- **No Manual Data Setup**: "Tests should never require manual test data setup" - automatic download enforced
- **Docker Build Skipping**: Docker builds automatically skipped in CI unless `ROMPY_ENABLE_DOCKER_IN_CI` is explicitly set
- **CI Environment Detection**: Never assume Docker availability - always check `should_skip_docker_builds()` fixture
- **Test Data Hardcoding**: Never hardcode test data paths - use fixtures and auto-downloaded data
- **Logging Silence**: Tests must configure proper logging - no silent test failures allowed
- **Fixture Autouse**: Session-level fixtures run automatically to ensure consistent test environment