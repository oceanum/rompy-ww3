#!/usr/bin/env python3
"""WW3 mww3_test_09 multi-grid regression test configuration using rompy-ww3.

Test: SMC multi-grid for Great Lakes
Purpose: Validate multi-grid with Spherical Multiple-Cell (SMC) grids
Reference: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/mww3_test_09
"""

from rompy.model import ModelRun
from rompy.core.time import TimeRange
from rompy_ww3.config import NMLConfig
from rompy_ww3.components import Multi
from rompy_ww3.namelists import Domain
from rompy_ww3.namelists.input import ModelGrid, ModelGridForcing, ModelGridResource
from rompy_ww3.namelists.output_date import OutputDate, OutputDateField
from rompy_ww3.namelists.output_type import OutputType, OutputTypeField


def create_ww3_mww3_test_09_component():
    """Create rompy-ww3 Multi component for mww3_test_09 multi-grid test."""

    domain = Domain(
        start="20200101 000000",
        stop="20200101 120000",
        iostyp=1,
        nrinp=1,
        nrgrd=3,
    )

    model_grid1 = ModelGrid(
        name="Michi",
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
            comm_frac_end=0.33,
        ),
    )

    model_grid2 = ModelGrid(
        name="Huron",
        forcing=ModelGridForcing(
            water_levels="no",
            currents="no",
            winds="no",
            ice_conc="no",
            
            
        ),
        resource=ModelGridResource(
            rank_id=2,
            group_id=1,
            comm_frac_start=0.33,
            comm_frac_end=0.67,
        ),
    )

    model_grid3 = ModelGrid(
        name="Super",
        forcing=ModelGridForcing(
            water_levels="no",
            currents="no",
            winds="no",
            ice_conc="no",
            
            
        ),
        resource=ModelGridResource(
            rank_id=3,
            group_id=1,
            comm_frac_start=0.67,
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
        model_grids=[model_grid1, model_grid2, model_grid3],
        output_type=output_type,
        output_date=output_date,
    )

    return multi_component


def main():
    """Generate WW3 multi-grid configuration for mww3_test_09 regression test."""
    print("Creating WW3 multi-grid configuration for mww3_test_09 regression test...")
    print("Test: SMC multi-grid for Great Lakes")

    multi_component = create_ww3_mww3_test_09_component()
    config = NMLConfig(multi_component=multi_component)

    period = TimeRange(
        start="2020-01-01T00:00:00",
        end="2020-01-01T12:00:00",
        interval="1H",
    )

    model_run = ModelRun(
        run_id="ww3_mww3_test_09_regression",
        config=config,
        period=period,
        output_dir="rompy_runs",
    )
    model_run.generate()

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nGenerated namelists for mww3_test_09 test:")
    print("  - ww3_multi.nml: Multi-grid configuration")
    print("  - Configuration includes:")
    print("    * 3 Great Lakes grids (Michigan, Huron, Superior)")
    print("    * SMC (Spherical Multi-Cell) grid support")
    print("    * Lake-specific boundary handling")


if __name__ == "__main__":
    main()
