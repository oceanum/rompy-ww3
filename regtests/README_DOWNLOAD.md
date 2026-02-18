# WW3 Regression Test Input Data Download

This directory contains the download infrastructure for WW3 regression test input files from the official NOAA-EMC/WW3 GitHub repository.

## Quick Start

```bash
# Download specific test inputs
python download_input_data.py tp2.4

# Download entire test series
python download_input_data.py tp2

# Preview downloads (dry-run)
python download_input_data.py tp1 --dry-run

# List available tests
python download_input_data.py --list
```

## Features

- **Fast Concurrent Downloads**: 8 parallel workers by default
- **Resume Support**: Interrupted downloads continue from last position
- **Smart Skipping**: Existing files skipped unless `--force` specified
- **Progress Tracking**: Real-time progress bars (requires tqdm)
- **Dry Run Mode**: Preview downloads without downloading
- **File Integrity**: Size verification for all downloads

## Usage Examples

### Download Single Test
```bash
python download_input_data.py tp2.4
```
Downloads all input files for tp2.4 test to `ww3_tp2.4/input/`

### Download Multiple Tests
```bash
python download_input_data.py tp1.1 tp2.4 tp2.5
```
Downloads inputs for specified tests

### Download Test Series
```bash
python download_input_data.py tp1
```
Downloads all tp1.x tests (tp1.1 through tp1.10)

### Force Re-download
```bash
python download_input_data.py tp2.4 --force
```
Overwrites existing files

### Adjust Concurrency
```bash
python download_input_data.py tp2 --workers 16
```
Uses 16 concurrent download workers

## Test Series

| Series | Description | Count | Total Size |
|--------|-------------|-------|------------|
| tp1 | 1-D propagation tests | 10 tests | ~0.2 MB |
| tp2 | 2-D propagation tests | 17 tests | ~25 MB |

## File Organization

```
regtests/
├── download_input_data.py    # This script
├── ww3_tp1.1/
│   └── input/                # Downloaded input files
│       ├── 1-D.depth
│       ├── namelists_1-D.nml
│       └── ...
├── ww3_tp2.4/
│   └── input/                # Downloaded input files
│       ├── depth.225x106.IDLA1.dat
│       ├── namelists_2-D.nml
│       └── ...
└── ...
```

## Requirements

- Python 3.7+
- Standard library only (urllib, json, pathlib, concurrent.futures)
- Optional: `tqdm` for progress bars (pip install tqdm)

## CI/CD Integration

```bash
# Cache-friendly download (skip existing)
python download_input_data.py tp2.4

# Verify before downloading
python download_input_data.py tp2 --dry-run
```

Input files are added to `.gitignore` - download before running tests.

## Source Repository

Input files are fetched from:
- Repository: https://github.com/NOAA-EMC/WW3
- Branch: develop
- Path: regtests/ww3_tpX.X/input/

## Troubleshooting

### Downloads Failing
- Check internet connectivity
- GitHub may be down (check status.github.com)
- Try reducing workers: `--workers 2`

### Missing Files
- Use `--force` to re-download
- Check test name is valid: `--list`

### No Progress Bars
- Install tqdm: `pip install tqdm`
- Progress still reported in summary

## Performance

- tp2.4 (29 files, 1.46 MB): ~3 seconds
- tp2 series (17 tests, ~25 MB): ~45 seconds
- Concurrent downloads 5-10x faster than sequential

## Support

For issues or questions about input data:
- WW3 Source: https://github.com/NOAA-EMC/WW3
- rompy-ww3: https://github.com/rom-py/rompy-ww3
