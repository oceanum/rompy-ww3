"""Test case representation and management."""

from pathlib import Path
from typing import List, Optional
import logging
import yaml

from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of test case validation.

    Attributes:
        is_valid: Whether the test case passed validation
        message: Explanation of validation result
        missing_files: List of required files that are missing
    """

    is_valid: bool
    message: str
    missing_files: List[Path] = None

    def __post_init__(self):
        if self.missing_files is None:
            self.missing_files = []


class TestCase:
    """Encapsulates a single WW3 regression test case.

    A test case represents one regression test configuration, including:
    - Path to configuration file (YAML)
    - Test metadata (name, series, description)
    - Required input files
    - Expected outputs

    Example:
        >>> test = TestCase(config_path="regtests/ww3_tp1.1/rompy_ww3_tp1_1.yaml")
        >>> print(test.name)
        'tp1.1'
        >>> print(test.series)
        'tp1.x'
        >>> validation = test.validate()
        >>> if validation.is_valid:
        ...     print("Test is ready to run")
    """

    def __init__(self, config_path: Path):
        """Initialize test case from configuration file.

        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = Path(config_path)
        self.test_dir = self.config_path.parent
        self._config = None

    @property
    def name(self) -> str:
        """Test identifier (e.g., 'tp1.1')."""
        config_name = self.config_path.stem
        if "_grdset_" in config_name:
            if config_name.startswith("rompy_ww3_"):
                return config_name[10:]
            return config_name

        dir_name = self.test_dir.name
        if dir_name.startswith("ww3_"):
            return dir_name[4:]
        return dir_name

    @property
    def series(self) -> str:
        """Test series identifier (e.g., 'tp1.x').

        Extracts the series from the test name.
        Example: 'tp1.1' -> 'tp1.x'
        """
        name = self.name
        if "." in name:
            base = name.split(".")[0]
            return f"{base}.x"
        return name

    def load_config(self) -> dict:
        """Load and parse YAML configuration.

        Returns:
            Parsed configuration as dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid YAML
        """
        if self._config is None:
            logger.debug(f"Loading config from {self.config_path}")
            with open(self.config_path, "r") as f:
                self._config = yaml.safe_load(f)
        return self._config

    def get_required_inputs(self) -> List[Path]:
        """List required input files for this test.

        Scans the test directory for input files and returns their paths.

        Returns:
            List of paths to required input files
        """
        input_dir = self.test_dir / "input"
        if not input_dir.exists():
            return []

        # List all files in input directory
        input_files = []
        for file_path in input_dir.rglob("*"):
            if file_path.is_file():
                input_files.append(file_path)

        return input_files

    def validate(self) -> ValidationResult:
        """Validate test case configuration and requirements.

        Checks:
        - Configuration file exists and is valid YAML
        - Required input files are present
        - Configuration has required fields

        Returns:
            ValidationResult indicating validity and any issues
        """
        # Check config file exists
        if not self.config_path.exists():
            return ValidationResult(
                is_valid=False,
                message=f"Config file not found: {self.config_path}",
            )

        # Try loading config
        try:
            self.load_config()
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"Failed to load config: {e}",
            )

        # Check for required input files
        required_inputs = self.get_required_inputs()
        missing_files = []
        for input_file in required_inputs:
            if not input_file.exists():
                missing_files.append(input_file)

        if missing_files:
            return ValidationResult(
                is_valid=False,
                message=f"Missing {len(missing_files)} required input files",
                missing_files=missing_files,
            )

        # All checks passed
        return ValidationResult(
            is_valid=True,
            message="Test case is valid",
        )

    @property
    def reference_output_dir(self) -> Optional[Path]:
        """Path to reference outputs for validation (if available).

        Returns:
            Path to reference outputs, or None if not available
        """
        ref_dir = Path("regtests/reference_outputs") / self.name
        if ref_dir.exists():
            return ref_dir
        return None

    def __repr__(self) -> str:
        return f"TestCase(name='{self.name}', series='{self.series}')"
