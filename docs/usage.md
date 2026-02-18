# Usage

The rompy-ww3 package provides a plugin for the rompy framework to facilitate the setup,
configuration, and execution of WAVEWATCH III (WW3) models.

## Basic Configuration

```python
from rompy_ww3.config import Config
from rompy_ww3.namelists import Domain, Input

# Create a basic WW3 configuration
config = Config(
    domain=Domain(
        start="20230101 000000",
        stop="20230107 000000",
        iostyp=1
    ),
    input_nml=Input(
        forcing={
            "winds": "T",
            "water_levels": "T"
        }
    )
)

# Generate namelist files
result = config(runtime=your_runtime_object)

# Generate template context for use in templates
context = config.get_template_context()
```

## Available Namelist Components

The rompy-ww3 plugin includes implementations for all major WW3 namelist components:

- **DOMAIN_NML**: Domain definition and model timing
- **INPUT_NML**: Input data configuration for single-grid models
- **INPUT_GRID_NML**: Input grid specification for multi-grid models
- **MODEL_GRID_NML**: Model grid specification for multi-grid models
- **OUTPUT_TYPE_NML**: Output field specifications
- **OUTPUT_DATE_NML**: Output timing configuration
- **HOMOG_COUNT_NML**: Homogeneous input counts
- **HOMOG_INPUT_NML**: Homogeneous input specifications
- **SPECTRUM_NML**: Frequency and direction discretization
- **RUN_NML**: Run parameterization
- **TIMESTEPS_NML**: Time step configuration
- **GRID_NML & RECT_NML**: Grid preprocessing parameters
- **BOUND_NML**: Boundary input preprocessing
- **FORCING_NML**: Forcing field preprocessing
- **TRACK_NML**: Track output post-processing
- **FIELD_NML**: Field output post-processing
- **POINT_NML**: Point output post-processing
- **RESTART_NML**: Restart file initialization

## Command Line Interface

The package provides a command-line interface for common operations:

```bash
# Generate a WW3 configuration
rompy_ww3 generate --config my_config.yaml

# Validate a configuration
rompy_ww3 validate --config my_config.yaml

# Render templates using a configuration
rompy_ww3 render --config my_config.yaml --output-dir ./output
```

## Post-Processing

### WW3TransferPostprocessor

The `WW3TransferPostprocessor` provides automatic transfer of WW3 model outputs to multiple destinations with consistent datestamped naming. It is registered as the `ww3_transfer` entry point under the `rompy.postprocess` group and can be invoked as part of the rompy post-processing pipeline.

#### Features

- **Multi-destination fan-out**: Transfer files to multiple destinations (S3, local filesystem, HTTP, etc.) in a single operation
- **Datestamped filenames**: Automatically generates `YYYYMMDD_HHMMSS_filename` format for consistent naming
- **Restart file handling**: Special processing for restart files with valid-date computation
- **Configurable failure policies**: Choose between CONTINUE (log errors and continue) or FAIL_FAST (stop on first error)
- **Backend-agnostic**: Works with any rompy.transfer backend via scheme-based dispatch

#### Configuration Parameters

- `destinations`: List of destination URIs treated as prefixes (e.g., `["s3://bucket/path/", "file:///local/backup/"]`)
- `output_types`: Dictionary specifying which WW3 output types to transfer (e.g., `{"restart": {"extra": "DW"}}`)
- `failure_policy`: Either "CONTINUE" or "FAIL_FAST" (default: "CONTINUE")
- `start_date`: Optional WW3 date string for datestamp generation (e.g., "20230101 000000")
- `output_stride`: Optional integer for restart valid-date computation

#### Basic Example

```python
from rompy_ww3.postprocess.processor import WW3TransferPostprocessor

# Create postprocessor with single local destination
postprocessor = WW3TransferPostprocessor(
    destinations=["file:///backup/ww3-outputs/"],
    output_types={"restart": {"extra": "DW"}},
    failure_policy="CONTINUE",
    start_date="20230101 000000"
)

# Process model outputs
result = postprocessor.process(model_run)

# Check results
if result["success"]:
    print(f"Successfully transferred {result['transferred_count']} files")
else:
    print(f"Transferred {result['transferred_count']}, failed {result['failed_count']}")
```

#### Multi-Destination Example

```python
# Transfer to both S3 and local backup
postprocessor = WW3TransferPostprocessor(
    destinations=[
        "s3://my-bucket/model-outputs/run-001/",
        "file:///local/backup/run-001/"
    ],
    output_types={
        "restart": {"extra": "DW"},
        "field": {"list": [1, 2, 3]}
    },
    failure_policy="FAIL_FAST",  # Stop on first error
    start_date="20230101 000000",
    output_stride=3600
)

result = postprocessor.process(model_run)
```

#### Failure Policy Examples

**CONTINUE Policy** (default): Log errors but continue transferring remaining files

```python
postprocessor = WW3TransferPostprocessor(
    destinations=["s3://bucket-a/", "s3://bucket-b/", "file:///backup/"],
    output_types={"restart": {"extra": "DW"}},
    failure_policy="CONTINUE"
)

# If bucket-b fails, bucket-a and file:/// transfers still attempted
result = postprocessor.process(model_run)
print(f"Succeeded: {result['transferred_count']}, Failed: {result['failed_count']}")
```

**FAIL_FAST Policy**: Stop immediately on first error

```python
postprocessor = WW3TransferPostprocessor(
    destinations=["s3://bucket-a/", "s3://bucket-b/"],
    output_types={"restart": {"extra": "DW"}},
    failure_policy="FAIL_FAST"
)

# If bucket-a fails, bucket-b transfer is never attempted
try:
    result = postprocessor.process(model_run)
except Exception as e:
    print(f"Transfer failed: {e}")
```

#### Integration with rompy

The postprocessor integrates with the rompy framework via the entry point system:

```python
# Entry point: rompy.postprocess
# Name: ww3_transfer
# Class: rompy_ww3.postprocess.processor:WW3TransferPostprocessor

# Loaded automatically by rompy's postprocessing pipeline
from importlib.metadata import entry_points

eps = entry_points(group='rompy.postprocess')
ww3_transfer = eps['ww3_transfer'].load()
```