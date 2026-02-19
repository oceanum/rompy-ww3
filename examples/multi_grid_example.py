#!/usr/bin/env python
"""
Multi-grid example of using rompy-ww3 to configure a WW3 model.

This example demonstrates:
- Creating a multi-grid WW3 configuration
- Setting up different input and model grids
- Configuring coupling between grids
"""

from pathlib import Path

from rompy_ww3.config import Config
from rompy_ww3.grid import Grid
from rompy_ww3.namelists import (
    Domain,
    InputGrid,
    ModelGrid,
    OutputType,
    OutputDate,
    Spectrum,
    Run,
    Timesteps,
)
from rompy_ww3.namelists.input import InputForcing, ModelGridForcing, ModelGridResource
from rompy_ww3.namelists.output_date import (
    OutputDateField,
    OutputDatePoint,
    OutputDateRestart,
)


def main():
    print("Rompy-WW3 Multi-Grid Example")
    print("=" * 50)

    # 1. Create WW3 multi-grid configuration
    print("\n1. Creating WW3 multi-grid configuration...")

    # Domain for multi-grid setup
    domain = Domain(
        start="20230101 000000",
        stop="20230102 000000",
        iostyp=1,
        nrgrd=2,  # 2 model grids
        nrinp=1,  # 1 input grid
    )

    print(
        f"   Domain: {domain.start} to {domain.stop}, {domain.nrgrd} model grids, {domain.nrinp} input grid"
    )

    # Input grid configuration (e.g., global model)

    input_grid = InputGrid(
        name="global",
        forcing=InputForcing(
            water_levels="F",
            currents="F",
            winds="T",  # From files
            ice_conc="F",
            air_density="F",
            atm_momentum="F",
        ),
    )
    print(
        f"   Input grid: {input_grid.name}, winds forcing = {input_grid.forcing.winds}"
    )

    # Model grid configurations (e.g., regional models)
    model_grid1 = ModelGrid(
        name="region1",
        forcing=ModelGridForcing(
            winds="global",
            currents="no",
            water_levels="no",
            ice_conc="no",
        ),
        resource=ModelGridResource(
            rank_id=0,
            group_id=0,
            comm_frac_start=0.0,
            comm_frac_end=1.0,
        ),
    )
    print(f"   Model grid 1: {model_grid1.name}, rank {model_grid1.resource.rank_id}")

    model_grid2 = ModelGrid(
        name="region2",
        forcing=ModelGridForcing(
            winds="global",
            currents="no",
            water_levels="no",
            ice_conc="no",
        ),
        resource=ModelGridResource(
            rank_id=1,
            group_id=0,
            comm_frac_start=0.0,
            comm_frac_end=1.0,
        ),
    )
    print(f"   Model grid 2: {model_grid2.name}, rank {model_grid2.resource.rank_id}")

    # Grid configurations
    grid1 = Grid(
        model_type="ww3",
        grid_type="RECT",
        coordinate_system="SPHE",
        nx=50,
        ny=50,
        x0=-10.0,
        y0=40.0,
        dx=20.0 / 49,  # Calculate dx to span from x0 to x1
        dy=20.0 / 49,  # Calculate dy to span from y0 to y1
        name="region1_grid",
    )
    grid2 = Grid(
        model_type="ww3",
        grid_type="RECT",
        coordinate_system="SPHE",
        nx=40,
        ny=40,
        x0=-5.0,
        y0=45.0,
        dx=20.0 / 39,  # Calculate dx to span from x0 to x1
        dy=20.0 / 39,  # Calculate dy to span from y0 to y1
        name="region2_grid",
    )
    print(
        f"   Grid 1: {grid1.grid_type} ({grid1.nx}x{grid1.ny}) from {grid1.x0},{grid1.y0} with dx={grid1.dx:.3f}, dy={grid1.dy:.3f}"
    )
    print(
        f"   Grid 2: {grid2.grid_type} ({grid2.nx}x{grid2.ny}) from {grid2.x0},{grid2.y0} with dx={grid2.dx:.3f}, dy={grid2.dy:.3f}"
    )

    # Output configuration
    output_type = OutputType(
        field={"list": "HSIGN TMM10 TM02 PDIR PENT"},
        point={"file": "points.inp", "active": True},
        track={"format": 1},
        alltype={
            "field": {"list": "HSIGN TMM10 TM02 PDIR PENT"},
        },
        itype=[
            {"field": {"list": "HSIGN TMM10 TM02 PDIR PENT"}},
            {"field": {"list": "HSIGN TMM10 TM02 PDIR PENT"}},
        ],
    )
    print(f"   Output: Field variables = {output_type.field.list}")

    output_date = OutputDate(
        field=OutputDateField(
            start="20230101 000000", stride="3600", stop="20230102 000000"
        ),
        point=OutputDatePoint(
            start="20230101 000000", stride="3600", stop="20230102 000000"
        ),
        restart=OutputDateRestart(
            start="20230101 120000", stride="43200", stop="20230102 000000"
        ),
    )
    print(
        f"   Output dates: Field from {output_date.field.start} every {output_date.field.stride}s"
    )

    # Spectrum settings
    spectrum = Spectrum(xfr=1.1, freq1=0.03418, nth=24, thoff=0.0)
    print(f"   Spectrum: {spectrum.nth} directions, first freq {spectrum.freq1:.4f}")

    # Run settings
    run = Run(fldry=False, flcx=True, flcy=True, flcth=True, flck=True, flsou=True)
    print(f"   Run: Include source terms = {run.flsou}")

    # Timestep settings
    timesteps = Timesteps(dtmax=1800, dtxy=600, dtkth=900, dtmin=10)
    print(
        f"   Timesteps: Max = {timesteps.dtmax}s, XY = {timesteps.dtxy}s, KTH = {timesteps.dtkth}s"
    )

    # 2. Create the main WW3 multi-grid configuration
    print("\n2. Creating main WW3 multi-grid configuration...")
    config = Config(
        domain=domain,
        input_grid=input_grid,
        model_grid=model_grid1,  # The first model grid
        model_grids=[model_grid1, model_grid2],  # All model grids
        output_type=output_type,
        output_date=output_date,
        spectrum=spectrum,
        run=run,
        timesteps=timesteps,
        grids=[grid1, grid2],  # All grids
    )
    print(f"   Multi-grid configuration created with model type: {config.model_type}")

    # 3. Create a staging directory and generate namelist files
    print("\n3. Generating WW3 namelist files...")
    staging_dir = Path("multi_grid_example_output")
    staging_dir.mkdir(exist_ok=True)

    # Generate all namelist files using the config's __call__ method
    # We'll create a mock runtime object for this example
    class MockRuntime:
        def __init__(self):
            self.staging_dir = str(staging_dir)

    runtime = MockRuntime()
    result = config(runtime)

    print(f"   Namelist files generated in: {result['namelists_dir']}")

    # List the generated files
    namelists_path = Path(result["namelists_dir"])
    for file_path in namelists_path.iterdir():
        if file_path.is_file():
            print(f"   - {file_path.name}")

    # 4. Show a summary
    print("\n4. Multi-Grid Configuration Summary")
    print("=" * 35)
    print(f"Model run: {domain.start} to {domain.stop}")
    print(f"Number of model grids: {domain.nrgrd}")
    print(f"Number of input grids: {domain.nrinp}")
    print(f"Output variables: {output_type.field.list}")
    print(f"Time step: {timesteps.dtxy} seconds")

    print("\nExample completed successfully!")
    print(
        f"\nYou can now run multi-grid WW3 with the generated namelist files in {staging_dir}/namelists/"
    )


if __name__ == "__main__":
    main()
