#!/usr/bin/env python3
"""
WW3 tp2.12 regression test: Global 30-minute grid with simple closure.

This test validates a realistic operational global grid configuration with
30-minute (0.5°) resolution and simple periodic closure in longitude.

Key configuration:
- Grid type: RECT (rectilinear)
- Coordinates: SPHE (spherical)
- Closure: SMPL (simple - periodic in longitude)
- Grid: 720×311 points (0.5° resolution, -77.5° to 77.5°)
- Physics: ST4 package (SIN4 with custom parameters)
- Test Purpose: Validates global grid handling with realistic bathymetry

Run with:
    python rompy_ww3_tp2_12.py
"""

import sys
from rompy.model import ModelRun
from rompy.core.time import TimeRange
from rompy_ww3.core.data import WW3DataBlob

from rompy_ww3.config import NMLConfig

from rompy_ww3.components import Grid, Namelists
from rompy_ww3.components.namelists import MISC

from rompy_ww3.namelists import (
    Spectrum,
    Run,
    Timesteps,
)
from rompy_ww3.namelists.grid import Grid as GRID_NML, Rect
from rompy_ww3.namelists.depth import Depth
from rompy_ww3.namelists.mask import Mask
from rompy_ww3.namelists.obstacle import Obstacle


def create_ww3_tp2_12_config():
    """Create rompy-ww3 configuration for ww3_tp2.12 regression test.

    Demonstrates global 30-minute resolution grid with simple periodic closure.
    """

    grid_component = Grid(
        spectrum=Spectrum(
            xfr=1.07,
            freq1=0.035,
            nk=50,
            nth=36,
            thoff=0.5,
        ),
        run=Run(
            flcx=True,
            flcy=True,
            flcth=True,
            flck=False,
            flsou=False,
        ),
        timesteps=Timesteps(
            dtmax=3600.0,
            dtxy=1200.0,
            dtkth=1800.0,
            dtmin=30.0,
        ),
        grid=GRID_NML(
            name="Global 30 min GFS wind grid",
            nml="../input/namelists_Global.nml",
            type="RECT",
            coord="SPHE",
            clos="SMPL",  # Simple closure: periodic in longitude (NX+1,J) => (1,J)
            zlim=-0.1,
            dmin=2.50,
        ),
        rect=Rect(
            nx=720,  # 0.5° resolution: 360°/0.5° = 720 points
            ny=311,  # -77.5° to 77.5°: 155°/0.5° = 310 intervals + 1 = 311 points
            sx=0.50,
            sy=0.50,
            x0=0.0,
            y0=-77.5,
        ),
        depth=Depth(
            filename=WW3DataBlob(source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.12/input/glo_30m.bot"),
            sf=0.001,
        ),
        mask=Mask(
            filename=WW3DataBlob(source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.12/input/glo_30m.mask"),
        ),
        obstacle=Obstacle(
            filename=WW3DataBlob(source="https://raw.githubusercontent.com/NOAA-EMC/WW3/refs/tags/6.07.1/regtests/ww3_tp2.12/input/glo_30m.obst"),
            sf=0.01,
        ),
    )

    parameters_component = Namelists(
        misc=MISC(
            cice0=0.25,
            cicen=0.75,
            flagtr=4,
        ),
    )

    config = NMLConfig(
        ww3_grid=grid_component,
        namelists=parameters_component,
    )

    return config


if __name__ == "__main__":
    print("Creating WW3 tp2.12 configuration (Global 30-min Grid + SMPL Closure)...")
    config = create_ww3_tp2_12_config()

    period = TimeRange(
        start="20000101T000000",
        end="20000102T000000",
    )

    model = ModelRun(
        run_id="ww3_tp2_12",
        output_dir="rompy_runs",
        period=period,
        config=config,
    )

    print("\nGenerating namelist files...")
    result = model()

    if result:
        print("\n" + "=" * 70)
        print("✓ CONFIGURATION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print(f"\nConfiguration files generated in: {model.output_dir}")

        import os

        output_path = os.path.join(model.output_dir, model.run_id)
        if os.path.exists(output_path):
            files = [f for f in os.listdir(output_path) if f.endswith(".nml")]
            print(f"Files created: {len(files)}")
            for f in sorted(files):
                print(f"  - {f}")

        print("\n" + "=" * 70)
        print("GRID CHARACTERISTICS:")
        print("=" * 70)
        print("  Total Points:      223,920 (720×311)")
        print("  Resolution:        0.5° (~55 km at equator)")
        print("  Longitude:         0° to 360° (wraps with SMPL closure)")
        print("  Latitude:          -77.5° to 77.5°")
        print("  Closure Type:      SMPL (simple - periodic in longitude)")
        print("  Spectral:          50 frequencies × 36 directions")
    else:
        print("\n✗ Configuration generation failed")
        sys.exit(1)
