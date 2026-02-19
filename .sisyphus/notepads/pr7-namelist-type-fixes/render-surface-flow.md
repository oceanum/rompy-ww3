# Render/Serialization Surface: Namelist Flow

- Overview: Capture the end-to-end path from namelist model objects to final string blocks and .nml files, without changing code behavior.
- Entry points and call sites:
- - WW3ComponentBaseModel.render() and per-component render() implementations (src/rompy_ww3/namelists and src/rompy_ww3/components).
- - Namelist composer (src/rompy_ww3/namelists) wires renders into keys like domain.nml, input.nml, etc.
- - write_nml() emissions (src/rompy_ww3/namelists/basemodel.py and component wrappers in config.py and components/*).
- Template usage:
- - Jinja2 templates found in: src/rompy_ww3/templates/base/run_ww3.j2 and ww3_shel.nml, plus context generation in source.py and config.py.
- Output artifacts:
- - In-memory namelist strings, and emitted *.nml files on disk when write_nml() is invoked.
- Validation approach:
- - Confirm that rendering relies on a consistent render() surface across components and that templates only substitute values via their context, not performing ad-hoc string manipulation.
