#!/usr/bin/env python3
"""
Test script to verify namelist comparison functionality.

This script tests the NamelistComparator class by:
1. Comparing two identical namelists (should match)
2. Comparing two different namelists (should show diff)
3. Testing the download functionality
"""

import sys
from pathlib import Path

# Add regtests to path
sys.path.insert(0, str(Path(__file__).parent.parent / "regtests"))

from regtests.runner import NamelistComparator


def test_identical_namelists():
    """Test comparison of identical namelists."""
    print("=" * 70)
    print("Test 1: Comparing identical namelists")
    print("=" * 70)

    comparator = NamelistComparator()

    # Use the same file for both generated and reference
    ref_nml = Path(__file__).parent.parent / "tests" / "reference_nmls" / "ww3_shel.nml"

    diff = comparator.compare_namelists(
        generated_path=ref_nml,
        reference_path=ref_nml,
        namelist_name="ww3_shel.nml",
    )

    print(f"Namelist: {diff.namelist_name}")
    print(f"Match: {diff.is_match}")
    print("Expected: True")

    if diff.is_match:
        print("✓ Test 1 PASSED")
        return True
    else:
        print("✗ Test 1 FAILED")
        return False


def test_different_namelists():
    """Test comparison of different namelists."""
    print("\n" + "=" * 70)
    print("Test 2: Comparing different namelists")
    print("=" * 70)

    comparator = NamelistComparator()

    # Compare two different namelist files
    shel_nml = (
        Path(__file__).parent.parent / "tests" / "reference_nmls" / "ww3_shel.nml"
    )
    grid_nml = (
        Path(__file__).parent.parent / "tests" / "reference_nmls" / "ww3_grid.nml"
    )

    diff = comparator.compare_namelists(
        generated_path=shel_nml,
        reference_path=grid_nml,
        namelist_name="comparison.nml",
    )

    print(f"Namelist: {diff.namelist_name}")
    print(f"Match: {diff.is_match}")
    print("Expected: False")

    if not diff.is_match and diff.diff_content:
        print("✓ Test 2 PASSED (correctly detected differences)")
        # Show first few lines of diff
        print("\nDiff preview (first 10 lines):")
        print("\n".join(diff.diff_content.split("\n")[:10]))
        return True
    else:
        print("✗ Test 2 FAILED")
        return False


def test_namelist_report():
    """Test the full namelist comparison report."""
    print("\n" + "=" * 70)
    print("Test 3: Generating comparison report")
    print("=" * 70)

    comparator = NamelistComparator()

    # Use the test reference directory
    test_dir = Path(__file__).parent.parent / "tests" / "reference_nmls"

    report = comparator.compare_test_namelists(
        test_name="test",
        generated_dir=test_dir,
        download_missing=False,  # Don't try to download for this test
    )

    print(f"Test: {report.test_name}")
    print(f"Namelists compared: {report.namelists_compared}")
    print(f"Namelists matched: {report.namelists_matched}")
    print(f"All valid: {report.is_valid()}")

    # Generate and print the report
    report_text = report.generate_report()
    print("\nReport preview:")
    print(report_text[:500] + "..." if len(report_text) > 500 else report_text)

    if report.namelists_compared > 0:
        print("✓ Test 3 PASSED")
        return True
    else:
        print("✗ Test 3 FAILED (no namelists found)")
        return False


def test_missing_reference():
    """Test handling of missing reference namelist."""
    print("\n" + "=" * 70)
    print("Test 4: Handling missing reference namelist")
    print("=" * 70)

    comparator = NamelistComparator()

    shel_nml = (
        Path(__file__).parent.parent / "tests" / "reference_nmls" / "ww3_shel.nml"
    )
    nonexistent = Path("/nonexistent/path/ww3_shel.nml")

    diff = comparator.compare_namelists(
        generated_path=shel_nml,
        reference_path=nonexistent,
        namelist_name="ww3_shel.nml",
    )

    print(f"Namelist: {diff.namelist_name}")
    print(f"Match: {diff.is_match}")
    print("Expected: True (should not fail when reference is missing)")

    if diff.is_match:
        print("✓ Test 4 PASSED")
        return True
    else:
        print("✗ Test 4 FAILED")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("NAMELIST COMPARATOR TEST SUITE")
    print("=" * 70)

    results = []
    results.append(("Identical namelists", test_identical_namelists()))
    results.append(("Different namelists", test_different_namelists()))
    results.append(("Namelist report", test_namelist_report()))
    results.append(("Missing reference", test_missing_reference()))

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")

    print(f"\n{passed}/{total} tests passed")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
