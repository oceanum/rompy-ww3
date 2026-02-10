"""Output validation against reference data."""

from pathlib import Path
from typing import List, Optional, Dict
from enum import Enum
import logging
import hashlib

import xarray as xr
import numpy as np

from .result import ValidationReport


logger = logging.getLogger(__name__)


class ComparisonMode(Enum):
    """Comparison mode for numerical tolerance."""

    EXACT = "exact"  # Bit-for-bit comparison
    RELATIVE = "relative"  # |a-b|/|b| < tolerance
    ABSOLUTE = "absolute"  # |a-b| < tolerance


class Validator:
    """Validates test outputs against reference data.

    Performs comparison of test outputs with reference outputs to determine
    if the test produced expected results. Supports multiple file formats:
    - NetCDF files: Variable-by-variable comparison with tolerance
    - Binary files: Checksum comparison
    - Text files: Line-by-line diff

    Example:
        >>> validator = Validator(tolerance=1e-6, mode=ComparisonMode.RELATIVE)
        >>> report = validator.validate(
        ...     output_dir=Path("test_outputs/tp1.1"),
        ...     reference_dir=Path("reference_outputs/tp1.1"),
        ... )
        >>> if report.is_valid():
        ...     print("Validation passed")
    """

    def __init__(
        self,
        tolerance: float = 1e-6,
        mode: ComparisonMode = ComparisonMode.RELATIVE,
        field_tolerances: Optional[Dict[str, float]] = None,
    ):
        """Initialize validator with tolerance settings.

        Args:
            tolerance: Default tolerance for numerical comparisons (default: 1e-6)
            mode: Comparison mode (default: RELATIVE)
            field_tolerances: Field-specific tolerance overrides
                            (e.g., {"HS": 0.01, "T01": 0.1})
        """
        self.tolerance = tolerance
        self.mode = mode
        self.field_tolerances = field_tolerances or {}

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
        try:
            output_ds = xr.open_dataset(output_file)
            reference_ds = xr.open_dataset(reference_file)
        except Exception as e:
            logger.error(f"Failed to open NetCDF files: {e}")
            return False

        try:
            if set(output_ds.data_vars) != set(reference_ds.data_vars):
                logger.warning(f"Variable mismatch in {output_file.name}")
                return False

            all_match = True
            for var_name in output_ds.data_vars:
                var_name_str = str(var_name)
                field_tolerance = self.field_tolerances.get(
                    var_name_str, self.tolerance
                )

                output_var = output_ds[var_name].values
                reference_var = reference_ds[var_name].values

                if output_var.shape != reference_var.shape:
                    logger.warning(
                        f"Shape mismatch for {var_name_str}: {output_var.shape} != {reference_var.shape}"
                    )
                    all_match = False
                    continue

                if self.mode == ComparisonMode.EXACT:
                    match = np.array_equal(output_var, reference_var)
                elif self.mode == ComparisonMode.RELATIVE:
                    mask = ~(np.isnan(output_var) | np.isnan(reference_var))
                    if np.any(mask):
                        reference_safe = np.where(
                            reference_var == 0, 1.0, reference_var
                        )
                        rel_diff = np.abs((output_var - reference_var) / reference_safe)
                        match = np.all(rel_diff[mask] < field_tolerance)
                    else:
                        match = True
                elif self.mode == ComparisonMode.ABSOLUTE:
                    mask = ~(np.isnan(output_var) | np.isnan(reference_var))
                    abs_diff = np.abs(output_var - reference_var)
                    match = np.all(abs_diff[mask] < field_tolerance)
                else:
                    match = False

                if not match:
                    logger.debug(
                        f"Variable {var_name_str} mismatch (tolerance={field_tolerance}, mode={self.mode.value})"
                    )
                    all_match = False
                    continue

                if self.mode == ComparisonMode.EXACT:
                    match = np.array_equal(output_var, reference_var)
                elif self.mode == ComparisonMode.RELATIVE:
                    mask = ~(np.isnan(output_var) | np.isnan(reference_var))
                    if np.any(mask):
                        reference_safe = np.where(
                            reference_var == 0, 1.0, reference_var
                        )
                        rel_diff = np.abs((output_var - reference_var) / reference_safe)
                        match = np.all(rel_diff[mask] < field_tolerance)
                    else:
                        match = True
                elif self.mode == ComparisonMode.ABSOLUTE:
                    mask = ~(np.isnan(output_var) | np.isnan(reference_var))
                    abs_diff = np.abs(output_var - reference_var)
                    match = np.all(abs_diff[mask] < field_tolerance)
                else:
                    match = False

                if not match:
                    logger.debug(
                        f"Variable {var_name} mismatch (tolerance={field_tolerance}, mode={self.mode.value})"
                    )
                    all_match = False

            return all_match
        finally:
            output_ds.close()
            reference_ds.close()

    def _compare_binary(self, output_file: Path, reference_file: Path) -> bool:
        """Compare binary files via checksum.

        Args:
            output_file: Test output binary file
            reference_file: Reference binary file

        Returns:
            True if checksums match
        """
        try:
            output_hash = self._compute_sha256(output_file)
            reference_hash = self._compute_sha256(reference_file)

            match = output_hash == reference_hash
            if not match:
                logger.debug(
                    f"Binary mismatch: {output_file.name} "
                    f"(output: {output_hash[:8]}... != ref: {reference_hash[:8]}...)"
                )
            return match
        except Exception as e:
            logger.error(f"Failed to compare binary files: {e}")
            return False

    def _compare_text(self, output_file: Path, reference_file: Path) -> bool:
        """Compare text files line by line.

        Args:
            output_file: Test output text file
            reference_file: Reference text file

        Returns:
            True if files match
        """
        try:
            with open(output_file, "r") as f_out, open(reference_file, "r") as f_ref:
                output_lines = f_out.readlines()
                reference_lines = f_ref.readlines()

            if len(output_lines) != len(reference_lines):
                logger.debug(
                    f"Line count mismatch: {output_file.name} "
                    f"({len(output_lines)} != {len(reference_lines)})"
                )
                return False

            for i, (out_line, ref_line) in enumerate(
                zip(output_lines, reference_lines)
            ):
                if out_line != ref_line:
                    logger.debug(f"Line {i + 1} mismatch in {output_file.name}")
                    return False

            return True
        except Exception as e:
            logger.error(f"Failed to compare text files: {e}")
            return False

    def _compute_sha256(self, file_path: Path) -> str:
        """Compute SHA256 hash of file.

        Args:
            file_path: Path to file

        Returns:
            Hexadecimal hash string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def generate_report(
        self,
        output_dir: Path,
        reference_dir: Path,
        validation_report: ValidationReport,
    ) -> str:
        """Generate human-readable comparison report.

        Args:
            output_dir: Directory containing test outputs
            reference_dir: Directory containing reference outputs
            validation_report: ValidationReport from validation run

        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 70)
        lines.append("VALIDATION REPORT")
        lines.append("=" * 70)
        lines.append(f"Output Directory:    {output_dir}")
        lines.append(f"Reference Directory: {reference_dir}")
        lines.append(f"Comparison Mode:     {self.mode.value}")
        lines.append(f"Default Tolerance:   {self.tolerance}")

        if self.field_tolerances:
            lines.append("Field-Specific Tolerances:")
            for field, tol in self.field_tolerances.items():
                lines.append(f"  {field}: {tol}")

        lines.append("")
        lines.append(f"Files Compared: {validation_report.files_compared}")
        lines.append(f"Files Matched:  {validation_report.files_matched}")

        if validation_report.is_valid():
            lines.append("")
            lines.append("✓ VALIDATION PASSED - All files matched")
        else:
            lines.append("")
            lines.append("✗ VALIDATION FAILED")
            lines.append("")
            lines.append("Differences:")
            for diff in validation_report.differences:
                lines.append(f"  - {diff}")

        lines.append("=" * 70)

        return "\n".join(lines)
