# WW3 Namelist Documentation

This document provides an overview of the WW3 namelist classes implemented in rompy-ww3.

## Overview

The WW3 namelist system in rompy-ww3 provides Pydantic-based classes for generating and validating WW3 namelist files. Each namelist section is implemented as a separate class that can be composed together to create a complete WW3 configuration.

## Core Namelist Classes

### Domain (DOMAIN_NML)
Defines top-level model parameters including start/stop times and I/O settings.

**Key Parameters:**
- `start`: Start date for the model run (yyyymmdd hhmmss)
- `stop`: Stop date for the model run (yyyymmdd hhmmss)
- `iostyp`: Output server type (0-3)

### Input (INPUT_NML)
Defines forcing inputs for the model including winds, currents, water levels, etc.

**Key Components:**
- `forcing`: Forcing input parameters (winds, currents, water levels, etc.)
- `assim`: Data assimilation parameters

### OutputType (OUTPUT_TYPE_NML)
Defines output types and parameters including field lists, point outputs, and track outputs.

**Key Components:**
- `field`: Field output parameters (list of fields to output)
- `point`: Point output parameters (output file, name)
- `track`: Track output parameters (format)

### OutputDate (OUTPUT_DATE_NML)
Defines output timing including start, stride, and stop times for different output types.

**Key Components:**
- `field`: Field output timing
- `point`: Point output timing
- `restart`: Restart output timing

### HomogCount (HOMOG_COUNT_NML)
Defines counts for homogeneous input types.

**Key Parameters:**
- `n_wnd`: Number of wind inputs
- `n_lev`: Number of water level inputs
- And other input types...

### HomogInput (HOMOG_INPUT_NML)
Defines individual homogeneous inputs with name, date, and values.

**Key Parameters:**
- `name`: Input type name (WND, LEV, etc.)
- `date`: Input date (yyyymmdd hhmmss)
- `value1`, `value2`, `value3`: Input values (depending on type)

## Usage Examples

### Basic Configuration

```python
from rompy_ww3.namelists import Domain, Input

# Create domain configuration
domain = Domain(
    start="20230101 000000",
    stop="20230107 000000",
    iostyp=1
)

# Create input configuration
input_nml = Input(
    forcing={
        "winds": "T",
        "water_levels": "T"
    }
)

# Render namelists
print(domain.render())
print(input_nml.render())
```

### Writing to Files

```python
from pathlib import Path

# Write namelists to files
domain.write_nml(Path("./namelists"))
input_nml.write_nml(Path("./namelists"))
```

## Namelist Composition

For complex configurations, use the `NamelistComposition` class:

```python
from rompy_ww3.namelist_composer import NamelistComposition

composition = NamelistComposition(
    domain=domain,
    input_nml=input_nml
)

# Validate the configuration
issues = composition.validate_completeness()
if not issues:
    print("Configuration is complete!")

# Render all namelists at once
all_namelists = composition.render_all_namelists()

# Write all namelists to files
composition.write_all_namelists(Path("./namelists"))
```

## Integration with Config Class

The namelist classes integrate seamlessly with the main `Config` class:

```python
from rompy_ww3.config import Config

config = Config(
    domain=Domain(start="20230101 000000", stop="20230107 000000"),
    input_nml=Input(forcing={"winds": "T"})
)

# Generate template context for use in Jinja2 templates
context = config.get_template_context()

# Generate run script
config.generate_run_script(Path("./run"))
```

## Validation

All namelist classes include built-in validation:

- Required fields are checked
- Field values are validated (e.g., forcing flags must be 'F', 'T', 'H', or 'C')
- Cross-validation between related namelists (e.g., homog counts vs. actual inputs)

## Customization

You can extend the namelist classes to add custom functionality:

```python
from rompy_ww3.namelists import Domain

class CustomDomain(Domain):
    def custom_method(self):
        # Add custom functionality here
        pass
```