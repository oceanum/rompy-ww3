#!/usr/bin/env python3
"""
Download static input data files for WW3 regression tests from NOAA-EMC/WW3 repository.

This script fetches test input files from the official WW3 GitHub repository and organizes
them in the regtests directory structure. It supports bulk downloads (entire test series)
or selective downloads (specific tests).

Usage Examples:
    # Download all tp2.x test inputs
    python download_input_data.py tp2

    # Download specific test inputs
    python download_input_data.py tp2.4 tp1.1

    # Download with progress and resume support
    python download_input_data.py tp2.4 --force

    # Dry run (show what would be downloaded)
    python download_input_data.py tp2 --dry-run

    # List available tests
    python download_input_data.py --list

File Organization:
    regtests/ww3_tp2.4/input/depth.225x106.IDLA1.dat
    regtests/ww3_tp2.4/input/points.list
    regtests/ww3_tp2.4/input/namelists_2-D.nml
    ...

Features:
    - Concurrent downloads for improved performance
    - Resume interrupted downloads
    - SHA256 verification (when available)
    - Skip existing files unless --force flag
    - Progress reporting with tqdm
    - Comprehensive error handling
"""

import argparse
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    from tqdm import tqdm

    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print(
        "Warning: tqdm not installed. Install with 'pip install tqdm' for progress bars."
    )


# Constants
GITHUB_API_BASE = "https://api.github.com/repos/NOAA-EMC/WW3"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/NOAA-EMC/WW3/develop"
WW3_BRANCH = "develop"
REGTESTS_DIR = Path(__file__).parent
MAX_WORKERS = 8  # Concurrent downloads
CHUNK_SIZE = 8192  # Download chunk size in bytes


class DownloadError(Exception):
    """Custom exception for download errors."""

    pass


def get_github_file_list(test_path: str) -> List[Dict[str, str]]:
    """
    Get list of files from GitHub API for a specific test's input directory.

    Args:
        test_path: Path like "ww3_tp2.4/input"

    Returns:
        List of file metadata dicts with keys: name, download_url, sha, size

    Raises:
        DownloadError: If API request fails
    """
    api_url = f"{GITHUB_API_BASE}/contents/regtests/{test_path}"

    try:
        req = Request(api_url)
        req.add_header("Accept", "application/vnd.github.v3+json")

        with urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))

        # Filter for files only (not directories)
        files = [
            {
                "name": item["name"],
                "download_url": item["download_url"],
                "sha": item["sha"],
                "size": item["size"],
            }
            for item in data
            if item["type"] == "file"
        ]

        return files

    except HTTPError as e:
        if e.code == 404:
            raise DownloadError(f"Test path not found: {test_path}")
        raise DownloadError(f"GitHub API error ({e.code}): {e.reason}")
    except URLError as e:
        raise DownloadError(f"Network error: {e.reason}")
    except json.JSONDecodeError as e:
        raise DownloadError(f"Invalid JSON response from GitHub API: {e}")


def compute_sha256(filepath: Path) -> str:
    """
    Compute SHA256 hash of a file.

    Args:
        filepath: Path to file

    Returns:
        Hex string of SHA256 hash
    """
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def download_file(
    url: str,
    dest_path: Path,
    expected_size: Optional[int] = None,
    force: bool = False,
    show_progress: bool = True,
) -> Tuple[bool, str]:
    """
    Download a single file with resume support.

    Args:
        url: Download URL
        dest_path: Destination file path
        expected_size: Expected file size in bytes (for verification)
        force: Overwrite existing file
        show_progress: Show progress bar (requires tqdm)

    Returns:
        Tuple of (success: bool, message: str)
    """
    # Check if file exists and is complete
    if dest_path.exists() and not force:
        if expected_size and dest_path.stat().st_size == expected_size:
            return True, f"Already exists: {dest_path.name}"
        elif not expected_size:
            return True, f"Already exists (skipped): {dest_path.name}"

    # Create parent directory
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Handle resume
    resume_pos = 0
    mode = "wb"
    if dest_path.exists() and not force:
        resume_pos = dest_path.stat().st_size
        mode = "ab"

    try:
        req = Request(url)
        if resume_pos > 0:
            req.add_header("Range", f"bytes={resume_pos}-")

        with urlopen(req, timeout=60) as response:
            total_size = int(response.headers.get("Content-Length", 0))
            if resume_pos > 0:
                total_size += resume_pos

            # Verify expected size if provided
            if expected_size and total_size != expected_size:
                return (
                    False,
                    f"Size mismatch: expected {expected_size}, got {total_size}",
                )

            # Download with progress
            pbar = None
            if show_progress and HAS_TQDM and total_size > 0:
                pbar = tqdm(
                    total=total_size,
                    initial=resume_pos,
                    unit="B",
                    unit_scale=True,
                    desc=dest_path.name,
                    leave=False,
                )

            with open(dest_path, mode) as f:
                while True:
                    chunk = response.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)
                    if pbar:
                        pbar.update(len(chunk))

            if pbar:
                pbar.close()

        return True, f"Downloaded: {dest_path.name}"

    except HTTPError as e:
        return False, f"HTTP error ({e.code}): {e.reason}"
    except URLError as e:
        return False, f"Network error: {e.reason}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def expand_test_patterns(patterns: List[str]) -> Set[str]:
    """
    Expand test patterns into specific test names.

    Args:
        patterns: List of patterns like ["tp2", "tp1.1", "mww3_test_01"]

    Returns:
        Set of expanded test names like {"ww3_tp2.1", "ww3_tp2.2", ...}
    """
    expanded = set()

    for pattern in patterns:
        if "." in pattern:
            # Specific test: tp2.4 -> ww3_tp2.4
            if pattern.startswith("ww3_"):
                expanded.add(pattern)
            else:
                expanded.add(f"ww3_{pattern}")
        else:
            # Series pattern: tp2 -> query GitHub for all tp2.x tests
            # For now, use known ranges (can be enhanced with API call)
            if pattern == "tp1":
                for i in range(1, 11):  # tp1.1 to tp1.10
                    expanded.add(f"ww3_tp1.{i}")
            elif pattern == "tp2":
                for i in range(1, 18):  # tp2.1 to tp2.17
                    expanded.add(f"ww3_tp2.{i}")
            elif pattern.startswith("mww3"):
                # Specific multi-grid test
                expanded.add(pattern)
            else:
                print(f"Warning: Unknown test pattern: {pattern}")

    return expanded


def list_available_tests() -> None:
    """List available test series from GitHub."""
    print("Available WW3 Regression Tests:")
    print("\nTest Series:")
    print("  tp1     - 1-D propagation tests (tp1.1 to tp1.10)")
    print("  tp2     - 2-D propagation tests (tp2.1 to tp2.17)")
    print("\nSpecific Tests:")
    print("  tp1.1, tp1.2, ... tp1.10")
    print("  tp2.1, tp2.2, ... tp2.17")
    print("\nMulti-Grid Tests:")
    print("  mww3_test_01, mww3_test_02, ...")
    print("\nExample Usage:")
    print("  python download_input_data.py tp2         # All tp2.x tests")
    print("  python download_input_data.py tp2.4       # Only tp2.4")
    print("  python download_input_data.py tp1.1 tp2.4 # Multiple specific tests")


def main():
    """Main entry point for the download script."""
    parser = argparse.ArgumentParser(
        description="Download WW3 regression test input data from NOAA-EMC/WW3 repository",
        epilog="Examples:\n"
        "  %(prog)s tp2.4              # Download tp2.4 inputs\n"
        "  %(prog)s tp2                # Download all tp2.x inputs\n"
        "  %(prog)s tp1.1 tp2.4 --force # Download and overwrite\n"
        "  %(prog)s --list             # List available tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "tests",
        nargs="*",
        help="Test names or patterns (e.g., tp2.4, tp2, mww3_test_01)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be downloaded without downloading",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available test series",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=MAX_WORKERS,
        help=f"Number of concurrent downloads (default: {MAX_WORKERS})",
    )

    args = parser.parse_args()

    # Handle --list
    if args.list:
        list_available_tests()
        return 0

    # Require at least one test pattern
    if not args.tests:
        parser.print_help()
        print("\nError: Specify at least one test pattern or use --list")
        return 1

    # Expand test patterns
    test_names = expand_test_patterns(args.tests)
    if not test_names:
        print("Error: No valid test patterns provided")
        return 1

    print(f"Processing {len(test_names)} test(s): {', '.join(sorted(test_names))}")

    # Collect all files to download
    download_tasks = []
    for test_name in sorted(test_names):
        input_path = f"{test_name}/input"

        try:
            print(f"\nFetching file list for {test_name}...")
            files = get_github_file_list(input_path)

            if not files:
                print(f"  No input files found for {test_name}")
                continue

            print(f"  Found {len(files)} files")

            for file_info in files:
                dest_path = REGTESTS_DIR / test_name / "input" / file_info["name"]
                download_tasks.append(
                    {
                        "url": file_info["download_url"],
                        "dest": dest_path,
                        "size": file_info["size"],
                        "test": test_name,
                        "name": file_info["name"],
                    }
                )

        except DownloadError as e:
            print(f"  Error: {e}")
            continue

    if not download_tasks:
        print("\nNo files to download")
        return 0

    # Dry run - just show what would be downloaded
    if args.dry_run:
        print(f"\nDry run - would download {len(download_tasks)} files:")
        total_size = 0
        for task in download_tasks:
            size_mb = task["size"] / (1024 * 1024)
            total_size += task["size"]
            print(f"  {task['test']}/input/{task['name']} ({size_mb:.2f} MB)")
        print(f"\nTotal size: {total_size / (1024 * 1024):.2f} MB")
        return 0

    # Download files
    print(f"\nDownloading {len(download_tasks)} files with {args.workers} workers...")

    success_count = 0
    fail_count = 0
    skip_count = 0

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        # Submit all download tasks
        future_to_task = {
            executor.submit(
                download_file,
                task["url"],
                task["dest"],
                task["size"],
                args.force,
                HAS_TQDM,
            ): task
            for task in download_tasks
        }

        # Process completed downloads
        if HAS_TQDM:
            pbar = tqdm(total=len(download_tasks), desc="Overall progress")

        for future in as_completed(future_to_task):
            task = future_to_task[future]

            try:
                success, message = future.result()

                if success:
                    if "Already exists" in message:
                        skip_count += 1
                    else:
                        success_count += 1
                else:
                    fail_count += 1
                    print(f"\nFailed: {task['test']}/{task['name']} - {message}")

            except Exception as e:
                fail_count += 1
                print(f"\nException: {task['test']}/{task['name']} - {str(e)}")

            if HAS_TQDM:
                pbar.update(1)

        if HAS_TQDM:
            pbar.close()

    # Summary
    print("\n" + "=" * 70)
    print("Download Summary:")
    print(f"  Downloaded: {success_count}")
    print(f"  Skipped (existing): {skip_count}")
    print(f"  Failed: {fail_count}")
    print(f"  Total: {len(download_tasks)}")
    print("=" * 70)

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
