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
WW3-specific grid configuration with clean architecture.

#### RectGrid
```python
class RectGrid(BaseGrid):
    grid_type: Literal["base"]
    model_type: Literal["ww3_rect"]
    grid_nml: Optional[GRID_NML]
    rect_nml: Optional[Rect]
    depth: Optional[Depth]
    mask: Optional[Mask]
    obst: Optional[Obstacle]
    slope: Optional[Slope]
    sed: Optional[Sediment]
```

**Methods:**
- `get()`: Copy grid files and generate namelist content
- `render_grid_nml()`: Generate GRID_NML content directly from namelist object
- `render_rect_nml()`: Generate RECT_NML content directly from namelist object

#### CurvGrid
```python
class CurvGrid(BaseGrid):
    grid_type: Literal["base"]
    model_type: Literal["ww3_curv"]
    grid_nml: Optional[GRID_NML]
    curv_nml: Optional[Curv]
    depth: Optional[Depth]
    mask: Optional[Mask]
    obst: Optional[Obstacle]
    slope: Optional[Slope]
    sed: Optional[Sediment]
    x_coord_file: Optional[Path]
    y_coord_file: Optional[Path]
```

**Methods:**
- `get()`: Copy grid files and generate namelist content
- `render_grid_nml()`: Generate GRID_NML content directly from namelist object
- `render_curv_nml()`: Generate CURV_NML content directly from namelist object

#### UnstGrid
```python
class UnstGrid(BaseGrid):
    grid_type: Literal["base"]
    model_type: Literal["ww3_unst"]
    grid_nml: Optional[GRID_NML]
    unst_nml: Optional[Unst]
    unst_obc_file: Optional[Path]
```

**Methods:**
- `get()`: Copy grid files and generate namelist content
- `render_grid_nml()`: Generate GRID_NML content directly from namelist object
- `render_unst_nml()`: Generate UNST_NML content directly from namelist object

#### SmcGrid
```python
class SmcGrid(BaseGrid):
    grid_type: Literal["base"]
    model_type: Literal["ww3_smc"]
    grid_nml: Optional[GRID_NML]
    smc_nml: Optional[Smc]
```

**Methods:**
- `get()`: Copy grid files and generate namelist content
- `render_grid_nml()`: Generate GRID_NML content directly from namelist object
- `render_smc_nml()`: Generate SMC_NML content directly from namelist object

#### AnyWw3Grid
```python
AnyWw3Grid = Union[RectGrid, CurvGrid, UnstGrid, SmcGrid]
```

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