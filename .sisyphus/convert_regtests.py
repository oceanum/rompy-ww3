#!/usr/bin/env python3
"""
Script to convert string dates and integers to proper Python types in regtest files.
"""

import re
import sys
from pathlib import Path


def convert_date_string(date_str):
    """Convert WW3 date string YYYYMMDD HHMMSS to datetime(YYYY, M, D, H, M, S)."""
    # Parse: "19680606 000000" -> datetime(1968, 6, 6, 0, 0, 0)
    match = re.match(r"(\d{4})(\d{2})(\d{2})\s+(\d{2})(\d{2})(\d{2})", date_str)
    if match:
        y, m, d, hh, mm, ss = match.groups()
        return (
            f"datetime({int(y)}, {int(m)}, {int(d)}, {int(hh)}, {int(mm)}, {int(ss)})"
        )
    return None


def process_file(filepath):
    """Process a single file to convert string dates and integers."""
    content = filepath.read_text()
    original_content = content

    # Track if we need to add datetime import
    needs_datetime_import = False
    has_datetime_import = (
        "from datetime import datetime" in content or "import datetime" in content
    )

    # Pattern 1: start="YYYYMMDD HHMMSS"
    def replace_start(match):
        nonlocal needs_datetime_import
        date_str = match.group(1)
        datetime_obj = convert_date_string(date_str)
        if datetime_obj:
            needs_datetime_import = True
            return f"start={datetime_obj}"
        return match.group(0)

    content = re.sub(r'start="(\d{8}\s+\d{6})"', replace_start, content)

    # Pattern 2: stop="YYYYMMDD HHMMSS"
    def replace_stop(match):
        nonlocal needs_datetime_import
        date_str = match.group(1)
        datetime_obj = convert_date_string(date_str)
        if datetime_obj:
            needs_datetime_import = True
            return f"stop={datetime_obj}"
        return match.group(0)

    content = re.sub(r'stop="(\d{8}\s+\d{6})"', replace_stop, content)

    # Pattern 3: timestart="YYYYMMDD HHMMSS"
    def replace_timestart(match):
        nonlocal needs_datetime_import
        date_str = match.group(1)
        datetime_obj = convert_date_string(date_str)
        if datetime_obj:
            needs_datetime_import = True
            return f"timestart={datetime_obj}"
        return match.group(0)

    content = re.sub(r'timestart="(\d{8}\s+\d{6})"', replace_timestart, content)

    # Pattern 4: stride="NNNNN"
    content = re.sub(r'stride="(\d+)"', r"stride=\1", content)

    # Pattern 5: timestride="NNNNN"
    content = re.sub(r'timestride="(\d+)"', r"timestride=\1", content)

    # Pattern 6: timecount="NNNNN"
    content = re.sub(r'timecount="(\d+)"', r"timecount=\1", content)

    # Pattern 7: Dict syntax - "start": "YYYYMMDD HHMMSS"
    def replace_dict_start(match):
        nonlocal needs_datetime_import
        date_str = match.group(1)
        datetime_obj = convert_date_string(date_str)
        if datetime_obj:
            needs_datetime_import = True
            return f'"start": {datetime_obj}'
        return match.group(0)

    content = re.sub(r'"start":\s*"(\d{8}\s+\d{6})"', replace_dict_start, content)

    # Pattern 8: Dict syntax - "stop": "YYYYMMDD HHMMSS"
    def replace_dict_stop(match):
        nonlocal needs_datetime_import
        date_str = match.group(1)
        datetime_obj = convert_date_string(date_str)
        if datetime_obj:
            needs_datetime_import = True
            return f'"stop": {datetime_obj}'
        return match.group(0)

    content = re.sub(r'"stop":\s*"(\d{8}\s+\d{6})"', replace_dict_stop, content)

    # Pattern 9: Dict syntax - "timestart": "YYYYMMDD HHMMSS"
    def replace_dict_timestart(match):
        nonlocal needs_datetime_import
        date_str = match.group(1)
        datetime_obj = convert_date_string(date_str)
        if datetime_obj:
            needs_datetime_import = True
            return f'"timestart": {datetime_obj}'
        return match.group(0)

    content = re.sub(
        r'"timestart":\s*"(\d{8}\s+\d{6})"', replace_dict_timestart, content
    )

    # Pattern 10: Dict syntax - "stride": "NNNNN"
    content = re.sub(r'"stride":\s*"(\d+)"', r'"stride": \1', content)

    # Pattern 11: Dict syntax - "timestride": "NNNNN"
    content = re.sub(r'"timestride":\s*"(\d+)"', r'"timestride": \1', content)

    # Pattern 12: Dict syntax - "timecount": "NNNNN"
    content = re.sub(r'"timecount":\s*"(\d+)"', r'"timecount": \1', content)

    # Add datetime import if needed and not present
    if needs_datetime_import and not has_datetime_import:
        # Find the first import line and add after it
        lines = content.split("\n")
        insert_index = 0
        for i, line in enumerate(lines):
            if line.startswith("from ") or line.startswith("import "):
                insert_index = i + 1
            elif insert_index > 0 and not line.startswith(
                ("from ", "import ", "#", "\n", "")
            ):
                break

        if insert_index > 0:
            lines.insert(insert_index, "from datetime import datetime")
            content = "\n".join(lines)

    # Write back if changed
    if content != original_content:
        filepath.write_text(content)
        return True
    return False


def main():
    """Main function to process all regtest files."""
    regtests_dir = Path(
        "/home/tdurrant/source/rompy/rompy-meta/repos/rompy-ww3/fix-ww3-validation-errors/regtests"
    )

    if not regtests_dir.exists():
        print(f"Error: Directory {regtests_dir} does not exist")
        sys.exit(1)

    py_files = list(regtests_dir.glob("**/*.py"))
    py_files = [
        f for f in py_files if "run_regression_tests.py" not in f.name
    ]  # Skip test runner

    print(f"Found {len(py_files)} Python files in regtests directory")

    modified_count = 0
    for filepath in py_files:
        try:
            if process_file(filepath):
                modified_count += 1
                print(f"  Modified: {filepath.relative_to(regtests_dir)}")
        except Exception as e:
            print(f"  Error processing {filepath}: {e}")

    print(f"\nProcessed {len(py_files)} files, modified {modified_count} files")


if __name__ == "__main__":
    main()
