"""Input file management for WW3 regression tests.

This module provides functionality to discover required input files from
test configurations and download them from the NOAA WW3 repository.
"""

import logging
import re
from pathlib import Path
from typing import List, Set, Optional
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
import yaml


logger = logging.getLogger(__name__)


# Base URL for NOAA WW3 repository raw files
NOAA_WW3_RAW_URL = "https://raw.githubusercontent.com/NOAA-EMC/WW3/develop/regtests"


class InputFileManager:
    """Manages input file discovery and downloading for WW3 tests.

    This class handles:
    1. Parsing YAML configs to find input file references
    2. Checking if input files exist locally
    3. Downloading missing files from NOAA WW3 repository

    Example:
        >>> manager = InputFileManager()
        >>> test_case = TestCase(config_path="regtests/ww3_tp2.4/rompy_ww3_tp2_4.yaml")
        >>> missing = manager.get_missing_inputs(test_case)
        >>> if missing:
        ...     manager.download_inputs(test_case)
    """

    def __init__(self, base_url: str = NOAA_WW3_RAW_URL):
        """Initialize input file manager.

        Args:
            base_url: Base URL for NOAA WW3 repository
        """
        self.base_url = base_url

    def extract_input_references(self, config: dict) -> Set[str]:
        """Extract input file paths from YAML configuration.

        Scans the config dict recursively looking for 'source' fields
        that reference input files.

        Args:
            config: Parsed YAML configuration dictionary

        Returns:
            Set of input file paths referenced in config
        """
        input_files = set()

        def _scan_value(value):
            """Recursively scan value for input references."""
            if isinstance(value, dict):
                # Check if this is a data_blob with a source
                if value.get("model_type") in ("data_blob", "data_link"):
                    source = value.get("source")
                    if source and isinstance(source, str):
                        # Only include relative paths that point to input files
                        if (
                            "input/" in source
                            or source.endswith(".dat")
                            or source.endswith(".list")
                        ):
                            input_files.add(source)

                # Continue scanning nested dicts
                for k, v in value.items():
                    _scan_value(v)

            elif isinstance(value, list):
                for item in value:
                    _scan_value(item)

        _scan_value(config)
        return input_files

    def get_required_inputs(self, test_case) -> List[Path]:
        """Get list of required input files for a test case.

        Parses the test's YAML config to find all input file references.

        Args:
            test_case: TestCase instance

        Returns:
            List of Path objects for required input files
        """
        try:
            config = test_case.load_config()
        except Exception as e:
            logger.warning(f"Could not load config for {test_case.name}: {e}")
            return []

        # Extract input references from config
        input_refs = self.extract_input_references(config)

        # Convert to absolute paths
        input_files = []
        for ref in input_refs:
            # Handle both absolute and relative paths
            if ref.startswith("regtests/"):
                # Path relative to repo root
                path = Path(ref)
            elif ref.startswith("/"):
                # Absolute path
                path = Path(ref)
            else:
                # Relative to test directory
                path = test_case.test_dir / ref

            input_files.append(path)

        return input_files

    def get_missing_inputs(self, test_case) -> List[Path]:
        """Check which required input files are missing.

        Args:
            test_case: TestCase instance

        Returns:
            List of missing input file paths
        """
        required = self.get_required_inputs(test_case)
        missing = [p for p in required if not p.exists()]

        if missing:
            logger.debug(
                f"Missing inputs for {test_case.name}: {[p.name for p in missing]}"
            )

        return missing

    def download_file(self, url: str, dest_path: Path) -> bool:
        """Download a single file from URL.

        Args:
            url: URL to download from
            dest_path: Destination path for the file

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.debug(f"Downloading {url} -> {dest_path}")

            # Create parent directory if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Download file
            with urlopen(url, timeout=60) as response:
                dest_path.write_bytes(response.read())

            logger.debug(f"Successfully downloaded {dest_path.name}")
            return True

        except HTTPError as e:
            logger.error(f"HTTP error downloading {url}: {e.code}")
            return False
        except URLError as e:
            logger.error(f"URL error downloading {url}: {e.reason}")
            return False
        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            return False

    def download_inputs(self, test_case, dry_run: bool = False) -> dict:
        """Download missing input files for a test case.

        Args:
            test_case: TestCase instance
            dry_run: If True, only report what would be downloaded

        Returns:
            Dictionary with 'downloaded', 'failed', and 'skipped' lists
        """
        missing = self.get_missing_inputs(test_case)

        if not missing:
            logger.debug(f"All inputs present for {test_case.name}")
            return {"downloaded": [], "failed": [], "skipped": []}

        results = {"downloaded": [], "failed": [], "skipped": []}

        logger.info(f"Downloading {len(missing)} input files for {test_case.name}")

        for local_path in missing:
            # Construct URL from local path
            # Convert local path like "regtests/ww3_tp2.4/input/depth.dat"
            # to URL like "https://raw.githubusercontent.com/.../regtests/ww3_tp2.4/input/depth.dat"

            # Try to find the regtests component in the path
            parts = local_path.parts
            try:
                regtests_idx = parts.index("regtests")
                # Skip the 'regtests' part itself since base_url already includes it
                relative_path = "/".join(parts[regtests_idx + 1 :])
            except ValueError:
                # If 'regtests' not in path, use the filename only
                # This handles cases where path is relative to test dir
                relative_path = f"{test_case.name}/input/{local_path.name}"

            url = f"{self.base_url}/{relative_path}"

            if dry_run:
                logger.info(f"Would download: {url} -> {local_path}")
                results["skipped"].append(str(local_path))
                continue

            if self.download_file(url, local_path):
                results["downloaded"].append(str(local_path))
            else:
                results["failed"].append(str(local_path))

        return results

    def ensure_inputs(self, test_case, dry_run: bool = False) -> bool:
        """Ensure all input files are available for a test case.

        Downloads any missing input files. Returns True if all inputs
        are available (or were successfully downloaded).

        Args:
            test_case: TestCase instance
            dry_run: If True, only report what would be downloaded

        Returns:
            True if all inputs are available, False otherwise
        """
        results = self.download_inputs(test_case, dry_run=dry_run)

        if results["failed"]:
            logger.error(
                f"Failed to download {len(results['failed'])} files for {test_case.name}"
            )
            return False

        if results["downloaded"]:
            logger.info(
                f"Downloaded {len(results['downloaded'])} files for {test_case.name}"
            )

        return True
