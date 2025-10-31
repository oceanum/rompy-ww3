# Components API Reference

This section documents the various WW3 component classes available in rompy-ww3. Each component represents a specific WW3 executable and its configuration through associated namelist objects.

## Base Component

The base WW3 component model provides common functionality for all WW3 components including rendering, file writing, and namelist management.

::: rompy_ww3.components.basemodel.WW3ComponentBaseModel
    handler: python
    options:
      show_root_heading: true
      show_root_full_path: false
      show_object_full_path: false
      show_category_heading: true
      show_if_no_docstring: true
      show_signature_annotations: true
      signature_crossrefs: true
      separate_signature: true
      docstring_section_style: table
      members_order: source
      group_by_category: true
      show_submodules: false
      filters:
        - "!^_"  # Hide private members by default

## Shell Component

The Shell component handles the main WW3 shell program configuration (ww3_shel.nml).

::: rompy_ww3.components.shel.Shel
    handler: python
    options:
      show_root_heading: true
      show_root_full_path: false
      show_object_full_path: false
      show_category_heading: true
      show_if_no_docstring: true
      show_signature_annotations: true
      signature_crossrefs: true
      separate_signature: true
      docstring_section_style: table
      members_order: source
      group_by_category: true
      show_submodules: false
      filters:
        - "!^_"  # Hide private members by default

## Grid Component

The Grid component handles WW3 grid preprocessing configuration (ww3_grid.nml).

::: rompy_ww3.components.grid.Grid
    handler: python
    options:
      show_root_heading: true
      show_root_full_path: false
      show_object_full_path: false
      show_category_heading: true
      show_if_no_docstring: true
      show_signature_annotations: true
      signature_crossrefs: true
      separate_signature: true
      docstring_section_style: table
      members_order: source
      group_by_category: true
      show_submodules: false
      filters:
        - "!^_"  # Hide private members by default

## Multi-Grid Component

The Multi component handles multi-grid WW3 configuration (ww3_multi.nml).

::: rompy_ww3.components.multi.Multi
    handler: python
    options:
      show_root_heading: true
      show_root_full_path: false
      show_object_full_path: false
      show_category_heading: true
      show_if_no_docstring: true
      show_signature_annotations: true
      signature_crossrefs: true
      separate_signature: true
      docstring_section_style: table
      members_order: source
      group_by_category: true
      show_submodules: false
      filters:
        - "!^_"  # Hide private members by default

## Boundary Conditions Component

The Bounc component handles WW3 boundary condition generation (ww3_bounc.nml).

::: rompy_ww3.components.bounc.Bounc
    handler: python
    options:
      show_root_heading: true
      show_root_full_path: false
      show_object_full_path: false
      show_category_heading: true
      show_if_no_docstring: true
      show_signature_annotations: true
      signature_crossrefs: true
      separate_signature: true
      docstring_section_style: table
      members_order: source
      group_by_category: true
      show_submodules: false
      filters:
        - "!^_"  # Hide private members by default

## Boundary Data Component

The BounD component handles WW3 boundary data extraction (ww3_bound.nml).

::: rompy_ww3.components.bound.Bound
    handler: python
    options:
      show_root_heading: true
      show_root_full_path: false
      show_object_full_path: false
      show_category_heading: true
      show_if_no_docstring: true
      show_signature_annotations: true
      signature_crossrefs: true
      separate_signature: true
      docstring_section_style: table
      members_order: source
      group_by_category: true
      show_submodules: false
      filters:
        - "!^_"  # Hide private members by default

## Preprocessor Component

The Prnc component handles WW3 preprocessor configuration (ww3_prnc.nml).

::: rompy_ww3.components.prnc.Prnc
    handler: python
    options:
      show_root_heading: true
      show_root_full_path: false
      show_object_full_path: false
      show_category_heading: true
      show_if_no_docstring: true
      show_signature_annotations: true
      signature_crossrefs: true
      separate_signature: true
      docstring_section_style: table
      members_order: source
      group_by_category: true
      show_submodules: false
      filters:
        - "!^_"  # Hide private members by default

## Track Component

The Trnc component handles WW3 track processor configuration (ww3_trnc.nml).

::: rompy_ww3.components.trnc.Trnc
    handler: python
    options:
      show_root_heading: true
      show_root_full_path: false
      show_object_full_path: false
      show_category_heading: true
      show_if_no_docstring: true
      show_signature_annotations: true
      signature_crossrefs: true
      separate_signature: true
      docstring_section_style: table
      members_order: source
      group_by_category: true
      show_submodules: false
      filters:
        - "!^_"  # Hide private members by default

## Output Fields Component

The Ounf component handles WW3 field output configuration (ww3_ounf.nml).

::: rompy_ww3.components.ounf.Ounf
    handler: python
    options:
      show_root_heading: true
      show_root_full_path: false
      show_object_full_path: false
      show_category_heading: true
      show_if_no_docstring: true
      show_signature_annotations: true
      signature_crossrefs: true
      separate_signature: true
      docstring_section_style: table
      members_order: source
      group_by_category: true
      show_submodules: false
      filters:
        - "!^_"  # Hide private members by default

## Output Points Component

The Ounp component handles WW3 point output configuration (ww3_ounp.nml).

::: rompy_ww3.components.ounp.Ounp
    handler: python
    options:
      show_root_heading: true
      show_root_full_path: false
      show_object_full_path: false
      show_category_heading: true
      show_if_no_docstring: true
      show_signature_annotations: true
      signature_crossrefs: true
      separate_signature: true
      docstring_section_style: table
      members_order: source
      group_by_category: true
      show_submodules: false
      filters:
        - "!^_"  # Hide private members by default

## Restart Update Component

The Uptstr component handles WW3 restart update configuration (ww3_upstr.nml).

::: rompy_ww3.components.uptstr.Uptstr
    handler: python
    options:
      show_root_heading: true
      show_root_full_path: false
      show_object_full_path: false
      show_category_heading: true
      show_if_no_docstring: true
      show_signature_annotations: true
      signature_crossrefs: true
      separate_signature: true
      docstring_section_style: table
      members_order: source
      group_by_category: true
      show_submodules: false
      filters:
        - "!^_"  # Hide private members by default

## Physics Parameters Component

The Namelists component handles WW3 physics parameter configuration for source terms, propagation schemes, and other model physics (namelists.nml).

::: rompy_ww3.components.namelists.Namelists
    handler: python
    options:
      show_root_heading: true
      show_root_full_path: false
      show_object_full_path: false
      show_category_heading: true
      show_if_no_docstring: true
      show_signature_annotations: true
      signature_crossrefs: true
      separate_signature: true
      docstring_section_style: table
      members_order: source
      group_by_category: true
      show_submodules: false
      filters:
        - "!^_"  # Hide private members by default