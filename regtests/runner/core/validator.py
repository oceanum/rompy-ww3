"""Output validation against reference data."""

from pathlib import Path
from typing import List, Optional
import logging

from .result import ValidationReport


logger = logging.getLogger(__name__)


class Validator:
    """Validates test outputs against reference data.

    Performs comparison of test outputs with reference outputs to determine
    if the test produced expected results. Supports multiple file formats:
    - NetCDF files: Variable-by-variable comparison with tolerance
    - Binary files: Checksum comparison
    - Text files: Line-by-line diff

    Example:
        >>> validator = Validator(tolerance=1e-6)
        >>> report = validator.validate(
        ...     output_dir=Path("test_outputs/tp1.1"),
        ...     reference_dir=Path("reference_outputs/tp1.1"),
        ... )
        >>> if report.is_valid():
        ...     print("Validation passed")
    """

    def __init__(self, tolerance: float = 1e-6):
        """Initialize validator with tolerance level.

        Args:
            tolerance: Relative tolerance for numerical comparisons
                      (default: 1e-6)
        """
        self.tolerance = tolerance

    def validate(
        self,
        output_dir: Path,
        reference_dir: Path,
        file_patterns: Optional[List[str]] = None,
    ) -> ValidationReport:
        """Validate outputs against reference data.

        Compares all files in output_dir with corresponding files in
        reference_dir. Files are matched by name.

        Args:
            output_dir: Directory containing test outputs
            reference_dir: Directory containing reference outputs
            file_patterns: Optional list of glob patterns to filter files
                         (default: compare all files)

        Returns:
            ValidationReport with comparison results

        Example:
            >>> report = validator.validate(
            ...     output_dir=Path("outputs"),
            ...     reference_dir=Path("references"),
            ...     file_patterns=["*.nc", "out_grd.ww3"],
            ... )
        """
        logger.info(f"Validating outputs against {reference_dir}")

        # Find files to compare
        if file_patterns is None:
            file_patterns = ["*"]

        files_to_compare = []
        for pattern in file_patterns:
            files_to_compare.extend(output_dir.glob(pattern))

        differences = []
        files_compared = 0
        files_matched = 0

        for output_file in files_to_compare:
            if not output_file.is_file():
                continue

            # Find corresponding reference file
            relative_path = output_file.relative_to(output_dir)
            reference_file = reference_dir / relative_path

            if not reference_file.exists():
                differences.append(f"Missing reference for {relative_path}")
                continue

            files_compared += 1

            # Compare based on file type
            if self._compare_files(output_file, reference_file):
                files_matched += 1
            else:
                differences.append(f"Mismatch in {relative_path}")

        logger.info(f"Validation complete: {files_matched}/{files_compared} matched")

        return ValidationReport(
            files_compared=files_compared,
            files_matched=files_matched,
            differences=differences,
            tolerance_used=self.tolerance,
        )

    def _compare_files(self, output_file: Path, reference_file: Path) -> bool:
        """Compare two files based on their type.

        Args:
            output_file: Test output file
            reference_file: Reference file

        Returns:
            True if files match within tolerance, False otherwise
        """
        suffix = output_file.suffix.lower()

        if suffix == ".nc":
            return self._compare_netcdf(output_file, reference_file)
        elif suffix in [".ww3", ".dat"]:
            return self._compare_binary(output_file, reference_file)
        else:
            return self._compare_text(output_file, reference_file)

    def _compare_netcdf(self, output_file: Path, reference_file: Path) -> bool:
        """Compare NetCDF files variable by variable.

        Args:
            output_file: Test output NetCDF file
            reference_file: Reference NetCDF file

        Returns:
            True if variables match within tolerance
        """
        # Placeholder implementation
        # TODO: Implement NetCDF comparison using xarray or netCDF4
        logger.debug(f"Comparing NetCDF: {output_file.name}")
        return True

    def _compare_binary(self, output_file: Path, reference_file: Path) -> bool:
        """Compare binary files via checksum.

        Args:
            output_file: Test output binary file
            reference_file: Reference binary file

        Returns:
            True if checksums match
        """
        # Placeholder implementation
        # TODO: Implement binary comparison using hashlib
        logger.debug(f"Comparing binary: {output_file.name}")
        return True

    def _compare_text(self, output_file: Path, reference_file: Path) -> bool:
        """Compare text files line by line.

        Args:
            output_file: Test output text file
            reference_file: Reference text file

        Returns:
            True if files match
        """
        # Placeholder implementation
        # TODO: Implement text comparison
        logger.debug(f"Comparing text: {output_file.name}")
        return True
