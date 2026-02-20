#!/usr/bin/env python3
"""
WW3 mww3_test_02 multi-grid regression test configuration using rompy-ww3.

Test: Multi-grid configuration with 3 model grids with varying resolution.
Purpose: Validate multi-grid nesting with 3-level grid hierarchy.
Reference: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/mww3_test_02
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


def create_ww3_mww3_test_02_component():
    """Create rompy-ww3 Multi component for mww3_test_02 multi-grid test."""

    # Domain configuration for multi-grid run with 3 grids
    domain = Domain(
        start="20200101 000000",
        stop="20200102 000000",
        iostyp=1,  # Unified point output
        nrinp=1,  # Number of input grids (minimum 1 required)
        nrgrd=3,  # Number of model grids (3-level nesting)
    )

    # Model grid 1 - Coarsest grid (outer domain)
    model_grid1 = ModelGrid(
        name="coarse",
        forcing=ModelGridForcing(
            water_levels="no",
            currents="no",
            winds="T",  # Wind forcing from files
            ice_conc="no",
        ),
        resource=ModelGridResource(
            rank_id=1,  # MPI rank assignment
            group_id=1,
            comm_frac_start=0.00,
            comm_frac_end=0.33,  # First third of resources
        ),
    )

    # Model grid 2 - Medium resolution grid (intermediate domain)
    model_grid2 = ModelGrid(
        name="medium",
        forcing=ModelGridForcing(
            water_levels="no",
            currents="no",
            winds="T",  # Wind forcing from files
            ice_conc="no",
        ),
        resource=ModelGridResource(
            rank_id=2,  # Different MPI rank
            group_id=1,
            comm_frac_start=0.33,
            comm_frac_end=0.67,  # Middle third of resources
        ),
    )

    # Model grid 3 - Finest grid (nested inner domain)
    model_grid3 = ModelGrid(
        name="fine",
        forcing=ModelGridForcing(
            water_levels="no",
            currents="no",
            winds="T",  # Wind forcing from files
            ice_conc="no",
        ),
        resource=ModelGridResource(
            rank_id=3,  # Third MPI rank
            group_id=1,
            comm_frac_start=0.67,
            comm_frac_end=1.00,  # Last third of resources
        ),
    )

    # Output configuration - more output fields than test_01
    output_type = OutputType(
        field=OutputTypeField(list="HS FP DP DIR SPR WND CUR"),
    )

    output_date = OutputDate(
        field=OutputDateField(
            start="20200101 000000",
            stride=1800,  # Every 30 minutes (more frequent than test_01)
            stop="20200102 000000",
        ),
    )

    # Create Multi component with all configurations
    multi_component = Multi(
        domain=domain,
        model_grids=[model_grid1, model_grid2, model_grid3],
        output_type=output_type,
        output_date=output_date,
    )

    return multi_component


def main():
    """Generate WW3 multi-grid configuration for mww3_test_02 regression test."""
    print("Creating WW3 multi-grid configuration for mww3_test_02 regression test...")
    print("Test: Multi-grid with 3 coupled grids (3-level nesting)")

    multi_component = create_ww3_mww3_test_02_component()

    # Create configuration with Multi component
    config = NMLConfig(multi_component=multi_component)

    period = TimeRange(start="2020-01-01T00:00:00", duration="1D", interval="30m")

    model_run = ModelRun(
        run_id="ww3_mww3_test_02_regression",
        config=config,
        period=period,
        output_dir="rompy_runs",
    )
    model_run.generate()

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nGenerated namelists for mww3_test_02 test:")
    print("  - ww3_multi.nml: Multi-grid configuration")
    print("  - Configuration includes:")
    print("    * 3 model grids (coarse, medium, fine)")
    print("    * 3-level grid hierarchy with nested domains")
    print("    * Per-grid resource allocation (3 MPI ranks)")
    print("    * More output fields than test_01")
    print("    * More frequent output (every 30 min vs hourly)")
    print("\nThis test validates 3-level multi-grid nesting in WW3.")


if __name__ == "__main__":
    main()
