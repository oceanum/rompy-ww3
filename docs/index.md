# Welcome to rompy-ww3's documentation!

Relocatable Ocean Modelling in PYthon (rompy) is a modular Python library that
aims to streamline the setup, configuration, execution, and analysis of coastal
ocean models. Rompy combines templated model configuration with powerful
xarray-based data handling and pydantic validation, enabling users to
efficiently generate model control files and input datasets for a variety of
ocean and wave models.

## Contents

- [Installation](installation.md)
- [Usage](usage.md)
- [Architecture](architecture.md)
- [Contributing](contributing.md)
- [API Reference](#)

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

For more detailed examples, see the examples directory.