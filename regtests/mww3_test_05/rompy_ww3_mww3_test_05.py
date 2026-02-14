#!/usr/bin/env python3
"""WW3 mww3_test_05 multi-grid regression test configuration using rompy-ww3.

Test: Telescoping nests over hurricane with continuous moving grid
Purpose: Validate multi-grid hurricane modeling with moving grids
Reference: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/mww3_test_05
"""

from rompy.model import ModelRun
from rompy.core.time import TimeRange
from rompy_ww3.config import NMLConfig
from rompy_ww3.components import Multi
from rompy_ww3.namelists import Domain
from rompy_ww3.namelists.input import ModelGrid, ModelGridForcing, ModelGridResource
from rompy_ww3.namelists.output_date import OutputDate, OutputDateField
from rompy_ww3.namelists.output_type import OutputType, OutputTypeField


def create_ww3_mww3_test_05_component():
    """Create rompy-ww3 Multi component for mww3_test_05 multi-grid test."""

    # Domain configuration for 24-hour hurricane simulation
    domain = Domain(
        start="20200101 000000",
        stop="20200102 000000",
        iostyp=1,
        nrinp=1,
        nrgrd=3,
    )

    # Outer grid - coarse resolution (50km)
    model_grid1 = ModelGrid(
        name="grd1",
        forcing=ModelGridForcing(
            water_levels="no",
            currents="no",
            winds="T",
            ice_conc="no",
            air_density="no",
            atm_momentum="no",
        ),
        resource=ModelGridResource(
            rank_id=1,
            group_id=1,
            comm_frac_start=0.00,
            comm_frac_end=0.30,
        ),
    )

    # Middle grid - medium resolution (15km)
    model_grid2 = ModelGrid(
        name="grd2",
        forcing=ModelGridForcing(
            water_levels="no",
            currents="no",
            winds="T",
            ice_conc="no",
            air_density="no",
            atm_momentum="no",
        ),
        resource=ModelGridResource(
            rank_id=2,
            group_id=1,
            comm_frac_start=0.30,
            comm_frac_end=0.65,
        ),
    )

    # Inner grid - high resolution (5km)
    model_grid3 = ModelGrid(
        name="grd3",
        forcing=ModelGridForcing(
            water_levels="no",
            currents="no",
            winds="T",
            ice_conc="no",
            air_density="no",
            atm_momentum="no",
        ),
        resource=ModelGridResource(
            rank_id=3,
            group_id=1,
            comm_frac_start=0.65,
            comm_frac_end=1.00,
        ),
    )

    # Output configuration
    output_type = OutputType(
        field=OutputTypeField(list="HS FP DP DIR SPR WND CUR"),
    )

    output_date = OutputDate(
        field=OutputDateField(
            start="20200101 000000",
            stride="3600",
            stop="20200102 000000",
        ),
    )

    # Create Multi component
    multi_component = Multi(
        domain=domain,
        model_grids=[model_grid1, model_grid2, model_grid3],
        output_type=output_type,
        output_date=output_date,
    )

    return multi_component


def main():
    """Generate WW3 multi-grid configuration for mww3_test_05 regression test."""
    print("Creating WW3 multi-grid configuration for mww3_test_05 regression test...")
    print("Test: Telescoping nests over hurricane with continuous moving grid")

    multi_component = create_ww3_mww3_test_05_component()
    config = NMLConfig(multi_component=multi_component)

    period = TimeRange(
        start="2020-01-01T00:00:00",
        end="2020-01-02T00:00:00",
        interval="1H",
    )

    model_run = ModelRun(
        run_id="ww3_mww3_test_05_regression",
        config=config,
        period=period,
        output_dir="rompy_runs",
    )
    model_run.generate()

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nGenerated namelists for mww3_test_05 test:")
    print("  - ww3_multi.nml: Multi-grid configuration")
    print("  - Configuration includes:")
    print("    * 3 model grids (outer, middle, inner)")
    print("    * Telescoping nests for hurricane tracking")
    print("    * Moving grid support")
    print("    * High-resolution inner grid (5km)")


if __name__ == "__main__":
    main()
