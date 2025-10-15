# WW3 Configuration Schema

The rompy-ww3 Config object defines the complete configuration for a WAVEWATCH III (WW3) model run. This includes all namelist components, data sources, and grid configurations required to set up and execute a WW3 model.

## Complete Configuration Schema

<div id="redoc-container" style="margin: 20px 0; border: 1px solid #ddd; border-radius: 4px; min-height: 600px;"></div>

<style>
  #redoc-container {
    position: relative;
  }
  #redoc-container redoc {
    display: block;
  }
</style>

<script src="https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js"></script>
<script>
  Redoc.init(
    '../config_schema.json',
    {
      scrollYOffset: 50,
      hideHostname: false,
      hideLoading: true,
      expandResponses: 'all',
      requiredPropsFirst: true,
      sortPropsAlphabetically: true,
    },
    document.getElementById('redoc-container')
  );
</script>

## Description

This schema represents the Pydantic model for the WW3 configuration. It includes:

- Domain configuration (domain)
- Input data specifications (input_nml, input_grid, model_grid)
- Output specifications (output_type, output_date)
- Grid configurations (grid, grids, rect)
- Boundary conditions (bound, forcing)
- All other WW3 namelist components

Each component can be individually configured to control different aspects of the WW3 model run.