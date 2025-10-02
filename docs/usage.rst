=====
Usage
=====

To use rompy-ww3 in a project::

    import rompy_ww3

Basic Configuration
===================

The basic usage pattern involves creating a ``Config`` object with the desired WW3 namelist components:

.. code-block:: python

    from rompy_ww3.config import Config
    from rompy_ww3.namelists import Domain, Input, OutputType, OutputDate

    # Create a basic configuration
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
        ),
        output_type=OutputType(
            field={"list": "HS DIR SPR WND LEV"}
        ),
        output_date=OutputDate(
            field={
                "start": "20230101 000000",
                "stride": "3600",
                "stop": "20230107 000000"
            }
        )
    )

Generating Namelist Files
=========================

Once you have a configuration, you can generate the WW3 namelist files:

.. code-block:: python

    from rompy.core.runtime import Runtime
    import tempfile

    # Create a runtime object (in a real application, this would be provided)
    with tempfile.TemporaryDirectory() as tmpdir:
        runtime = type('Runtime', (), {'staging_dir': tmpdir})()
        
        # Generate namelist files
        result = config(runtime)
        
        print(f"Namelist files generated in: {result['namelists_dir']}")

Using the Namelist Composition System
=====================================

For more advanced usage, you can use the ``NamelistComposition`` class:

.. code-block:: python

    from rompy_ww3.namelist_composer import NamelistComposition

    # Create a composition from the config
    composition = NamelistComposition.from_config(config)

    # Validate the configuration
    completeness_issues = composition.validate_completeness()
    consistency_issues = composition.validate_consistency()

    if not completeness_issues and not consistency_issues:
        print("Configuration is valid!")

        # Render all namelists
        all_namelists = composition.render_all_namelists()

        # Write all namelists to files
        composition.write_all_namelists("/path/to/output/directory")

Working with Grids
==================

Configure WW3 grids using the ``Grid`` class:

.. code-block:: python

    from rompy_ww3.grid import Grid

    # Create a grid configuration
    grid = Grid(
        x0=-10.0,    # Western boundary
        y0=20.0,     # Southern boundary
        dx=0.1,      # Grid spacing in x-direction
        dy=0.1,      # Grid spacing in y-direction
        nx=200,      # Number of grid points in x-direction
        ny=100       # Number of grid points in y-direction
    )

    # Set WW3-specific parameters
    grid.name = "Example Regional Grid"
    grid.grid_type = "RECT"
    grid.coordinate_system = "SPHE"

Working with Data Sources
=========================

Configure data sources using the ``Data`` and ``Ww3Source`` classes:

.. code-block:: python

    from rompy_ww3.data import Data
    from rompy_ww3.source import Ww3Source
    from rompy.core.source import SourceFile

    # Create a wind data source
    wind_source = Ww3Source(
        uri="/path/to/wind_data.nc",
        data_type="winds",
        file_format="netcdf",
        variable_mapping={
            "u_wind": "u10",
            "v_wind": "v10"
        }
    )

    # Create a data object
    wind_data = Data(source=wind_source)
    wind_data.forcing_flag = "T"  # From external file

Generating Run Scripts
======================

Generate a run script for executing the WW3 model:

.. code-block:: python

    from pathlib import Path

    # Generate a run script
    script_path = config.generate_run_script(Path("/path/to/model/directory"))
    print(f"Run script generated: {script_path}")

Template Context Generation
===========================

Generate template context for use with Jinja2 templates:

.. code-block:: python

    # Generate template context
    context = config.get_template_context()

    # Access specific context items
    start_time = context.get('start_time')
    output_fields = context.get('output_fields')
    namelists = context.get('namelists')

Examples
========

See the ``examples/`` directory for complete examples including:

1. Basic configuration examples (``examples/namelist_example.py``)
2. Complete workflow examples (``examples/complete_workflow.py``)
3. Jupyter notebooks demonstrating various aspects of the system