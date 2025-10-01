
# Relocatable Ocean Modelling in PYthon (rompy)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15093426.svg)](https://doi.org/10.5281/zenodo.15093426)
[![GitHub Pages](https://github.com/rom-py/rompy-ww3/actions/workflows/sphinx_docs_to_gh_pages.yaml/badge.svg)](https://rom-py.github.io/rompy-ww3/)
[![PyPI version](https://img.shields.io/pypi/v/rompy.svg)](https://pypi.org/project/rompy-ww3/)
[![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/rom-py/rompy-ww3/python-publish.yml)](https://github.com/rom-py/rompy-ww3/actions)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/rompy)](https://pypistats.org/packages/rompy)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rompy)](https://pypi.org/project/rompy/)

# Introduction

Relocatable Ocean Modelling in PYthon (rompy) is a modular Python library that
aims to streamline the setup, configuration, execution, and analysis of coastal
ocean models. Rompy combines templated model configuration with powerful
xarray-based data handling and pydantic validation, enabling users to
efficiently generate model control files and input datasets for a variety of
ocean and wave models. The architecture centers on high-level execution control
(`ModelRun`) and flexible configuration objects, supporting both persistent
scientific model state and runtime backend selection. Rompy provides unified
interfaces for grids, data sources, boundary conditions, and spectra, with
extensible plugin support for new models and execution environments.
Comprehensive documentation, example Jupyter notebooks, and a robust
logging/formatting framework make rompy accessible for both research and
operational workflows. Current model support includes SWAN and SCHISM, with
ongoing development for additional models and cloud/HPC backends.

Key Features:

- Modular architecture with clear separation of configuration and execution logic
- Templated, reproducible model configuration using pydantic and xarray
- Unified interfaces for grids, data, boundaries, and spectra
- Extensible plugin system for models, data sources, backends, and postprocessors
- Robust logging and formatting for consistent output and diagnostics
- Example notebooks and comprehensive documentation for rapid onboarding
- Support for local, Docker, and HPC execution backends

rompy is under active development—features, model support, and documentation are continually evolving. Contributions and feedback are welcome!

# WAVEWATCH III (WW3) Plugin

This package provides a plugin for the rompy framework to facilitate the setup,
configuration, and execution of WAVEWATCH III (WW3) models. It leverages
rompy's modular architecture to streamline the creation of WW3 model control
files, input datasets, and boundary conditions using templated configurations
and pydantic validation.

## Features

This package provides:

- Complete WW3 model configuration capabilities with all namelist components
- Integration with the rompy framework
- Comprehensive namelist generation for single-grid and multi-grid configurations
- Support for all WW3 model components: domain, input, output, forcing, boundary, grid, and more
- Ready-to-use examples including full model run configurations

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
- **NamelistComposer**: System for composing and validating complete namelist configurations

# Documentation

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

# Code Formatting and Pre-commit Hooks

This repository enforces Python code formatting using [black](https://github.com/psf/black) via the pre-commit framework.

To set up pre-commit hooks locally (required for all contributors)::

    pip install pre-commit
    pre-commit install

This will automatically check code formatting before each commit. To format your code manually, run::

    pre-commit run --all-files

All code must pass black formatting before it can be committed or merged.

# Versioning and Release

This project uses [tbump](https://github.com/dmerejkowsky/tbump) for version management.

To bump the version, run::

    tbump <new_version>

This will update the version in `src/rompy/__init__.py`, commit the change, and optionally create a git tag.

tbump is included in the development requirements (`requirements_dev.txt`).

For more advanced configuration, see `tbump.toml` in the project root.

# Relevant packages

> - [rompy](https://github.com/rom-py/rompy)
> - [rompy-swan](https://github.com/rom-py/rompy-swan)
> - [rompy-schism](https://github.com/rom-py/rompy-schism)
> - [rompy-notebooks](https://github.com/rom-py/rompy-notebooks)

.. image:: <https://img.shields.io/pypi/v/rompy_ww3.svg>
        :target: <https://pypi.python.org/pypi/rompy_ww3>

.. image:: <https://img.shields.io/travis/rom-py/rompy_ww3.svg>
        :target: <https://travis-ci.com/rom-py/rompy_ww3>

.. image:: <https://readthedocs.org/projects/rompy-ww3/badge/?version=latest>
        :target: <https://rompy-ww3.readthedocs.io/en/latest/?version=latest>
        :alt: Documentation Status

Rompy WW3 Config package.

- Free software: Apache Software License 2.0
- Documentation: <https://rompy-ww3.readthedocs.io>.

Features
--------

Code Formatting and Pre-commit Hooks
------------------------------------

This repository enforces Python code formatting using [black](https://github.com/psf/black) via the pre-commit framework.

To set up pre-commit hooks locally (required for all contributors)::

    pip install pre-commit
    pre-commit install

This will automatically check code formatting before each commit. To format your code manually, run::

    pre-commit run --all-files

All code must pass black formatting before it can be committed or merged.

Versioning and Release
----------------------

This project uses [tbump](https://github.com/dmerejkowsky/tbump) for version management.

To bump the version, run::

    tbump <new_version>

This will update the version in `src/rompy_ww3/__init__.py`, commit the change, and optionally create a git tag.

tbump is included in the development requirements (`requirements_dev.txt`).

For more advanced configuration, see `tbump.toml` in the project root.
