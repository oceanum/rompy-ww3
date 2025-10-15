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