# API Documentation

## Core Modules

### rompy_ww3.config
Main configuration class for WW3 models.

#### Config
```python
class Config(BaseConfig):
    domain: Optional[Domain]
    input_nml: Optional[Input]
    output_type: Optional[OutputType]
    output_date: Optional[OutputDate]
    homog_count: Optional[HomogCount]
    homog_input: Optional[List[HomogInput]]
```

**Methods:**
- `get_template_context()`: Generate template context for Jinja2 templates
- `generate_run_script()`: Generate a basic WW3 run script
- `render_namelists()`: Render all namelists as strings

### rompy_ww3.grid
WW3-specific grid configuration.

#### Grid
```python
class Grid(RegularGrid):
    name: Optional[str]
    grid_type: Optional[str]
    coordinate_system: Optional[str]
    # ... other grid parameters
```

**Methods:**
- `generate_grid_nml()`: Generate GRID_NML content
- `generate_rect_nml()`: Generate RECT_NML content
- `write_grid_files()`: Write grid namelist files

### rompy_ww3.data
WW3-specific data handling.

#### Data
```python
class Data(DataGrid):
    data_type: Optional[str]
    forcing_flag: Optional[str]
    assim_flag: Optional[str]
    # ... other data parameters
```

**Methods:**
- `get_forcing_config()`: Get INPUT_NML forcing parameters
- `get_assim_config()`: Get INPUT_NML assimilation parameters
- `generate_input_data_nml()`: Generate namelist entries for input data

### rompy_ww3.source
WW3-specific data sources.

#### Ww3Source
```python
class Ww3Source(SourceBase):
    data_type: Optional[str]
    file_format: Optional[str]
    variable_mapping: Optional[dict]
    # ... other source parameters
```

**Methods:**
- `get_ww3_variable_name()`: Map source variables to WW3 variable names
- `generate_source_config()`: Generate configuration dictionary
- `write_source_config()`: Write source configuration to file

## Namelist Modules

### rompy_ww3.namelists.basemodel
Base class for all namelist models.

#### NamelistBaseModel
Base class providing common functionality for namelist generation.

**Methods:**
- `render()`: Render namelist as a string
- `write_nml()`: Write namelist to file

### rompy_ww3.namelists.domain
DOMAIN_NML implementation.

#### Domain
Model for DOMAIN_NML namelist parameters.

### rompy_ww3.namelists.input
INPUT_NML implementation.

#### Input
Model for INPUT_NML namelist parameters.

#### InputForcing
Model for forcing input parameters.

#### InputAssim
Model for assimilation parameters.

### rompy_ww3.namelists.output_type
OUTPUT_TYPE_NML implementation.

#### OutputType
Model for OUTPUT_TYPE_NML namelist parameters.

### rompy_ww3.namelists.output_date
OUTPUT_DATE_NML implementation.

#### OutputDate
Model for OUTPUT_DATE_NML namelist parameters.

### rompy_ww3.namelists.homogeneous
HOMOG_COUNT_NML and HOMOG_INPUT_NML implementation.

#### HomogCount
Model for HOMOG_COUNT_NML namelist parameters.

#### HomogInput
Model for HOMOG_INPUT_NML namelist parameters.

## Composition Module

### rompy_ww3.namelist_composer
System for composing and validating complete namelist configurations.

#### NamelistComposition
Main class for composing namelist configurations.

**Methods:**
- `render_all_namelists()`: Render all namelists as strings
- `write_all_namelists()`: Write all namelists to files
- `validate_completeness()`: Validate configuration completeness
- `validate_consistency()`: Validate configuration consistency

#### compose_namelists()
Convenience function for creating NamelistComposition from Config.