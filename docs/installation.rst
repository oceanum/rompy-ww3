============
Installation
============

Stable release
--------------

To install rompy-ww3, run this command in your terminal:

.. code-block:: console

    $ pip install rompy-ww3

This is the preferred method to install rompy-ww3, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

From sources
------------

The sources for rompy-ww3 can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/your-org/rompy-ww3

Or download the `tarball`_:

.. code-block:: console

    $ curl -OJL https://github.com/your-org/rompy-ww3/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ pip install .

Or, for development:

.. code-block:: console

    $ pip install -e .

Development Installation
------------------------

For development work, install the package in editable mode with development dependencies:

.. code-block:: console

    $ pip install -e .
    $ pip install -r requirements_dev.txt

This will install all dependencies needed for development, including:

- Testing dependencies (pytest)
- Linting dependencies (ruff)
- Documentation dependencies (sphinx)
- Pre-commit hooks for code formatting

Pre-commit Hooks
----------------

To set up pre-commit hooks for automatic code formatting and linting:

.. code-block:: console

    $ pre-commit install

This will ensure that all code is properly formatted before commits.

Dependencies
------------

rompy-ww3 requires:

- Python 3.8 or higher
- rompy (core framework)
- pydantic (for configuration validation)
- typer (for CLI)
- rich (for rich terminal output)

These dependencies will be automatically installed when you install rompy-ww3.

WW3 Model Requirements
----------------------

To actually run WW3 models, you will also need:

- The WW3 model binaries installed on your system
- Appropriate computational resources
- Input data files in supported formats

See the WW3 documentation for detailed installation instructions for the model itself.