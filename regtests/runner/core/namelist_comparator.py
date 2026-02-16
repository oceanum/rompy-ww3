"""Namelist comparison against NOAA reference files.

This module provides functionality to compare generated WW3 namelist files
against reference namelists from the NOAA WW3 repository.
"""

import logging
import re
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from difflib import unified_diff
import fnmatch


logger = logging.getLogger(__name__)

# Default WW3 release tag to use for reference lookups
DEFAULT_WW3_TAG = "6.07.1"

# Base URL for NOAA WW3 repository raw files (pinned to DEFAULT_WW3_TAG by default)
NOAA_WW3_RAW_URL = (
    f"https://raw.githubusercontent.com/NOAA-EMC/WW3/{DEFAULT_WW3_TAG}/regtests"
)

# Default namelist file patterns to compare
DEFAULT_NAMELIST_PATTERNS = [
    "ww3_shel.nml",
    "ww3_grid.nml",
    "ww3_multi.nml",
    "ww3_ounf.nml",
    "ww3_ounp.nml",
    "ww3_bounc.nml",
    "ww3_prnc.nml",
    "ww3_trnc.nml",
    "namelists.nml",
]


def _parse_grdset(test_name: str) -> Tuple[str, Optional[str]]:
    """Parse test name to extract base name and grdset.

    Args:
        test_name: Name of the test (e.g., 'mww3_test_02_grdset_a')

    Returns:
        Tuple of (base_test_name, grdset_name or None)
        Example: ('mww3_test_02', 'grdset_a') or ('tp1.1', None)
    """
    grdset_match = re.match(r"(.+)_(grdset_[a-z0-9]+)$", test_name)
    if grdset_match:
        return grdset_match.group(1), grdset_match.group(2)
    return test_name, None


class NamelistDiff:
    """Represents a difference between two namelist files.

    Attributes:
        namelist_name: Name of the namelist file (e.g., 'ww3_shel.nml')
        generated_path: Path to the generated namelist
        reference_path: Path to the reference namelist
        diff_content: Unified diff content showing differences
        is_match: Whether the files match
    """

    def __init__(
        self,
        namelist_name: str,
        generated_path: Path,
        reference_path: Path,
        diff_content: str,
        is_match: bool,
    ):
        self.namelist_name = namelist_name
        self.generated_path = generated_path
        self.reference_path = reference_path
        self.diff_content = diff_content
        self.is_match = is_match

    def __repr__(self) -> str:
        status = "✓" if self.is_match else "✗"
        return f"NamelistDiff({status} {self.namelist_name})"


class NamelistComparisonReport:
    """Report from comparing generated namelists against references.

    Attributes:
        test_name: Name of the test being validated
        namelists_compared: Number of namelist files compared
        namelists_matched: Number of namelist files that matched
        differences: List of NamelistDiff objects with comparison details
    """

    def __init__(
        self,
        test_name: str,
        namelists_compared: int,
        namelists_matched: int,
        differences: List[NamelistDiff],
    ):
        self.test_name = test_name
        self.namelists_compared = namelists_compared
        self.namelists_matched = namelists_matched
        self.differences = differences

    def is_valid(self) -> bool:
        """Check if all namelists matched references."""
        return self.namelists_compared == self.namelists_matched

    def get_mismatches(self) -> List[NamelistDiff]:
        """Get list of namelists that don't match."""
        return [diff for diff in self.differences if not diff.is_match]

    def generate_report(self) -> str:
        """Generate human-readable comparison report.

        Returns:
            Formatted report string with diff details
        """
        lines = []
        lines.append("=" * 70)
        lines.append(f"NAMELIST COMPARISON REPORT: {self.test_name}")
        lines.append("=" * 70)
        lines.append(f"Namelists Compared: {self.namelists_compared}")
        lines.append(f"Namelists Matched:  {self.namelists_matched}")

        if self.is_valid():
            lines.append("")
            lines.append("✓ ALL NAMELISTS MATCHED")
        else:
            lines.append("")
            lines.append(f"✗ {len(self.get_mismatches())} NAMELIST(S) DIFFER")
            lines.append("")

            for diff in self.get_mismatches():
                lines.append(f"--- {diff.namelist_name} ---")
                if diff.diff_content:
                    lines.append(diff.diff_content)
                else:
                    lines.append("  (file missing or empty)")
                lines.append("")

        lines.append("=" * 70)
        return "\n".join(lines)


class NamelistComparator:
    """Compares generated WW3 namelist files against NOAA reference files.

    This class handles:
    1. Downloading reference namelists from NOAA WW3 repository
    2. Comparing generated namelists against references
    3. Generating detailed diff reports

    Example:
        >>> comparator = NamelistComparator()
        >>> report = comparator.compare_test_namelists(
        ...     test_name="tp1.1",
        ...     generated_dir=Path("outputs/tp1.1"),
        ... )
        >>> if not report.is_valid():
        ...     print(report.generate_report())
    """

    def __init__(
        self,
        base_url: str = None,
        reference_dir: Optional[Path] = None,
        namelist_patterns: Optional[List[str]] = None,
        normalize_whitespace: bool = True,
        ignore_comments: bool = False,
        ww3_tag: str = DEFAULT_WW3_TAG,
    ):
        """Initialize namelist comparator.

        Args:
            base_url: Base URL for NOAA WW3 repository
            reference_dir: Local directory to cache reference namelists
            namelist_patterns: List of namelist file patterns to compare
            normalize_whitespace: Whether to normalize whitespace in comparison
            ignore_comments: Whether to ignore comment lines in comparison
        """
        # Allow overriding the WW3 tag or the full base_url
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = (
                f"https://raw.githubusercontent.com/NOAA-EMC/WW3/{ww3_tag}/regtests"
            )
        self.reference_dir = reference_dir or Path(".reference_namelists")
        self.namelist_patterns = namelist_patterns or DEFAULT_NAMELIST_PATTERNS
        self.normalize_whitespace = normalize_whitespace
        self.ignore_comments = ignore_comments

    def get_reference_namelist_path(self, test_name: str, namelist_file: str) -> Path:
        """Get local path for caching a reference namelist.

        Args:
            test_name: Name of the test (e.g., 'tp1.1' or 'mww3_test_02_grdset_a')
            namelist_file: Name of the namelist file (e.g., 'ww3_shel.nml')

        Returns:
            Path to local reference namelist file
        """
        base_name, grdset = _parse_grdset(test_name)
        # The NOAA repo uses names like 'mww3_test_01' or 'ww3_tp1.1'.
        # Avoid adding an extra 'ww3_' prefix when the base_name already
        # contains the expected prefix (e.g., 'mww3_test_01' or 'ww3_...').
        if base_name.startswith("mww3") or base_name.startswith("ww3_"):
            repo_test_name = base_name
        else:
            repo_test_name = f"ww3_{base_name}"

        if grdset:
            return (
                self.reference_dir / repo_test_name / "input" / grdset / namelist_file
            )
        return self.reference_dir / repo_test_name / namelist_file

    def get_reference_url(self, test_name: str, namelist_file: str) -> str:
        """Construct URL for downloading reference namelist.

        Args:
            test_name: Name of the test (e.g., 'tp1.1' or 'mww3_test_02_grdset_a')
            namelist_file: Name of the namelist file (e.g., 'ww3_shel.nml')

        Returns:
            URL to download the reference namelist
        """
        base_name, grdset = _parse_grdset(test_name)
        # See note in get_reference_namelist_path: don't double-prefix names
        if base_name.startswith("mww3") or base_name.startswith("ww3_"):
            repo_test_name = base_name
        else:
            repo_test_name = f"ww3_{base_name}"

        if grdset:
            return f"{self.base_url}/{repo_test_name}/input/{grdset}/{namelist_file}"
        return f"{self.base_url}/{repo_test_name}/{namelist_file}"

    def download_reference_namelist(
        self, test_name: str, namelist_file: str, force: bool = False
    ) -> Optional[Path]:
        """Download reference namelist from NOAA repository.

        Args:
            test_name: Name of the test
            namelist_file: Name of the namelist file
            force: If True, re-download even if file exists

        Returns:
            Path to downloaded file, or None if download failed
        """
        local_path = self.get_reference_namelist_path(test_name, namelist_file)

        # Check if already cached
        if local_path.exists() and not force:
            logger.debug(f"Using cached reference: {local_path}")
            return local_path

        # Download from NOAA
        url = self.get_reference_url(test_name, namelist_file)
        logger.debug(f"Downloading reference namelist: {url}")

        try:
            # Create parent directory
            local_path.parent.mkdir(parents=True, exist_ok=True)

            # Download file
            with urlopen(url, timeout=60) as response:
                content = response.read()
                if content:
                    local_path.write_bytes(content)
                    logger.debug(f"Downloaded {namelist_file} to {local_path}")
                    return local_path
                else:
                    logger.warning(f"Empty content from {url}")
                    return None

        except HTTPError as e:
            if e.code == 404:
                logger.debug(f"Reference namelist not found: {url}")
            else:
                logger.warning(f"HTTP error downloading {url}: {e.code}")
            return None
        except URLError as e:
            logger.warning(f"URL error downloading {url}: {e.reason}")
            return None
        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            return None

    def download_all_references(
        self, test_name: str, force: bool = False
    ) -> Dict[str, Optional[Path]]:
        """Download all reference namelists for a test.

        Args:
            test_name: Name of the test
            force: If True, re-download even if files exist

        Returns:
            Dictionary mapping namelist names to paths (or None if failed)
        """
        results = {}
        for pattern in self.namelist_patterns:
            # Handle glob patterns
            if "*" in pattern or "?" in pattern:
                # For glob patterns, we need to check what files exist
                # For now, just try the pattern as-is
                path = self.download_reference_namelist(test_name, pattern, force)
                results[pattern] = path
            else:
                path = self.download_reference_namelist(test_name, pattern, force)
                results[pattern] = path

        return results

    def _normalize_line(self, line: str) -> str:
        """Normalize a line for comparison.

        Args:
            line: Raw line from namelist

        Returns:
            Normalized line
        """
        # Remove comments if configured
        if self.ignore_comments:
            # Remove everything after !
            if "!" in line:
                line = line[: line.index("!")]

        # Normalize whitespace
        if self.normalize_whitespace:
            # Strip leading/trailing whitespace
            line = line.strip()
            # Normalize internal whitespace
            line = re.sub(r"\s+", " ", line)

        return line

    def _read_namelist_lines(self, file_path: Path) -> List[str]:
        """Read and normalize namelist file.

        Args:
            file_path: Path to namelist file

        Returns:
            List of normalized lines
        """
        if not file_path.exists():
            return []

        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return []

        # Normalize each line
        normalized = []
        for line in lines:
            norm_line = self._normalize_line(line)
            # Skip empty lines after normalization
            if norm_line or not self.normalize_whitespace:
                normalized.append(norm_line)

        return normalized

    def compare_namelists(
        self,
        generated_path: Path,
        reference_path: Path,
        namelist_name: str,
    ) -> NamelistDiff:
        """Compare two namelist files and generate diff.

        Args:
            generated_path: Path to generated namelist
            reference_path: Path to reference namelist
            namelist_name: Name of the namelist for reporting

        Returns:
            NamelistDiff with comparison results
        """
        # Check if files exist
        if not generated_path.exists():
            logger.warning(f"Generated namelist not found: {generated_path}")
            return NamelistDiff(
                namelist_name=namelist_name,
                generated_path=generated_path,
                reference_path=reference_path,
                diff_content="Generated namelist file not found",
                is_match=False,
            )

        if not reference_path.exists():
            logger.debug(f"Reference namelist not found: {reference_path}")
            # Treat missing reference as a mismatch so users become aware that
            # the expected NOAA reference file is not present for the pinned tag.
            return NamelistDiff(
                namelist_name=namelist_name,
                generated_path=generated_path,
                reference_path=reference_path,
                diff_content="Reference namelist file not found (not in NOAA repo)",
                is_match=False,
            )

        # Read and normalize files
        generated_lines = self._read_namelist_lines(generated_path)
        reference_lines = self._read_namelist_lines(reference_path)

        # Compare
        if generated_lines == reference_lines:
            return NamelistDiff(
                namelist_name=namelist_name,
                generated_path=generated_path,
                reference_path=reference_path,
                diff_content="",
                is_match=True,
            )

        # Generate unified diff
        diff = unified_diff(
            reference_lines,
            generated_lines,
            fromfile=f"reference/{namelist_name}",
            tofile=f"generated/{namelist_name}",
            lineterm="",
        )

        diff_content = "\n".join(diff)

        return NamelistDiff(
            namelist_name=namelist_name,
            generated_path=generated_path,
            reference_path=reference_path,
            diff_content=diff_content,
            is_match=False,
        )

    def find_generated_namelists(self, generated_dir: Path) -> List[Path]:
        """Find all namelist files in generated directory.

        Args:
            generated_dir: Directory containing generated namelists

        Returns:
            List of paths to namelist files
        """
        namelists = []

        for pattern in self.namelist_patterns:
            if "*" in pattern or "?" in pattern:
                # Glob pattern
                matches = list(generated_dir.glob(pattern))
                namelists.extend(matches)
            else:
                # Specific file
                path = generated_dir / pattern
                if path.exists():
                    namelists.append(path)

        return sorted(namelists)

    def compare_test_namelists(
        self,
        test_name: str,
        generated_dir: Path,
        download_missing: bool = True,
    ) -> NamelistComparisonReport:
        """Compare all namelists for a test against NOAA references.

        Args:
            test_name: Name of the test (e.g., 'tp1.1')
            generated_dir: Directory containing generated namelists
            download_missing: Whether to download missing references

        Returns:
            NamelistComparisonReport with all comparison results
        """
        logger.info(f"Comparing namelists for test: {test_name}")

        # Coerce generated_dir to Path and attempt to locate a generated
        # run directory if the exact path isn't present. Some runs include
        # grdset suffixes (e.g., ww3_mww3_test_02_grdset_a_regression).
        if not isinstance(generated_dir, Path):
            generated_dir = Path(generated_dir)

        if not generated_dir.exists():
            # Try to find a matching directory under rompy_runs
            candidate_root = Path("rompy_runs")
            pattern = f"ww3_{test_name}*"
            matches = (
                list(candidate_root.glob(pattern)) if candidate_root.exists() else []
            )
            if matches:
                # prefer the most-recently-modified match
                matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                generated_dir = matches[0]
                logger.info(
                    f"Using fallback generated dir for {test_name}: {generated_dir}"
                )

        # Find generated namelists
        generated_namelists = self.find_generated_namelists(generated_dir)

        if not generated_namelists:
            logger.warning(f"No namelists found in {generated_dir}")
            return NamelistComparisonReport(
                test_name=test_name,
                namelists_compared=0,
                namelists_matched=0,
                differences=[],
            )

        # Download references if needed
        if download_missing:
            self.download_all_references(test_name)

        # Compare each namelist
        differences = []
        namelists_compared = 0
        namelists_matched = 0

        for generated_path in generated_namelists:
            namelist_name = generated_path.name

            # Get reference path
            reference_path = self.get_reference_namelist_path(test_name, namelist_name)

            # Compare
            diff = self.compare_namelists(generated_path, reference_path, namelist_name)
            differences.append(diff)
            namelists_compared += 1

            if diff.is_match:
                namelists_matched += 1
                logger.debug(f"✓ {namelist_name} matches reference")
            else:
                logger.debug(f"✗ {namelist_name} differs from reference")

        logger.info(
            f"Namelist comparison complete: {namelists_matched}/{namelists_compared} matched"
        )

        return NamelistComparisonReport(
            test_name=test_name,
            namelists_compared=namelists_compared,
            namelists_matched=namelists_matched,
            differences=differences,
        )

    def validate_before_execution(
        self,
        test_name: str,
        generated_dir: Path,
        raise_on_mismatch: bool = False,
    ) -> bool:
        """Validate namelists before executing test.

        This is a convenience method for pre-execution validation.

        Args:
            test_name: Name of the test
            generated_dir: Directory containing generated namelists
            raise_on_mismatch: If True, raise exception on mismatch

        Returns:
            True if all namelists match or no references exist

        Raises:
            NamelistMismatchError: If raise_on_mismatch=True and mismatches found
        """
        report = self.compare_test_namelists(test_name, generated_dir)

        if not report.is_valid():
            mismatches = report.get_mismatches()
            message = f"Namelist validation failed for {test_name}: "
            message += f"{len(mismatches)}/{report.namelists_compared} differ"

            if raise_on_mismatch:
                raise NamelistMismatchError(message, report)

            logger.warning(message)
            return False

        return True


class NamelistMismatchError(Exception):
    """Exception raised when namelists don't match references.

    Attributes:
        message: Error message
        report: NamelistComparisonReport with full comparison details
    """

    def __init__(self, message: str, report: NamelistComparisonReport):
        super().__init__(message)
        self.report = report

    def get_diff_report(self) -> str:
        """Get full diff report."""
        return self.report.generate_report()
