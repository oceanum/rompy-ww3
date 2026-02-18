#!/usr/bin/env python3
"""
Comprehensive diagnostic report for WW3 namelist comparison.
"""

import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent / "regtests"))

from regtests.runner import NamelistComparator


def generate_report():
    """Generate comprehensive diagnostic report."""

    print("=" * 80)
    print("WW3 NAMELIST COMPARISON - COMPREHENSIVE DIAGNOSTIC REPORT")
    print("=" * 80)
    print(f"Generated: {datetime.now().isoformat()}")
    print()

    # Find all test directories
    test_dirs = []
    base_paths = [
        Path("regtests/rompy_runs"),
        Path("rompy_runs"),
    ]

    for base_path in base_paths:
        if base_path.exists():
            for d in base_path.iterdir():
                if d.is_dir() and any(d.glob("*.nml")):
                    test_name = (
                        d.name.replace("ww3_", "")
                        .replace("_regression", "")
                        .replace("_", ".")
                    )
                    if (test_name, d) not in test_dirs:
                        test_dirs.append((test_name, d))

    if not test_dirs:
        print("No generated namelists found!")
        return

    print(f"Found {len(test_dirs)} tests with generated namelists")
    print()

    # Analyze each test
    reports = {}
    mismatches = defaultdict(list)

    for test_name, test_dir in sorted(test_dirs):
        comparator = NamelistComparator()
        report = comparator.compare_test_namelists(
            test_name=test_name, generated_dir=test_dir, download_missing=True
        )
        reports[test_name] = report

        status = "✅ PASS" if report.is_valid() else "❌ FAIL"
        print(
            f"{status} {test_name:15s} {report.namelists_matched}/{report.namelists_compared} matched"
        )

        if not report.is_valid():
            for diff in report.get_mismatches():
                mismatches[diff.namelist_name].append(
                    {
                        "test": test_name,
                        "diff": diff.diff_content[:500]
                        if diff.diff_content
                        else "No reference",
                    }
                )

    # Summary statistics
    print()
    print("=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    total_tests = len(reports)
    passed_tests = sum(1 for r in reports.values() if r.is_valid())
    failed_tests = total_tests - passed_tests

    print(f"Total tests analyzed:    {total_tests}")
    print(
        f"Tests with all matches:  {passed_tests} ({100 * passed_tests / total_tests:.1f}%)"
    )
    print(
        f"Tests with mismatches:   {failed_tests} ({100 * failed_tests / total_tests:.1f}%)"
    )

    if failed_tests > 0:
        print()
        print("=" * 80)
        print("MISMATCH BREAKDOWN BY NAMELIST TYPE")
        print("=" * 80)
        for namelist_name, issues in sorted(
            mismatches.items(), key=lambda x: -len(x[1])
        ):
            print(f"\n{namelist_name}: {len(issues)} test(s) affected")
            for issue in issues[:3]:  # Show first 3
                print(f"  - {issue['test']}")
            if len(issues) > 3:
                print(f"  ... and {len(issues) - 3} more")
    else:
        print()
        print("🎉 EXCELLENT! All namelists match NOAA reference files perfectly!")

    print()
    print("=" * 80)
    print("END OF REPORT")
    print("=" * 80)


if __name__ == "__main__":
    generate_report()
