#!/usr/bin/env python3
"""WW3 mww3_test_07 multi-grid regression test configuration using rompy-ww3.

Test: Rectangular grid with triangular mesh (unstructured)
Purpose: Validate multi-grid with unstructured grids containing islands
Reference: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/mww3_test_07
"""

from rompy.model import ModelRun
from rompy.core.time import TimeRange
from rompy_ww3.config import NMLConfig
from rompy_ww3.components import Multi
from rompy_ww3.namelists import Domain
from rompy_ww3.namelists.input import ModelGrid, ModelGridForcing, ModelGridResource
from rompy_ww3.namelists.output_date import OutputDate, OutputDateField
from rompy_ww3.namelists.output_type import OutputType, OutputTypeField


def create_ww3_mww3_test_07_component():
    """Create rompy-ww3 Multi component for mww3_test_07 multi-grid test."""

    domain = Domain(
        start="20200101 000000",
        stop="20200101 060000",
        iostyp=1,
        nrinp=1,
        nrgrd=2,
    )

    model_grid1 = ModelGrid(
        name="parent",
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
            comm_frac_end=0.50,
        ),
    )

    model_grid2 = ModelGrid(
        name="refug",
        forcing=ModelGridForcing(
            water_levels="no",
            currents="no",
            winds="no",
            ice_conc="no",
            
            
        ),
        resource=ModelGridResource(
            rank_id=2,
            group_id=1,
            comm_frac_start=0.50,
            comm_frac_end=1.00,
        ),
    )

    output_type = OutputType(
        field=OutputTypeField(list="HS FP DP DIR DPT"),
    )

    output_date = OutputDate(
        field=OutputDateField(
            start="20200101 000000",
            stride="1800",
            stop="20200101 060000",
        ),
    )

    multi_component = Multi(
        domain=domain,
        model_grids=[model_grid1, model_grid2],
        output_type=output_type,
        output_date=output_date,
    )

    return multi_component


def main():
    """Generate WW3 multi-grid configuration for mww3_test_07 regression test."""
    print("Creating WW3 multi-grid configuration for mww3_test_07 regression test...")
    print("Test: Rectangular grid with triangular mesh (unstructured)")

    multi_component = create_ww3_mww3_test_07_component()
    config = NMLConfig(multi_component=multi_component)

    period = TimeRange(
        start="2020-01-01T00:00:00",
        end="2020-01-01T06:00:00",
        interval="30m",
    )

    model_run = ModelRun(
        run_id="ww3_mww3_test_07_regression",
        config=config,
        period=period,
        output_dir="rompy_runs",
    )
    model_run.generate()

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nGenerated namelists for mww3_test_07 test:")
    print("  - ww3_multi.nml: Multi-grid configuration")
    print("  - Configuration includes:")
    print("    * 2 model grids (parent + refug)")
    print("    * Rectangular parent grid")
    print("    * Unstructured grid with island")


if __name__ == "__main__":
    main()
