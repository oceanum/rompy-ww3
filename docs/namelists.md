# WW3 Namelist Documentation

This document provides an overview of the WW3 namelist classes implemented in rompy-ww3.

## Overview

The WW3 namelist system in rompy-ww3 provides Pydantic-based classes for generating and validating WW3 namelist files. Each namelist section is implemented as a separate class that can be composed together to create a complete WW3 configuration.

All namelist classes include **comprehensive validation** and **detailed documentation** for every parameter, ensuring that configurations are both syntactically correct and physically meaningful according to WW3-6.07.1 specifications.

## Enhanced Features

### Comprehensive Documentation
Every WW3 namelist field now includes:
- **Clear descriptions** of purpose and function
- **Valid value ranges** and formats
- **Usage context** and examples
- **References** to WW3-6.07.1 specifications
- **Cross-field dependencies** where applicable

### Robust Validation
All namelist classes include comprehensive validation:
- **Type safety** with Pydantic validation
- **Range validation** for physical parameters (frequencies, angles, etc.)
- **Format validation** for date/time strings and file paths
- **Enumerated value validation** for flag fields
- **Cross-field validation** for dependent parameters
- **Custom validators** for WW3-specific constraints

## Core Namelist Classes

### Domain (DOMAIN_NML)
Defines top-level model parameters including start/stop times and I/O settings.

**Key Parameters:**
- `start`: Start date for the model run (yyyymmdd hhmmss)
- `stop`: Stop date for the model run (yyyymmdd hhmmss)
- `iostyp`: Output server type (0-3)

**Enhanced Features:**
- Validates IOSTYP range (0-3)
- Validates date format for START/STOP fields
- Provides detailed documentation for all parameters

### Input (INPUT_NML)
Defines forcing inputs for the model including winds, currents, water levels, etc.

**Key Components:**
- `forcing`: Forcing input parameters (winds, currents, water levels, etc.)
- `assim`: Data assimilation parameters

**Enhanced Features:**
- Validates forcing values ('F', 'T', 'H', 'C')
- Implements cross-field validation for dependencies
- Comprehensive documentation for all forcing types

### OutputType (OUTPUT_TYPE_NML)
Defines output types and parameters including field lists, point outputs, and track outputs.

**Key Components:**
- `field`: Field output parameters (list of fields to output)
- `point`: Point output parameters (output file, name)
- `track`: Track output parameters (format)

**Enhanced Features:**
- Validates field lists against WW3 allowed values
- Adds validation for format flags (T/F)
- Detailed documentation for output configuration

### OutputDate (OUTPUT_DATE_NML)
Defines output timing including start, stride, and stop times for different output types.

**Key Components:**
- `field`: Field output timing
- `point`: Point output timing
- `restart`: Restart output timing

**Enhanced Features:**
- Validates date format consistency
- Adds validation for time stride values
- Comprehensive documentation for all timing parameters

### HomogCount (HOMOG_COUNT_NML)
Defines counts for homogeneous input types.

**Key Parameters:**
- `n_wnd`: Number of wind inputs
- `n_lev`: Number of water level inputs
- And other input types...

**Enhanced Features:**
- Validates count ranges
- Comprehensive documentation for all homogeneous input types

### HomogInput (HOMOG_INPUT_NML)
Defines individual homogeneous inputs with name, date, and values.

**Key Parameters:**
- `name`: Input type name (WND, LEV, etc.)
- `date`: Input date (yyyymmdd hhmmss)
- `value1`, `value2`, `value3`: Input values (depending on type)

**Enhanced Features:**
- Validates date formats for input dates
- Adds validation for homogeneous input values
- Detailed documentation for all input types

## Grid Namelist Classes

### Spectrum (SPECTRUM_NML)
Defines spectral parameterization including frequency and direction discretization.

**Enhanced Features:**
- Range validation for frequency, bin, and angle values
- Validates THOFF range [-0.5, 0.5]
- Comprehensive documentation for spectral parameters

### Run (RUN_NML)
Defines model run parameterization including propagation and source term flags.

**Enhanced Features:**
- Boolean validation for flags
- Detailed documentation for all run parameters

### Timesteps (TIMESTEPS_NML)
Defines model timestep configuration including CFL constraints.

**Enhanced Features:**
- Positive value validation for time steps
- Cross-validation between related timesteps
- Comprehensive documentation for all timestep parameters

### Grid (GRID_NML)
Defines grid configuration including type, coordinate system, and closure.

**Enhanced Features:**
- Validation for grid type values
- Validates coordinate system values
- Range validation for depth limits
- Detailed documentation for all grid parameters

## Preprocessor Namelist Classes

### Forcing (FORCING_NML)
Defines forcing field preprocessing configuration.

**Enhanced Features:**
- Validation for forcing values
- Validates tidal constituents
- Comprehensive documentation for all forcing parameters

### File (FILE_NML)
Defines input file content for preprocessing.

**Enhanced Features:**
- File path validation
- Validates time shift format
- Detailed documentation for all file parameters

## Usage Examples

### Basic Configuration

```python
from rompy_ww3.namelists import Domain, Input

# Create domain configuration with validation
domain = Domain(
    start="20230101 000000",
    stop="20230107 000000",
    iostyp=1
)

# Create input configuration with validation
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

### Validation Error Handling

```python
from rompy_ww3.namelists import Domain

# This will raise a validation error with a clear message
try:
    invalid_domain = Domain(
        start="invalid_date_format",  # Invalid date format
        stop="20230107 000000",
        iostyp=5  # Invalid IOSTYP value (> 3)
    )
except Exception as e:
    print(f"Validation error: {e}")
    # Output: Validation error: 1 validation error for Domain
    # iostyp
    #   IOSTYP value 5 is invalid. Must be 0, 1, 2, or 3 (type=value_error)
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
- Date/time formats are validated according to WW3 specifications
- Physical constraints are enforced (e.g., positive time steps, valid frequency ranges)

## Customization

You can extend the namelist classes to add custom functionality:

```python
from rompy_ww3.namelists import Domain

class CustomDomain(Domain):
    def custom_method(self):
        # Add custom functionality here
        pass
```

## Benefits of Enhanced Documentation and Validation

### Improved Reliability
- **Reduced Configuration Errors**: Validation catches misconfigurations before execution
- **Better Error Messages**: Clear feedback helps users fix issues quickly
- **Physical Consistency**: Validation ensures parameters meet physical constraints

### Enhanced Usability
- **Self-Documenting Code**: Clear documentation reduces learning curve
- **IDE Support**: Type hints enable better autocomplete and error detection
- **Simplified Configuration**: Clear field descriptions make configuration easier

### Better Maintainability
- **Unified Validation Approach**: Consistent validation patterns across all namelists
- **Extensible Framework**: Easy to add new validation rules and fields
- **Comprehensive Testing**: Automated tests ensure validation continues working