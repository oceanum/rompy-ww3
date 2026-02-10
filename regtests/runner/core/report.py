"""Test result reporting and aggregation.

This module provides reporting functionality for regression test results,
supporting multiple output formats (text, JSON, HTML) with summary statistics,
per-test details, and trend analysis capabilities.

Example:
    >>> from regtests.runner.core.report import ReportGenerator
    >>> from regtests.runner.core.result import TestSuiteResult
    >>>
    >>> generator = ReportGenerator()
    >>> text_report = generator.generate_text_report(suite_result)
    >>> print(text_report)
    >>>
    >>> # Save reports to files
    >>> generator.save_report(text_report, "report.txt")
    >>> json_data = generator.generate_json_report(suite_result)
    >>> generator.save_json_report(json_data, "report.json")
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import sys

from .result import TestSuiteResult, TestStatus


class ReportGenerator:
    """Generates test execution reports in multiple formats.

    Provides comprehensive reporting with:
    - Summary statistics (pass/fail counts, duration)
    - Per-test details (name, status, errors, validation)
    - Execution timestamps and duration
    - Multiple output formats (text, JSON, HTML)
    - Trend analysis (comparison with previous runs)

    Example:
        >>> generator = ReportGenerator()
        >>> text_report = generator.generate_text_report(suite_result)
        >>> json_report = generator.generate_json_report(suite_result)
        >>> html_report = generator.generate_html_report(suite_result)
    """

    def __init__(self):
        """Initialize report generator."""
        self.timestamp = datetime.now()

    def generate_text_report(
        self,
        results: TestSuiteResult,
        title: str = "WW3 Regression Test Report",
        show_skipped: bool = True,
    ) -> str:
        """Generate human-readable text report.

        Args:
            results: TestSuiteResult with test outcomes
            title: Report title (default: "WW3 Regression Test Report")
            show_skipped: Whether to show skipped tests (default: True)

        Returns:
            Formatted text report string

        Example:
            >>> report = generator.generate_text_report(suite_result)
            >>> print(report)
        """
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append(title.center(80))
        lines.append("=" * 80)
        lines.append(f"Generated: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Summary statistics
        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append(f"Total Tests:      {results.total_tests}")
        lines.append(
            f"Passed:           {results.passed} ({self._percentage(results.passed, results.total_tests)})"
        )
        lines.append(
            f"Failed:           {results.failed} ({self._percentage(results.failed, results.total_tests)})"
        )
        lines.append(
            f"Errors:           {results.errors} ({self._percentage(results.errors, results.total_tests)})"
        )
        lines.append(
            f"Skipped:          {results.skipped} ({self._percentage(results.skipped, results.total_tests)})"
        )
        lines.append(f"Total Duration:   {results.total_time:.2f}s")
        lines.append(
            f"Average Duration: {results.total_time / max(results.total_tests, 1):.2f}s"
        )
        lines.append("")

        # Overall status
        if results.is_success():
            lines.append("✓ ALL TESTS PASSED")
        else:
            lines.append("✗ TESTS FAILED")
        lines.append("")

        # Per-test details
        lines.append("TEST DETAILS")
        lines.append("-" * 80)

        # Group by status for better readability
        passed_tests = [r for r in results.results if r.status == TestStatus.SUCCESS]
        failed_tests = [r for r in results.results if r.status == TestStatus.FAILURE]
        error_tests = [r for r in results.results if r.status == TestStatus.ERROR]
        skipped_tests = [r for r in results.results if r.status == TestStatus.SKIPPED]

        # Passed tests
        if passed_tests:
            lines.append("")
            lines.append("PASSED TESTS:")
            for result in passed_tests:
                status_symbol = "✓"
                validation_info = ""
                if result.validation_results:
                    validation_info = f" (validated: {result.validation_results.files_matched}/{result.validation_results.files_compared} files)"
                lines.append(
                    f"  {status_symbol} {result.test_name:<30} {result.execution_time:>8.2f}s{validation_info}"
                )

        # Failed tests
        if failed_tests:
            lines.append("")
            lines.append("FAILED TESTS:")
            for result in failed_tests:
                status_symbol = "✗"
                lines.append(
                    f"  {status_symbol} {result.test_name:<30} {result.execution_time:>8.2f}s"
                )
                if (
                    result.validation_results
                    and not result.validation_results.is_valid()
                ):
                    lines.append(
                        f"     Validation: {result.validation_results.files_matched}/{result.validation_results.files_compared} files matched"
                    )
                    if result.validation_results.differences:
                        lines.append("     Differences:")
                        for diff in result.validation_results.differences[
                            :5
                        ]:  # Limit to first 5
                            lines.append(f"       - {diff}")
                        if len(result.validation_results.differences) > 5:
                            remaining = len(result.validation_results.differences) - 5
                            lines.append(f"       ... and {remaining} more differences")

        # Error tests
        if error_tests:
            lines.append("")
            lines.append("TESTS WITH ERRORS:")
            for result in error_tests:
                status_symbol = "⚠"
                lines.append(
                    f"  {status_symbol} {result.test_name:<30} {result.execution_time:>8.2f}s"
                )
                if result.error_message:
                    # Truncate long error messages
                    error_lines = result.error_message.split("\n")
                    for error_line in error_lines[:3]:
                        lines.append(f"     {error_line}")
                    if len(error_lines) > 3:
                        lines.append(f"     ... ({len(error_lines) - 3} more lines)")

        # Skipped tests
        if show_skipped and skipped_tests:
            lines.append("")
            lines.append("SKIPPED TESTS:")
            for result in skipped_tests:
                status_symbol = "○"
                lines.append(f"  {status_symbol} {result.test_name}")

        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    def generate_json_report(
        self,
        results: TestSuiteResult,
        include_logs: bool = False,
    ) -> Dict[str, Any]:
        """Generate JSON-formatted report.

        Args:
            results: TestSuiteResult with test outcomes
            include_logs: Whether to include full execution logs (default: False)

        Returns:
            Dictionary suitable for JSON serialization

        Example:
            >>> json_data = generator.generate_json_report(suite_result)
            >>> with open("report.json", "w") as f:
            ...     json.dump(json_data, f, indent=2)
        """
        report = {
            "metadata": {
                "generated_at": self.timestamp.isoformat(),
                "timestamp": self.timestamp.timestamp(),
            },
            "summary": {
                "total_tests": results.total_tests,
                "passed": results.passed,
                "failed": results.failed,
                "errors": results.errors,
                "skipped": results.skipped,
                "total_time": results.total_time,
                "average_time": results.total_time / max(results.total_tests, 1),
                "success": results.is_success(),
            },
            "tests": [],
        }

        # Per-test results
        for result in results.results:
            test_data = {
                "name": result.test_name,
                "status": result.status.value,
                "execution_time": result.execution_time,
            }

            # Add validation results if present
            if result.validation_results:
                test_data["validation"] = {
                    "files_compared": result.validation_results.files_compared,
                    "files_matched": result.validation_results.files_matched,
                    "is_valid": result.validation_results.is_valid(),
                    "tolerance": result.validation_results.tolerance_used,
                    "differences": result.validation_results.differences,
                }

            # Add error message if present
            if result.error_message:
                test_data["error_message"] = result.error_message

            # Add outputs if present
            if result.outputs_generated:
                test_data["outputs"] = [str(p) for p in result.outputs_generated]

            # Add logs if requested
            if include_logs and result.logs:
                test_data["logs"] = result.logs

            report["tests"].append(test_data)

        return report

    def generate_html_report(
        self,
        results: TestSuiteResult,
        title: str = "WW3 Regression Test Report",
    ) -> str:
        """Generate HTML report with interactive elements.

        Args:
            results: TestSuiteResult with test outcomes
            title: Report title (default: "WW3 Regression Test Report")

        Returns:
            HTML string

        Example:
            >>> html = generator.generate_html_report(suite_result)
            >>> with open("report.html", "w") as f:
            ...     f.write(html)
        """
        html_parts = []

        # HTML header with inline CSS
        html_parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .header .timestamp {{
            opacity: 0.9;
            font-size: 14px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            text-transform: uppercase;
            color: #666;
        }}
        .summary-card .value {{
            font-size: 32px;
            font-weight: bold;
        }}
        .summary-card.passed .value {{ color: #10b981; }}
        .summary-card.failed .value {{ color: #ef4444; }}
        .summary-card.errors .value {{ color: #f59e0b; }}
        .summary-card.skipped .value {{ color: #6b7280; }}
        .test-list {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .test-item {{
            padding: 15px;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .test-item:last-child {{
            border-bottom: none;
        }}
        .test-status {{
            display: inline-block;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            text-align: center;
            line-height: 24px;
            font-weight: bold;
            margin-right: 10px;
        }}
        .test-status.passed {{ background: #10b981; color: white; }}
        .test-status.failed {{ background: #ef4444; color: white; }}
        .test-status.error {{ background: #f59e0b; color: white; }}
        .test-status.skipped {{ background: #6b7280; color: white; }}
        .test-details {{
            flex-grow: 1;
        }}
        .test-name {{
            font-weight: 600;
            margin-bottom: 5px;
        }}
        .test-meta {{
            font-size: 14px;
            color: #666;
        }}
        .test-time {{
            font-weight: 600;
            color: #666;
        }}
        .validation-info {{
            margin-top: 10px;
            padding: 10px;
            background: #f9fafb;
            border-radius: 4px;
            font-size: 14px;
        }}
        .error-message {{
            margin-top: 10px;
            padding: 10px;
            background: #fef2f2;
            border-left: 3px solid #ef4444;
            border-radius: 4px;
            font-size: 14px;
            font-family: monospace;
            white-space: pre-wrap;
        }}
        .differences {{
            margin-top: 5px;
            padding-left: 20px;
        }}
        .differences li {{
            margin: 3px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <div class="timestamp">Generated: {self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}</div>
    </div>
""")

        # Summary cards
        html_parts.append("""    <div class="summary">""")

        summary_cards = [
            ("Total Tests", results.total_tests, ""),
            ("Passed", results.passed, "passed"),
            ("Failed", results.failed, "failed"),
            ("Errors", results.errors, "errors"),
            ("Skipped", results.skipped, "skipped"),
            ("Duration", f"{results.total_time:.1f}s", ""),
        ]

        for label, value, css_class in summary_cards:
            html_parts.append(f"""
        <div class="summary-card {css_class}">
            <h3>{label}</h3>
            <div class="value">{value}</div>
        </div>""")

        html_parts.append("""    </div>""")

        # Test list
        html_parts.append("""    <div class="test-list">""")

        for result in results.results:
            status_class = result.status.value
            status_symbol = self._get_status_symbol(result.status)

            html_parts.append(f"""
        <div class="test-item">
            <span class="test-status {status_class}">{status_symbol}</span>
            <div class="test-details">
                <div class="test-name">{result.test_name}</div>
                <div class="test-meta">Status: {result.status.value.upper()}</div>
""")

            # Validation info
            if result.validation_results:
                vr = result.validation_results
                html_parts.append(f"""
                <div class="validation-info">
                    Validation: {vr.files_matched}/{vr.files_compared} files matched (tolerance: {vr.tolerance_used})
""")
                if not vr.is_valid() and vr.differences:
                    html_parts.append("""
                    <ul class="differences">
""")
                    for diff in vr.differences[:5]:
                        html_parts.append(
                            f"""                        <li>{diff}</li>"""
                        )
                    if len(vr.differences) > 5:
                        remaining = len(vr.differences) - 5
                        html_parts.append(
                            f"""                        <li>... and {remaining} more differences</li>"""
                        )
                    html_parts.append("""
                    </ul>
""")
                html_parts.append("""                </div>""")

            # Error message
            if result.error_message:
                error_preview = result.error_message[:500]
                if len(result.error_message) > 500:
                    error_preview += "..."
                html_parts.append(f"""
                <div class="error-message">{error_preview}</div>
""")

            html_parts.append(
                """
            </div>
            <div class="test-time">{:.2f}s</div>
        </div>
""".format(result.execution_time)
            )

        html_parts.append("""    </div>""")

        # HTML footer
        html_parts.append("""
</body>
</html>""")

        return "".join(html_parts)

    def save_report(self, report: str, filepath: Path, encoding: str = "utf-8") -> None:
        """Save text or HTML report to file.

        Args:
            report: Report string (text or HTML)
            filepath: Path to output file
            encoding: File encoding (default: utf-8)

        Example:
            >>> generator.save_report(text_report, Path("report.txt"))
            >>> generator.save_report(html_report, Path("report.html"))
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", encoding=encoding) as f:
            f.write(report)

    def save_json_report(self, report: Dict[str, Any], filepath: Path) -> None:
        """Save JSON report to file.

        Args:
            report: JSON report dictionary
            filepath: Path to output file

        Example:
            >>> json_data = generator.generate_json_report(suite_result)
            >>> generator.save_json_report(json_data, Path("report.json"))
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    def print_report(self, report: str, file=None) -> None:
        """Print report to stdout or specified file.

        Args:
            report: Report string to print
            file: File object (default: sys.stdout)

        Example:
            >>> generator.print_report(text_report)
        """
        if file is None:
            file = sys.stdout
        print(report, file=file)

    def compare_with_previous(
        self,
        current: TestSuiteResult,
        previous: TestSuiteResult,
    ) -> str:
        """Generate trend analysis comparing current with previous results.

        Args:
            current: Current test suite results
            previous: Previous test suite results

        Returns:
            Text report showing trend analysis

        Example:
            >>> trend_report = generator.compare_with_previous(current, previous)
            >>> print(trend_report)
        """
        lines = []

        lines.append("=" * 80)
        lines.append("TREND ANALYSIS".center(80))
        lines.append("=" * 80)
        lines.append("")

        # Summary comparison
        lines.append("SUMMARY COMPARISON")
        lines.append("-" * 80)

        metrics = [
            ("Total Tests", previous.total_tests, current.total_tests),
            ("Passed", previous.passed, current.passed),
            ("Failed", previous.failed, current.failed),
            ("Errors", previous.errors, current.errors),
            ("Skipped", previous.skipped, current.skipped),
            ("Duration", previous.total_time, current.total_time),
        ]

        for label, prev_val, curr_val in metrics:
            if label == "Duration":
                change = curr_val - prev_val
                change_str = f"{change:+.2f}s"
            else:
                change = curr_val - prev_val
                change_str = f"{change:+d}"

            trend_symbol = self._get_trend_symbol(change, label)
            lines.append(
                f"{label:<15} {prev_val:>8} → {curr_val:>8} ({change_str:>8}) {trend_symbol}"
            )

        lines.append("")

        # Per-test changes
        lines.append("TEST STATUS CHANGES")
        lines.append("-" * 80)

        # Create lookup for previous results
        prev_lookup = {r.test_name: r for r in previous.results}

        changes = []
        for curr_result in current.results:
            prev_result = prev_lookup.get(curr_result.test_name)

            if prev_result is None:
                changes.append(
                    f"  NEW: {curr_result.test_name} - {curr_result.status.value}"
                )
            elif prev_result.status != curr_result.status:
                changes.append(
                    f"  CHANGED: {curr_result.test_name} - "
                    f"{prev_result.status.value} → {curr_result.status.value}"
                )

        # Check for removed tests
        curr_lookup = {r.test_name: r for r in current.results}
        for prev_result in previous.results:
            if prev_result.test_name not in curr_lookup:
                changes.append(f"  REMOVED: {prev_result.test_name}")

        if changes:
            lines.extend(changes)
        else:
            lines.append("  No status changes detected")

        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    def _percentage(self, value: int, total: int) -> str:
        """Calculate percentage string.

        Args:
            value: Numerator value
            total: Denominator value

        Returns:
            Formatted percentage string
        """
        if total == 0:
            return "0.0%"
        return f"{(value / total) * 100:.1f}%"

    def _get_status_symbol(self, status: TestStatus) -> str:
        """Get status symbol for HTML rendering.

        Args:
            status: Test status

        Returns:
            Single character symbol
        """
        symbols = {
            TestStatus.SUCCESS: "✓",
            TestStatus.FAILURE: "✗",
            TestStatus.ERROR: "⚠",
            TestStatus.SKIPPED: "○",
        }
        return symbols.get(status, "?")

    def _get_trend_symbol(self, change: float, metric: str) -> str:
        """Get trend symbol based on change and metric type.

        Args:
            change: Change in value
            metric: Metric name

        Returns:
            Trend symbol
        """
        if change == 0:
            return "→"

        # For "good" metrics (passed), positive change is good
        # For "bad" metrics (failed, errors), negative change is good
        good_metrics = ["Passed"]
        bad_metrics = ["Failed", "Errors", "Duration"]

        if metric in good_metrics:
            return "↑" if change > 0 else "↓"
        elif metric in bad_metrics:
            return "↓" if change > 0 else "↑"
        else:
            return "↑" if change > 0 else "↓"
