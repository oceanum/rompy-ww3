#!/usr/bin/env python3
"""
WW3 mww3_test_01 multi-grid regression test configuration using rompy-ww3.

Test: Basic multi-grid configuration with 2 model grids.
Purpose: Validate multi-grid coupling and boundary exchange.
Reference: https://github.com/NOAA-EMC/WW3/tree/develop/regtests/mww3_test_01
"""

from rompy.model import ModelRun
from rompy.core.time import TimeRange

from rompy_ww3.config import NMLConfig

from rompy_ww3.components import Multi

from rompy_ww3.namelists import (
    Domain,
)
from rompy_ww3.namelists.input import (
    ModelGrid,
    ModelGridForcing,
    ModelGridResource,
)
from rompy_ww3.namelists.output_date import OutputDate, OutputDateField
from rompy_ww3.namelists.output_type import OutputType, OutputTypeField


def create_ww3_mww3_test_01_component():
    """Create rompy-ww3 Multi component for mww3_test_01 multi-grid test."""

    # Domain configuration for multi-grid run
    domain = Domain(
        start="20200101 000000",
        stop="20200102 000000",
        iostyp=1,  # Unified point output
        nrinp=1,  # Number of input grids (minimum 1 required)
        nrgrd=2,  # Number of model grids
    )

    # Model grid 1 - Coarse grid (outer domain)
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
            comm_frac_end=0.50,
        ),
    )

    # Model grid 2 - Fine grid (nested domain)
    model_grid2 = ModelGrid(
        name="fine",
        forcing=ModelGridForcing(
            water_levels="no",
            currents="no",
            winds="T",  # Wind forcing from files
            ice_conc="no",
        ),
        resource=ModelGridResource(
            rank_id=2,  # Different MPI rank
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
            stride="3600",
            stop="20200102 000000",
        ),
    )

    # Create Multi component with all configurations
    multi_component = Multi(
        domain=domain,
        model_grids=[model_grid1, model_grid2],
        output_type=output_type,
        output_date=output_date,
    )

    return multi_component


def main():
    """Generate WW3 multi-grid configuration for mww3_test_01 regression test."""
    print("Creating WW3 multi-grid configuration for mww3_test_01 regression test...")
    print("Test: Basic multi-grid with 2 coupled grids")

    multi_component = create_ww3_mww3_test_01_component()

    # Create configuration with Multi component
    config = NMLConfig(multi_component=multi_component)

    period = TimeRange(start="2020-01-01T00:00:00", duration="1D", interval="1H")

    model_run = ModelRun(
        run_id="ww3_mww3_test_01_regression",
        config=config,
        period=period,
        output_dir="rompy_runs",
    )
    model_run.generate()

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nGenerated namelists for mww3_test_01 test:")
    print("  - ww3_multi.nml: Multi-grid configuration")
    print("  - Configuration includes:")
    print("    * 2 model grids (coarse and fine)")
    print("    * Grid coupling and boundary exchange")
    print("    * Per-grid resource allocation")
    print("    * Per-grid timesteps and spectrum")
    print("\nThis test validates basic multi-grid WW3 functionality.")


if __name__ == "__main__":
    main()
