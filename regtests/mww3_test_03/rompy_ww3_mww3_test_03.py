#!/usr/bin/env python3
"""
WW3 mww3_test_03 multi-grid regression test configuration using rompy-ww3.

Test: Advanced multi-grid configuration with 3 grids and extended features.
Purpose: Validate advanced multi-grid capabilities including differential forcing,
         non-uniform resource allocation, and comprehensive output configurations.
Reference: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/mww3_test_03
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
)
from rompy_ww3.namelists.output_date import OutputDate, OutputDateField
from rompy_ww3.namelists.output_type import OutputType, OutputTypeField


def create_ww3_mww3_test_03_component():
    """Create rompy-ww3 Multi component for mww3_test_03 advanced multi-grid test."""

    domain = Domain(
        start="20200101 000000",
        stop="20200102 120000",
        iostyp=1,
        nrinp=1,
        nrgrd=3,
    )

    model_grid1 = ModelGrid(
        name="coarse",
        forcing=ModelGridForcing(
            water_levels="no",
            currents="T",
            winds="T",
            ice_conc="no",
        ),
        resource=ModelGridResource(
            rank_id=1,
            group_id=1,
            comm_frac_start=0.00,
            comm_frac_end=0.30,
        ),
    )

    model_grid2 = ModelGrid(
        name="medium",
        forcing=ModelGridForcing(
            water_levels="no",
            currents="T",
            winds="T",
            ice_conc="no",
        ),
        resource=ModelGridResource(
            rank_id=2,
            group_id=1,
            comm_frac_start=0.30,
            comm_frac_end=0.65,
        ),
    )

    model_grid3 = ModelGrid(
        name="fine",
        forcing=ModelGridForcing(
            water_levels="T",
            currents="T",
            winds="T",
            ice_conc="no",
        ),
        resource=ModelGridResource(
            rank_id=3,
            group_id=1,
            comm_frac_start=0.65,
            comm_frac_end=1.00,
        ),
    )

    output_type = OutputType(
        field=OutputTypeField(
            list="HS FP DP DIR SPR WND CUR WCC WCF WCH WCM T02 T01 T0M1 FP0 THP0 THS EF TH1M TH2M"
        ),
    )

    output_date = OutputDate(
        field=OutputDateField(
            start="20200101 000000",
            stride=900,
            stop="20200102 120000",
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
    """Generate WW3 multi-grid configuration for mww3_test_03 regression test."""
    print("Creating WW3 multi-grid configuration for mww3_test_03 regression test...")
    print("Test: Advanced multi-grid with 3 grids and extended features")

    multi_component = create_ww3_mww3_test_03_component()

    config = NMLConfig(multi_component=multi_component)

    period = TimeRange(start="2020-01-01T00:00:00", duration="36H", interval="15m")

    model_run = ModelRun(
        run_id="ww3_mww3_test_03_regression",
        config=config,
        period=period,
        output_dir="rompy_runs",
    )
    model_run.generate()

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nGenerated namelists for mww3_test_03 test:")
    print("  - ww3_multi.nml: Advanced multi-grid configuration")
    print("  - Configuration includes:")
    print("    * 3 model grids with differential forcing")
    print("    * Comprehensive output field list (20+ variables)")
    print("    * High-frequency output (every 15 minutes)")
    print("    * Water levels enabled on fine grid only")
    print("    * Currents enabled on all three grids")
    print("    * Non-uniform resource allocation (30%/35%/35%)")
    print("    * Extended simulation duration (1.5 days)")
    print("\nThis test demonstrates advanced WW3 multi-grid capabilities:")
    print("  - Differential forcing per grid (water levels on fine only)")
    print("  - Non-uniform resource distribution for load balancing")
    print("  - Extended output: wave partitions, mean periods, peak parameters")
    print("  - High-frequency output for detailed temporal evolution")


if __name__ == "__main__":
    main()
