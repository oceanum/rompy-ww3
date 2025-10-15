# Architecture

The rompy-ww3 package follows the modular architecture of the rompy framework, providing WW3-specific implementations for configuration, data handling, grid definitions, and source definitions.

## Core Components

### Config
The `Config` class is the main entry point for WW3 model configuration. It orchestrates the various namelist components to generate complete WW3 control files.

### Grid
The `Grid` class extends rompy's grid functionality with WW3-specific parameters, handling grid discretization and coordinate systems specifically for WW3 models.

### Data
The `Data` class manages WW3-specific data requirements, including meteorological forcing (winds), oceanographic data (water levels, currents), and ice concentration, with proper formatting for WW3 input.

### Source
The `Ww3Source` class defines WW3-specific data source implementations, handling various data formats and providers with appropriate variable mappings for WW3 requirements.

## Namelist System

The package implements a comprehensive namelist system using Pydantic models for validation and serialization. Each WW3 namelist component is represented as a separate Pydantic model:

- Domain configuration (DOMAIN_NML)
- Input data specification (INPUT_NML, INPUT_GRID_NML)
- Model grid definitions (MODEL_GRID_NML)
- Output specifications (OUTPUT_TYPE_NML, OUTPUT_DATE_NML)
- Boundary conditions (BOUND_NML)
- Forcing parameters (FORCING_NML)
- And many more

## Template System

The package uses a templated approach to generate WW3 control files, allowing for both simple and complex model configurations. The template system ensures proper formatting and variable substitution for WW3 namelist and input files.

## Execution Flow

1. User defines configuration using Pydantic models
2. Configuration is validated using Pydantic's built-in validation
3. Template context is generated from the validated configuration
4. Templates are rendered to produce final WW3 control files
5. Generated files are written to the specified output directory