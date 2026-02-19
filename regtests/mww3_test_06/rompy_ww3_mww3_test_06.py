#!/usr/bin/env python3
"""WW3 mww3_test_06 multi-grid regression test configuration using rompy-ww3.

Test: Irregular grids with ww3_multi (curvilinear grids)
Purpose: Validate multi-grid with irregular/curvilinear grid types
Reference: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/mww3_test_06
"""

from rompy.model import ModelRun
from rompy.core.time import TimeRange
from rompy_ww3.config import NMLConfig
from rompy_ww3.components import Multi
from rompy_ww3.namelists import Domain
from rompy_ww3.namelists.input import ModelGrid, ModelGridForcing, ModelGridResource
from rompy_ww3.namelists.output_date import OutputDate, OutputDateField
from rompy_ww3.namelists.output_type import OutputType, OutputTypeField


def create_ww3_mww3_test_06_component():
    """Create rompy-ww3 Multi component for mww3_test_06 multi-grid test."""

    # Domain configuration for 6-hour curvilinear grid test
    domain = Domain(
        start="20200101 000000",
        stop="20200101 060000",
        iostyp=1,
        nrinp=1,
        nrgrd=2,
    )

    # Global band grid - regular lat/lon subset
    model_grid1 = ModelGrid(
        name="gband360",
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

    # Arctic subset grid - curvilinear
    model_grid2 = ModelGrid(
        name="arcticsub",
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

    # Output configuration
    output_type = OutputType(
        field=OutputTypeField(list="HS FP DP DIR"),
    )

    output_date = OutputDate(
        field=OutputDateField(
            start="20200101 000000",
            stride=3600,
            stop="20200101 060000",
        ),
    )

    # Create Multi component
    multi_component = Multi(
        domain=domain,
        model_grids=[model_grid1, model_grid2],
        output_type=output_type,
        output_date=output_date,
    )

    return multi_component


def main():
    """Generate WW3 multi-grid configuration for mww3_test_06 regression test."""
    print("Creating WW3 multi-grid configuration for mww3_test_06 regression test...")
    print("Test: Irregular grids with ww3_multi (curvilinear grids)")

    multi_component = create_ww3_mww3_test_06_component()
    config = NMLConfig(multi_component=multi_component)

    period = TimeRange(
        start="2020-01-01T00:00:00",
        end="2020-01-01T06:00:00",
        interval="1H",
    )

    model_run = ModelRun(
        run_id="ww3_mww3_test_06_regression",
        config=config,
        period=period,
        output_dir="rompy_runs",
    )
    model_run.generate()

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nGenerated namelists for mww3_test_06 test:")
    print("  - ww3_multi.nml: Multi-grid configuration")
    print("  - Configuration includes:")
    print("    * 2 model grids (regular + curvilinear)")
    print("    * Global band grid (gband360)")
    print("    * Arctic subset grid (arcticsub)")
    print("    * SCRIP regridding support")


if __name__ == "__main__":
    main()
