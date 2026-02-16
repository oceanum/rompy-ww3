#!/usr/bin/env python3
"""WW3 mww3_test_08 multi-grid regression test configuration using rompy-ww3.

Test: ww3_multi with wind and ice input
Purpose: Validate multi-grid with atmospheric and ice forcing
Reference: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/mww3_test_08
"""

from rompy.model import ModelRun
from rompy.core.time import TimeRange
from rompy_ww3.config import NMLConfig
from rompy_ww3.components import Multi
from rompy_ww3.namelists import Domain
from rompy_ww3.namelists.input import (
    ModelGrid,
    ModelGridForcing,
    ModelGridResource,
    InputGrid,
    InputForcing,
)
from rompy_ww3.namelists.output_date import OutputDate, OutputDateField
from rompy_ww3.namelists.output_type import OutputType, OutputTypeField


def create_ww3_mww3_test_08_component():
    """Create rompy-ww3 Multi component for mww3_test_08 multi-grid test."""

    domain = Domain(
        start="20200101 000000",
        stop="20200102 000000",
        iostyp=1,
        nrinp=1,
        nrgrd=2,
    )

    input_grid = InputGrid(
        name="input",
        forcing=InputForcing(
            water_levels="F",
            currents="F",
            winds="T",
            ice_conc="T",
            
            
        ),
    )

    model_grid1 = ModelGrid(
        name="grd_a",
        forcing=ModelGridForcing(
            water_levels="F",
            currents="F",
            winds="T",
            ice_conc="T",
            
            
        ),
        resource=ModelGridResource(
            rank_id=1,
            group_id=1,
            comm_frac_start=0.00,
            comm_frac_end=0.50,
        ),
    )

    model_grid2 = ModelGrid(
        name="grd_b",
        forcing=ModelGridForcing(
            water_levels="F",
            currents="F",
            winds="T",
            ice_conc="T",
            
            
        ),
        resource=ModelGridResource(
            rank_id=2,
            group_id=1,
            comm_frac_start=0.50,
            comm_frac_end=1.00,
        ),
    )

    output_type = OutputType(
        field=OutputTypeField(list="HS FP DP DIR ICE WND"),
    )

    output_date = OutputDate(
        field=OutputDateField(
            start="20200101 000000",
            stride="3600",
            stop="20200102 000000",
        ),
    )

    multi_component = Multi(
        domain=domain,
        input_grid=input_grid,
        model_grids=[model_grid1, model_grid2],
        output_type=output_type,
        output_date=output_date,
    )

    return multi_component


def main():
    """Generate WW3 multi-grid configuration for mww3_test_08 regression test."""
    print("Creating WW3 multi-grid configuration for mww3_test_08 regression test...")
    print("Test: ww3_multi with wind and ice input")

    multi_component = create_ww3_mww3_test_08_component()
    config = NMLConfig(multi_component=multi_component)

    period = TimeRange(
        start="2020-01-01T00:00:00",
        end="2020-01-02T00:00:00",
        interval="1H",
    )

    model_run = ModelRun(
        run_id="ww3_mww3_test_08_regression",
        config=config,
        period=period,
        output_dir="rompy_runs",
    )
    model_run.generate()

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nGenerated namelists for mww3_test_08 test:")
    print("  - ww3_multi.nml: Multi-grid configuration")
    print("  - Configuration includes:")
    print("    * 2 model grids with input grid")
    print("    * Wind and ice forcing")
    print("    * Multi-grid forcing propagation")


if __name__ == "__main__":
    main()
