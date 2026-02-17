#!/usr/bin/env python3
"""
Diagnostic script to analyze namelist differences between generated and NOAA references.

This script uses the NamelistComparator to:
1. Download NOAA reference namelists
2. Compare them against locally generated namelists
3. Generate a comprehensive diagnostic report
4. Identify common patterns in differences
"""

import sys
import argparse
from pathlib import Path
from collections import defaultdict

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "regtests"))

from regtests.runner import NamelistComparator
from regtests.runner.core.namelist_comparator import NamelistComparisonReport


def analyze_test(
    test_name: str, generated_dir: Path, verbose: bool = False
) -> NamelistComparisonReport:
    """Analyze a single test and return the comparison report."""
    comparator = NamelistComparator()

    if not generated_dir.exists():
        print(f"⚠️  Generated directory not found: {generated_dir}")
        return None

    # Find namelists
    namelists = comparator.find_generated_namelists(generated_dir)

    if not namelists:
        print(f"⚠️  No namelists found in {generated_dir}")
        return None

    if verbose:
        print(f"  Found {len(namelists)} namelist(s): {[n.name for n in namelists]}")

    # Compare
    report = comparator.compare_test_namelists(
        test_name=test_name,
        generated_dir=generated_dir,
        download_missing=True,
    )

    return report


def print_summary(reports: dict):
    """Print summary of all test analyses."""
    print("\n" + "=" * 80)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 80)

    total_tests = len(reports)
    tests_with_issues = sum(1 for r in reports.values() if r and not r.is_valid())
    tests_with_no_ref = sum(
        1 for r in reports.values() if r and r.namelists_compared == 0
    )

    print(f"\nTotal tests analyzed: {total_tests}")
    print(f"Tests with namelist differences: {tests_with_issues}")
    print(f"Tests with no generated namelists: {tests_with_no_ref}")

    if tests_with_issues == 0:
        print("\n✅ All namelists match NOAA references!")
        return

    # Analyze common issues
    issue_patterns = defaultdict(list)

    for test_name, report in reports.items():
        if not report or report.is_valid():
            continue

        for diff in report.get_mismatches():
            issue_patterns[diff.namelist_name].append(test_name)

    print("\n📊 Common Issues by Namelist Type:")
    print("-" * 80)
    for namelist_name, test_list in sorted(
        issue_patterns.items(), key=lambda x: -len(x[1])
    ):
        print(f"  {namelist_name}: {len(test_list)} tests affected")
        if len(test_list) <= 5:
            print(f"    Tests: {', '.join(test_list)}")

    print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Diagnose namelist differences in WW3 regression tests"
    )
    parser.add_argument(
        "--test",
        help="Analyze specific test (e.g., tp1.1, tp2.4)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Analyze all available tests",
    )
    parser.add_argument(
        "--test-outputs-dir",
        type=Path,
        default=Path("test_outputs"),
        help="Directory containing test outputs (default: test_outputs)",
    )
    parser.add_argument(
        "--rompy-runs-dir",
        type=Path,
        default=Path("rompy_runs"),
        help="Directory containing rompy runs (default: rompy_runs)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output",
    )
    parser.add_argument(
        "--show-diffs",
        action="store_true",
        help="Show full diff output for mismatches",
    )

    args = parser.parse_args()

    print("=" * 80)
    print("WW3 NAMELIST DIAGNOSTIC TOOL")
    print("=" * 80)
    print(f"\nTest outputs directory: {args.test_outputs_dir}")
    print(f"Rompy runs directory: {args.rompy_runs_dir}")
    print()

    reports = {}

    if args.test:
        # Analyze single test
        test_name = args.test

        # Try to find generated namelists in multiple locations
        possible_dirs = [
            args.test_outputs_dir / test_name,
            args.test_outputs_dir
            / test_name
            / "rompy_runs"
            / f"ww3_{test_name.replace('.', '_')}_regression",
            args.rompy_runs_dir / f"ww3_{test_name.replace('.', '_')}_regression",
            Path(f"regtests/rompy_runs/ww3_{test_name.replace('.', '_')}_regression"),
        ]

        generated_dir = None
        for d in possible_dirs:
            if d.exists():
                generated_dir = d
                break

        if not generated_dir:
            print(f"❌ Could not find generated namelists for test {test_name}")
            print(f"   Searched in: {[str(d) for d in possible_dirs]}")
            return 1

        print(f"Analyzing test: {test_name}")
        print(f"Generated namelists in: {generated_dir}")
        print()

        report = analyze_test(test_name, generated_dir, args.verbose)

        if report:
            reports[test_name] = report

            print("\nResults:")
            print(f"  Namelists compared: {report.namelists_compared}")
            print(f"  Namelists matched: {report.namelists_matched}")

            if report.is_valid():
                print("  ✅ All namelists match NOAA references")
            else:
                print(f"  ❌ {len(report.get_mismatches())} namelist(s) differ")

                for diff in report.get_mismatches():
                    print(f"\n  --- {diff.namelist_name} ---")

                    if diff.reference_path and not diff.reference_path.exists():
                        print("  ⚠️  Reference not found in NOAA repo")
                    elif args.show_diffs and diff.diff_content:
                        # Show first 30 lines of diff
                        lines = diff.diff_content.split("\n")[:30]
                        print("\n".join(f"    {line}" for line in lines))
                        if len(diff.diff_content.split("\n")) > 30:
                            print(
                                f"    ... ({len(diff.diff_content.split(chr(10))) - 30} more lines)"
                            )
                    else:
                        print("  Use --show-diffs to see differences")

    elif args.all:
        # Analyze all available tests
        print("Scanning for all available tests...\n")

        # Scan test_outputs directory
        if args.test_outputs_dir.exists():
            for test_dir in args.test_outputs_dir.iterdir():
                if test_dir.is_dir():
                    test_name = test_dir.name

                    # Find generated namelists
                    possible_dirs = [
                        test_dir,
                        test_dir / "rompy_runs" / f"ww3_{test_name}_regression",
                    ]

                    for d in possible_dirs:
                        if d.exists() and any(d.glob("*.nml")):
                            print(f"Found: {test_name}")
                            report = analyze_test(test_name, d, args.verbose)
                            if report:
                                reports[test_name] = report
                            break

        # Scan rompy_runs directory
        if args.rompy_runs_dir.exists():
            for run_dir in args.rompy_runs_dir.iterdir():
                if run_dir.is_dir() and any(run_dir.glob("*.nml")):
                    # Extract test name from directory name
                    test_name = (
                        run_dir.name.replace("ww3_", "")
                        .replace("_regression", "")
                        .replace("_", ".")
                    )

                    if test_name not in reports:
                        print(f"Found: {test_name}")
                        report = analyze_test(test_name, run_dir, args.verbose)
                        if report:
                            reports[test_name] = report

        # Scan regtests/rompy_runs directory
        regtests_runs = Path("regtests/rompy_runs")
        if regtests_runs.exists():
            for run_dir in regtests_runs.iterdir():
                if run_dir.is_dir() and any(run_dir.glob("*.nml")):
                    test_name = (
                        run_dir.name.replace("ww3_", "")
                        .replace("_regression", "")
                        .replace("_", ".")
                    )

                    if test_name not in reports:
                        print(f"Found: {test_name}")
                        report = analyze_test(test_name, run_dir, args.verbose)
                        if report:
                            reports[test_name] = report

        print_summary(reports)

    else:
        parser.print_help()
        return 1

    # Return error code if any tests have issues
    return 0 if all(r.is_valid() for r in reports.values() if r) else 1


if __name__ == "__main__":
    sys.exit(main())
