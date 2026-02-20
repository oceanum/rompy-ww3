# rompy-ww3

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15093426.svg)](https://doi.org/10.5281/zenodo.15093426)
[![GitHub Pages](https://github.com/rom-py/rompy-ww3/actions/workflows/sphinx_docs_to_gh_pages.yaml/badge.svg)](https://rom-py.github.io/rompy-ww3/)
[![PyPI version](https://img.shields.io/pypi/v/rompy-ww3.svg)](https://pypi.org/project/rompy-ww3/)
[![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/rom-py/rompy-ww3/python-publish.yml)](https://github.com/rom-py/rompy-ww3/actions)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/rompy-ww3)](https://pypistats.org/packages/rompy-ww3)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rompy-ww3)](https://pypi.org/project/rompy-ww3/)

The `rompy-ww3` package provides a plugin for the [rompy](https://github.com/rom-py/rompy) framework to facilitate the setup, configuration, and execution of WAVEWATCH III (WW3) models. It leverages rompy's modular architecture to streamline the creation of WW3 model control files, input datasets, and boundary conditions using templated configurations and pydantic validation.

## Development Status

**⚠️ ACTIVE DEVELOPMENT - UNRELEASED**

This WW3 plugin is currently under active development and has not yet been officially released. The architecture and API are being refined to provide the cleanest possible interface for WW3 model configuration.

**Backward compatibility is NOT guaranteed** during this development phase. Changes will strongly favor clean interfaces and architectural improvements over maintaining legacy compatibility.

## Features

This package provides:

- Complete WW3 model configuration capabilities with all namelist components
- Integration with the rompy framework using the new clean architecture
- Comprehensive namelist generation for single-grid and multi-grid configurations
- Support for all WW3 model components: domain, input, output, forcing, boundary, grid, and more
- Ready-to-use examples including full model run configurations
- Direct namelist object passing with full API access
- No redundant interfaces or parameter reconstruction
- Type-safe union types for flexible grid handling

## Implemented Namelist Components

The rompy-ww3 plugin includes complete implementations for all major WW3 namelist components:

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
- **OUNF_NML**: Unformatted output (user-created)
- **OUNP_NML**: Point output (user-created)
- **UPRSTR_NML**: Restart update (user-created)
- **PARAMS_NML**: Model parameters (user-created)

## Core Components

- **Config**: Main configuration class integrating all namelist components
- **Grid**: WW3-specific grid parameters and namelist generation
- **Data**: WW3-specific data handling with forcing and assimilation support
- **Source**: WW3-specific data sources with variable mapping
- **Namelists**: Complete set of Pydantic models for WW3 namelists

## Post-Processing

The rompy-ww3 package includes a post-processing system for transferring WW3 output files to multiple destinations with datestamped filenames.

### WW3TransferPostprocessor

Automatically transfers WW3 model outputs (restart files, field outputs, point outputs) to multiple destination prefixes using the rompy transfer backend system. The postprocessor uses rompy's Pydantic-based configuration framework for type-safe configuration management.

**Features:**
- Multi-destination fan-out: transfer to multiple destinations in one operation
- Datestamped filenames: automatic `YYYYMMDD_HHMMSS_filename` format
- Auto-extraction: timing parameters (`start_date` and `output_stride`) automatically extracted from model config
- Special restart handling: uses valid-date computation for restart files
- Failure policies: continue on error or fail-fast
- Backend-agnostic: works with any rompy.transfer backend (file://, s3://, gs://, az://, etc.)
- Standalone configuration files: processor configs can be run independently via CLI

**Configuration-Based Usage (Recommended):**

```python
from rompy_ww3.postprocess import WW3TransferConfig

# Create configuration object
config = WW3TransferConfig(
    destinations=["file:///backup/ww3-outputs/", "s3://my-bucket/outputs/"],
    output_types={"restart": {"extra": "DW"}, "field": {"list": [1, 2, 3]}},
    failure_policy="CONTINUE"
)

# Get processor class and instantiate
processor_class = config.get_postprocessor_class()
processor = processor_class()

# Process outputs - start_date and output_stride auto-extracted from model_run.config
result = processor.process(
    model_run,
    destinations=config.destinations,
    output_types=config.output_types,
    failure_policy=config.failure_policy
)
print(f"Transferred: {result['transferred_count']}, Failed: {result['failed_count']}")
```

**CLI Usage:**

```bash
# Using standalone processor config file
rompy postprocess --processor-config examples/postprocessor_configs/ww3_transfer_basic.yaml

# Or load from YAML
from rompy_ww3.postprocess import WW3TransferConfig
config = WW3TransferConfig.parse_file("ww3_transfer_config.yaml")
```

**Example Configuration File (`ww3_transfer_config.yaml`):**

```yaml
type: ww3_transfer

destinations:
  - "file:///backup/ww3-outputs/"
  - "s3://my-bucket/model-outputs/"
  - "gs://my-gcs-bucket/ww3-data/"

output_types:
  restart:
    extra: DW
  field:
    list: [1, 2, 3, 4]

failure_policy: CONTINUE
timeout: 3600

# Note: start_date and output_stride are automatically extracted from the model configuration
# They are read from model_run.config.ww3_shel.domain.start and 
# model_run.config.ww3_shel.output_date.restart.stride (or ww3_multi equivalents)
```

See `examples/postprocessor_configs/` for complete working examples.

## WW3 Executable Components

The rompy-ww3 package includes a comprehensive set of components for each WW3 executable:

- **Shell Component** (`Shel`): Handles the main WW3 shell program configuration (ww3_shel.nml)
- **Grid Component** (`Grid`): Handles WW3 grid preprocessing configuration (ww3_grid.nml)
- **Multi-Grid Component** (`Multi`): Handles multi-grid WW3 configuration (ww3_multi.nml)
- **Boundary Conditions Component** (`Bounc`): Handles WW3 boundary condition generation (ww3_bounc.nml)
- **Boundary Data Component** (`Bound`): Handles WW3 boundary data extraction (ww3_bound.nml)
- **Preprocessor Component** (`Prnc`): Handles WW3 preprocessor configuration (ww3_prnc.nml)
- **Track Component** (`Trnc`): Handles WW3 track processor configuration (ww3_trnc.nml)
- **Output Fields Component** (`Ounf`): Handles WW3 field output configuration (ww3_ounf.nml)
- **Output Points Component** (`Ounp`): Handles WW3 point output configuration (ww3_ounp.nml)
- **Restart Update Component** (`Uptstr`): Handles WW3 restart update configuration (ww3_upstr.nml)
- **Physics Parameters Component** (`Namelists`): Handles WW3 physics parameter configuration (namelists.nml)

## Documentation

See <https://rom-py.github.io/rompy-ww3/>

## Quick Start Example

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

For more detailed examples, see the [examples directory](./examples).

## Code Formatting and Pre-commit Hooks

This repository enforces Python code formatting using [black](https://github.com/psf/black) via the pre-commit framework.

To set up pre-commit hooks locally (required for all contributors):

```bash
pip install pre-commit
pre-commit install
```

This will automatically check code formatting before each commit. To format your code manually, run:

```bash
pre-commit run --all-files
```

All code must pass black formatting before it can be committed or merged.

## Versioning and Release

This project uses [tbump](https://github.com/dmerejkowsky/tbump) for version management.

To bump the version, run:

```bash
tbump <new_version>
```

This will update the version in `src/rompy_ww3/__init__.py`, commit the change, and optionally create a git tag.

tbump is included in the development requirements (`requirements_dev.txt`).

For more advanced configuration, see `tbump.toml` in the project root.

## Related Packages

- [rompy](https://github.com/rom-py/rompy)
- [rompy-swan](https://github.com/rom-py/rompy-swan)
- [rompy-schism](https://github.com/rom-py/rompy-schism)
- [rompy-notebooks](https://github.com/rom-py/rompy-notebooks)