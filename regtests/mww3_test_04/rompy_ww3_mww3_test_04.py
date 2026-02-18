#!/usr/bin/env python3
"""WW3 mww3_test_04 multi-grid regression test configuration using rompy-ww3.

Test: Static nesting with lateral boundary data from file
Purpose: Validate propagation with boundary conditions and inner grid with
         shallow water and/or currents
Reference: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/mww3_test_04
"""

from rompy.model import ModelRun
from rompy.core.time import TimeRange
from rompy_ww3.config import NMLConfig
from rompy_ww3.components import Multi
from rompy_ww3.namelists import Domain
from rompy_ww3.namelists.input import ModelGrid, ModelGridForcing, ModelGridResource
from rompy_ww3.namelists.output_date import OutputDate, OutputDateField
from rompy_ww3.namelists.output_type import OutputType, OutputTypeField


def create_ww3_mww3_test_04_component():
    """Create rompy-ww3 Multi component for mww3_test_04 multi-grid test."""

    domain = Domain(
        start="20200101 000000",
        stop="20200101 120000",
        iostyp=1,
        nrinp=1,
        nrgrd=3,
    )

    # Boundary grid - 1-D propagation with preset boundary data
    model_grid_bound = ModelGrid(
        name="bound",
        forcing=ModelGridForcing(
            water_levels="no",
            currents="no",
            winds="no",
            ice_conc="no",
            
            
        ),
        resource=ModelGridResource(
            rank_id=1,
            group_id=1,
            comm_frac_start=0.00,
            comm_frac_end=0.25,
        ),
    )

    # Outer grid - full 2-D propagation with constant depth
    model_grid_outer = ModelGrid(
        name="outer",
        forcing=ModelGridForcing(
            water_levels="no",
            currents="no",
            winds="no",
            ice_conc="no",
            
            
        ),
        resource=ModelGridResource(
            rank_id=2,
            group_id=1,
            comm_frac_start=0.25,
            comm_frac_end=0.60,
        ),
    )

    # Inner grid - higher resolution with shallow water
    model_grid_inner = ModelGrid(
        name="inner",
        forcing=ModelGridForcing(
            water_levels="no",
            currents="no",
            winds="no",
            ice_conc="no",
            
            
        ),
        resource=ModelGridResource(
            rank_id=3,
            group_id=1,
            comm_frac_start=0.60,
            comm_frac_end=1.00,
        ),
    )

    output_type = OutputType(
        field=OutputTypeField(list="HS FP DP DIR"),
    )

    output_date = OutputDate(
        field=OutputDateField(
            start="20200101 000000",
            stride="3600",
            stop="20200101 120000",
        ),
    )

    multi_component = Multi(
        domain=domain,
        model_grids=[model_grid_bound, model_grid_outer, model_grid_inner],
        output_type=output_type,
        output_date=output_date,
    )

    return multi_component


def main():
    """Generate WW3 multi-grid configuration for mww3_test_04 regression test."""
    print("Creating WW3 multi-grid configuration for mww3_test_04 regression test...")
    print("Test: Static nesting with lateral boundary data from file")

    multi_component = create_ww3_mww3_test_04_component()
    config = NMLConfig(multi_component=multi_component)

    period = TimeRange(
        start="2020-01-01T00:00:00",
        end="2020-01-01T12:00:00",
        interval="1h",
    )

    model_run = ModelRun(
        run_id="ww3_mww3_test_04_regression",
        config=config,
        period=period,
        output_dir="rompy_runs",
    )
    model_run.generate()

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nGenerated namelists for mww3_test_04 test:")
    print("  - ww3_multi.nml: Multi-grid configuration")
    print("  - Configuration includes:")
    print("    * 3 model grids (bound, outer, inner)")
    print("    * Boundary grid with 1-D propagation")
    print("    * Inner grid with shallow water support")
    print("    * No source terms (propagation only)")


if __name__ == "__main__":
    main()
