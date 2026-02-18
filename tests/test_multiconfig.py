"""
Unit tests for MultiConfig and GridSpec classes.

Tests cover:
- GridSpec creation and validation
- MultiConfig creation and validation
- Grid name matching validation
- Namelist generation
- Script generation
- YAML round-trip serialization
"""

import tempfile
from pathlib import Path
import pytest

from rompy_ww3.config import MultiConfig, GridSpec
from rompy_ww3.components import Multi, Grid as GridComponent
from rompy_ww3.namelists import (
    Domain,
    Timesteps,
    Spectrum,
    Run,
    Grid,
    Rect,
    Depth,
    ModelGrid,
)


class TestGridSpec:
    """Unit tests for GridSpec class."""

    def test_basic_creation(self):
        """Test GridSpec can be created with required fields only."""
        grid_component = GridComponent(
            spectrum=Spectrum(xfr=1.1, freq1=0.04177, nk=25, nth=24),
            run=Run(flcx=True, flcy=True, flcth=True, flsou=True),
            timesteps=Timesteps(dtmax=900.0, dtxy=300.0, dtkth=450.0, dtmin=30.0),
            grid=Grid(
                name="Test grid",
                type="RECT",
                coord="CART",
                clos="NONE",
                zlim=-0.1,
                dmin=0.25,
            ),
            rect=Rect(nx=50, ny=50, sx=10000, sy=10000, x0=0, y0=0),
            depth=Depth(sf=-1, filename="test.depth", idla=3),
        )

        grid_spec = GridSpec(name="test", grid=grid_component)

        assert grid_spec.name == "test"
        assert grid_spec.grid is not None
        assert grid_spec.prnc is None
        assert grid_spec.bounc is None

    def test_gridspec_with_optional_components(self):
        """Test GridSpec works with optional prnc and bounc components."""
        from rompy_ww3.components import Prnc, Bounc

        grid_component = GridComponent(
            spectrum=Spectrum(xfr=1.1, freq1=0.04177, nk=25, nth=24),
            run=Run(flcx=True, flcy=True, flcth=True, flsou=True),
            timesteps=Timesteps(dtmax=900.0, dtxy=300.0, dtkth=450.0, dtmin=30.0),
            grid=Grid(
                name="Test grid",
                type="RECT",
                coord="CART",
                clos="NONE",
                zlim=-0.1,
                dmin=0.25,
            ),
            rect=Rect(nx=50, ny=50, sx=10000, sy=10000, x0=0, y0=0),
            depth=Depth(sf=-1, filename="test.depth", idla=3),
        )

        prnc_component = Prnc()
        bounc_component = Bounc()

        grid_spec = GridSpec(
            name="test", grid=grid_component, prnc=prnc_component, bounc=bounc_component
        )

        assert grid_spec.name == "test"
        assert grid_spec.grid is not None
        assert grid_spec.prnc is not None
        assert grid_spec.bounc is not None

    def test_gridspec_validates_grid_component(self):
        """Test GridSpec requires valid Grid component."""
        with pytest.raises(Exception):  # Will raise validation error
            GridSpec(name="test", grid="invalid")


class TestMultiConfig:
    """Unit tests for MultiConfig class."""

    def test_basic_creation(self):
        """Test MultiConfig can be instantiated with multi and grids."""
        multi_component = Multi(
            domain=Domain(
                start="20200101 000000",
                stop="20200101 120000",
                iostyp=1,
                nrinp=0,
                nrgrd=1,
            ),
            model_grids=[
                ModelGrid(
                    name="test",
                    forcing={
                        "winds": "T",
                        "currents": "no",
                        "water_levels": "no",
                        "ice_conc": "no",
                    },
                    resource={
                        "rank_id": 1,
                        "group_id": 1,
                        "comm_frac_start": 0.0,
                        "comm_frac_end": 1.0,
                    },
                )
            ],
            output_type={"field": {"list": "HS FP DP DIR"}},
            output_date={
                "field": {
                    "start": "20200101 000000",
                    "stride": "3600",
                    "stop": "20200101 120000",
                }
            },
        )

        grid_component = GridComponent(
            spectrum=Spectrum(xfr=1.1, freq1=0.04177, nk=25, nth=24),
            run=Run(flcx=True, flcy=True, flcth=True, flsou=True),
            timesteps=Timesteps(dtmax=900.0, dtxy=300.0, dtkth=450.0, dtmin=30.0),
            grid=Grid(
                name="Test grid",
                type="RECT",
                coord="CART",
                clos="NONE",
                zlim=-0.1,
                dmin=0.25,
            ),
            rect=Rect(nx=50, ny=50, sx=10000, sy=10000, x0=0, y0=0),
            depth=Depth(sf=-1, filename="test.depth", idla=3),
        )

        grid_spec = GridSpec(name="test", grid=grid_component)

        config = MultiConfig(multi=multi_component, grids=[grid_spec])

        assert config.model_type == "multi"
        assert config.multi is not None
        assert len(config.grids) == 1
        assert config.grids[0].name == "test"

    def test_multiconfig_grid_name_validation_success(self):
        """Test validation passes when grid names match."""
        multi_component = Multi(
            domain=Domain(
                start="20200101 000000",
                stop="20200101 120000",
                iostyp=1,
                nrinp=0,
                nrgrd=2,
            ),
            model_grids=[
                ModelGrid(
                    name="coarse",
                    forcing={
                        "winds": "T",
                        "currents": "no",
                        "water_levels": "no",
                        "ice_conc": "no",
                    },
                    resource={
                        "rank_id": 1,
                        "group_id": 1,
                        "comm_frac_start": 0.0,
                        "comm_frac_end": 0.5,
                    },
                ),
                ModelGrid(
                    name="fine",
                    forcing={
                        "winds": "T",
                        "currents": "no",
                        "water_levels": "no",
                        "ice_conc": "no",
                    },
                    resource={
                        "rank_id": 2,
                        "group_id": 1,
                        "comm_frac_start": 0.5,
                        "comm_frac_end": 1.0,
                    },
                ),
            ],
        )

        grid_coarse = GridSpec(
            name="coarse",
            grid=GridComponent(
                spectrum=Spectrum(xfr=1.1, freq1=0.04177, nk=25, nth=24),
                run=Run(flcx=True, flcy=True, flcth=True, flsou=True),
                timesteps=Timesteps(dtmax=1200.0, dtxy=400.0, dtkth=600.0, dtmin=40.0),
                grid=Grid(
                    name="Coarse grid",
                    type="RECT",
                    coord="CART",
                    clos="NONE",
                    zlim=-0.1,
                    dmin=0.25,
                ),
                rect=Rect(nx=60, ny=60, sx=10000, sy=10000, x0=0, y0=0),
                depth=Depth(sf=-1, filename="coarse.depth", idla=3),
            ),
        )

        grid_fine = GridSpec(
            name="fine",
            grid=GridComponent(
                spectrum=Spectrum(xfr=1.1, freq1=0.04177, nk=25, nth=24),
                run=Run(flcx=True, flcy=True, flcth=True, flsou=True),
                timesteps=Timesteps(dtmax=600.0, dtxy=200.0, dtkth=300.0, dtmin=20.0),
                grid=Grid(
                    name="Fine grid",
                    type="RECT",
                    coord="CART",
                    clos="NONE",
                    zlim=-0.1,
                    dmin=0.25,
                ),
                rect=Rect(nx=30, ny=30, sx=10000, sy=10000, x0=0, y0=0),
                depth=Depth(sf=-1, filename="fine.depth", idla=3),
            ),
        )

        # Should not raise
        config = MultiConfig(multi=multi_component, grids=[grid_coarse, grid_fine])
        assert len(config.grids) == 2

    def test_multiconfig_grid_name_validation_failure_missing_in_multi(self):
        """Test validation catches grids in GridSpec but not in Multi."""
        multi_component = Multi(
            domain=Domain(
                start="20200101 000000",
                stop="20200101 120000",
                iostyp=1,
                nrinp=0,
                nrgrd=1,
            ),
            model_grids=[
                ModelGrid(
                    name="coarse",
                    forcing={
                        "winds": "T",
                        "currents": "no",
                        "water_levels": "no",
                        "ice_conc": "no",
                    },
                    resource={
                        "rank_id": 1,
                        "group_id": 1,
                        "comm_frac_start": 0.0,
                        "comm_frac_end": 1.0,
                    },
                )
            ],
        )

        grid_coarse = GridSpec(
            name="coarse",
            grid=GridComponent(
                spectrum=Spectrum(xfr=1.1, freq1=0.04177, nk=25, nth=24),
                run=Run(flcx=True, flcy=True, flcth=True, flsou=True),
                timesteps=Timesteps(dtmax=1200.0, dtxy=400.0, dtkth=600.0, dtmin=40.0),
                grid=Grid(
                    name="Coarse grid",
                    type="RECT",
                    coord="CART",
                    clos="NONE",
                    zlim=-0.1,
                    dmin=0.25,
                ),
                rect=Rect(nx=60, ny=60, sx=10000, sy=10000, x0=0, y0=0),
                depth=Depth(sf=-1, filename="coarse.depth", idla=3),
            ),
        )

        grid_extra = GridSpec(
            name="extra",
            grid=GridComponent(
                spectrum=Spectrum(xfr=1.1, freq1=0.04177, nk=25, nth=24),
                run=Run(flcx=True, flcy=True, flcth=True, flsou=True),
                timesteps=Timesteps(dtmax=600.0, dtxy=200.0, dtkth=300.0, dtmin=20.0),
                grid=Grid(
                    name="Extra grid",
                    type="RECT",
                    coord="CART",
                    clos="NONE",
                    zlim=-0.1,
                    dmin=0.25,
                ),
                rect=Rect(nx=30, ny=30, sx=10000, sy=10000, x0=0, y0=0),
                depth=Depth(sf=-1, filename="extra.depth", idla=3),
            ),
        )

        with pytest.raises(ValueError, match="Grid name mismatch.*extra"):
            MultiConfig(multi=multi_component, grids=[grid_coarse, grid_extra])

    def test_multiconfig_grid_name_validation_failure_missing_in_grids(self):
        """Test validation catches grids in Multi but not in GridSpec."""
        multi_component = Multi(
            domain=Domain(
                start="20200101 000000",
                stop="20200101 120000",
                iostyp=1,
                nrinp=0,
                nrgrd=2,
            ),
            model_grids=[
                ModelGrid(
                    name="coarse",
                    forcing={
                        "winds": "T",
                        "currents": "no",
                        "water_levels": "no",
                        "ice_conc": "no",
                    },
                    resource={
                        "rank_id": 1,
                        "group_id": 1,
                        "comm_frac_start": 0.0,
                        "comm_frac_end": 0.5,
                    },
                ),
                ModelGrid(
                    name="fine",
                    forcing={
                        "winds": "T",
                        "currents": "no",
                        "water_levels": "no",
                        "ice_conc": "no",
                    },
                    resource={
                        "rank_id": 2,
                        "group_id": 1,
                        "comm_frac_start": 0.5,
                        "comm_frac_end": 1.0,
                    },
                ),
            ],
        )

        grid_coarse = GridSpec(
            name="coarse",
            grid=GridComponent(
                spectrum=Spectrum(xfr=1.1, freq1=0.04177, nk=25, nth=24),
                run=Run(flcx=True, flcy=True, flcth=True, flsou=True),
                timesteps=Timesteps(dtmax=1200.0, dtxy=400.0, dtkth=600.0, dtmin=40.0),
                grid=Grid(
                    name="Coarse grid",
                    type="RECT",
                    coord="CART",
                    clos="NONE",
                    zlim=-0.1,
                    dmin=0.25,
                ),
                rect=Rect(nx=60, ny=60, sx=10000, sy=10000, x0=0, y0=0),
                depth=Depth(sf=-1, filename="coarse.depth", idla=3),
            ),
        )

        # Missing 'fine' GridSpec
        with pytest.raises(ValueError, match="Grid name mismatch.*fine"):
            MultiConfig(multi=multi_component, grids=[grid_coarse])

    def test_multiconfig_grid_count_validation_failure(self):
        """Test validation catches grid count mismatch."""
        multi_component = Multi(
            domain=Domain(
                start="20200101 000000",
                stop="20200101 120000",
                iostyp=1,
                nrinp=0,
                nrgrd=2,  # Declares 2 grids
            ),
            model_grids=[
                ModelGrid(
                    name="test",
                    forcing={
                        "winds": "T",
                        "currents": "no",
                        "water_levels": "no",
                        "ice_conc": "no",
                    },
                    resource={
                        "rank_id": 1,
                        "group_id": 1,
                        "comm_frac_start": 0.0,
                        "comm_frac_end": 1.0,
                    },
                )
            ],
        )

        grid_spec = GridSpec(
            name="test",
            grid=GridComponent(
                spectrum=Spectrum(xfr=1.1, freq1=0.04177, nk=25, nth=24),
                run=Run(flcx=True, flcy=True, flcth=True, flsou=True),
                timesteps=Timesteps(dtmax=900.0, dtxy=300.0, dtkth=450.0, dtmin=30.0),
                grid=Grid(
                    name="Test grid",
                    type="RECT",
                    coord="CART",
                    clos="NONE",
                    zlim=-0.1,
                    dmin=0.25,
                ),
                rect=Rect(nx=50, ny=50, sx=10000, sy=10000, x0=0, y0=0),
                depth=Depth(sf=-1, filename="test.depth", idla=3),
            ),
        )

        # Only 1 GridSpec but nrgrd=2
        with pytest.raises(ValueError, match="Grid count mismatch.*nrgrd=2.*1"):
            MultiConfig(multi=multi_component, grids=[grid_spec])

    def test_multiconfig_write_control_files(self):
        """Test namelist generation produces correct files."""
        multi_component = Multi(
            domain=Domain(
                start="20200101 000000",
                stop="20200101 120000",
                iostyp=1,
                nrinp=0,
                nrgrd=1,
            ),
            model_grids=[
                ModelGrid(
                    name="test",
                    forcing={
                        "winds": "T",
                        "currents": "no",
                        "water_levels": "no",
                        "ice_conc": "no",
                    },
                    resource={
                        "rank_id": 1,
                        "group_id": 1,
                        "comm_frac_start": 0.0,
                        "comm_frac_end": 1.0,
                    },
                )
            ],
            output_type={"field": {"list": "HS FP DP DIR"}},
            output_date={
                "field": {
                    "start": "20200101 000000",
                    "stride": "3600",
                    "stop": "20200101 120000",
                }
            },
        )

        grid_spec = GridSpec(
            name="test",
            grid=GridComponent(
                spectrum=Spectrum(xfr=1.1, freq1=0.04177, nk=25, nth=24),
                run=Run(flcx=True, flcy=True, flcth=True, flsou=True),
                timesteps=Timesteps(dtmax=900.0, dtxy=300.0, dtkth=450.0, dtmin=30.0),
                grid=Grid(
                    name="Test grid",
                    type="RECT",
                    coord="CART",
                    clos="NONE",
                    zlim=-0.1,
                    dmin=0.25,
                ),
                rect=Rect(nx=50, ny=50, sx=10000, sy=10000, x0=0, y0=0),
                depth=Depth(sf=-1, filename="test.depth", idla=3),
            ),
        )

        config = MultiConfig(multi=multi_component, grids=[grid_spec])

        with tempfile.TemporaryDirectory() as tmpdir:
            runtime_mock = type(
                "Runtime", (), {"staging_dir": Path(tmpdir), "period": None}
            )()

            config.write_control_files(runtime_mock)

            # Check expected files exist
            multi_file = Path(tmpdir) / "ww3_multi.nml"
            grid_file = Path(tmpdir) / "ww3_grid_test.nml"

            assert multi_file.exists(), "ww3_multi.nml was not created"
            assert grid_file.exists(), "ww3_grid_test.nml was not created"

            # Verify content
            with open(multi_file, "r") as f:
                multi_content = f.read()
                assert "&DOMAIN_NML" in multi_content
                assert "&MODEL_GRID_NML" in multi_content

            with open(grid_file, "r") as f:
                grid_content = f.read()
                assert "&SPECTRUM_NML" in grid_content
                assert "&TIMESTEPS_NML" in grid_content
                assert "&GRID_NML" in grid_content

    def test_multiconfig_generate_scripts(self):
        """Test script generation produces executable scripts."""
        multi_component = Multi(
            domain=Domain(
                start="20200101 000000",
                stop="20200101 120000",
                iostyp=1,
                nrinp=0,
                nrgrd=1,
            ),
            model_grids=[
                ModelGrid(
                    name="test",
                    forcing={
                        "winds": "T",
                        "currents": "no",
                        "water_levels": "no",
                        "ice_conc": "no",
                    },
                    resource={
                        "rank_id": 1,
                        "group_id": 1,
                        "comm_frac_start": 0.0,
                        "comm_frac_end": 1.0,
                    },
                )
            ],
        )

        grid_spec = GridSpec(
            name="test",
            grid=GridComponent(
                spectrum=Spectrum(xfr=1.1, freq1=0.04177, nk=25, nth=24),
                run=Run(flcx=True, flcy=True, flcth=True, flsou=True),
                timesteps=Timesteps(dtmax=900.0, dtxy=300.0, dtkth=450.0, dtmin=30.0),
                grid=Grid(
                    name="Test grid",
                    type="RECT",
                    coord="CART",
                    clos="NONE",
                    zlim=-0.1,
                    dmin=0.25,
                ),
                rect=Rect(nx=50, ny=50, sx=10000, sy=10000, x0=0, y0=0),
                depth=Depth(sf=-1, filename="test.depth", idla=3),
            ),
        )

        config = MultiConfig(multi=multi_component, grids=[grid_spec])

        with tempfile.TemporaryDirectory() as tmpdir:
            runtime_mock = type(
                "Runtime", (), {"staging_dir": Path(tmpdir), "period": None}
            )()

            run_script = config.generate_run_script(runtime_mock)

            # Check that all scripts exist
            preprocess_script = Path(tmpdir) / "preprocess_ww3.sh"
            run_script = Path(tmpdir) / "run_ww3.sh"
            postprocess_script = Path(tmpdir) / "postprocess_ww3.sh"
            full_script = Path(tmpdir) / "full_ww3.sh"

            assert preprocess_script.exists(), "preprocess_ww3.sh not created"
            assert run_script.exists(), "run_ww3.sh not created"
            assert postprocess_script.exists(), "postprocess_ww3.sh not created"
            assert full_script.exists(), "full_ww3.sh not created"

            # Check scripts are executable
            assert preprocess_script.stat().st_mode & 0o111, (
                "preprocess script not executable"
            )
            assert run_script.stat().st_mode & 0o111, "run script not executable"
            assert postprocess_script.stat().st_mode & 0o111, (
                "postprocess script not executable"
            )
            assert full_script.stat().st_mode & 0o111, "full script not executable"

            # Check basic content
            with open(preprocess_script, "r") as f:
                content = f.read()
                assert "#!/bin/bash" in content
                assert "ww3_grid" in content

            with open(run_script, "r") as f:
                content = f.read()
                assert "#!/bin/bash" in content
                assert "ww3_multi" in content

    def test_multiconfig_yaml_roundtrip(self):
        """Test MultiConfig can be saved/loaded from YAML."""
        # Create a simple config
        config_dict = {
            "model_type": "multi",
            "multi": {
                "domain": {
                    "start": "20200101 000000",
                    "stop": "20200101 120000",
                    "iostyp": 1,
                    "nrinp": 0,
                    "nrgrd": 1,
                },
                "model_grids": [
                    {
                        "name": "test",
                        "forcing": {
                            "winds": "T",
                            "currents": "no",
                            "water_levels": "no",
                            "ice_conc": "no",
                        },
                        "resource": {
                            "rank_id": 1,
                            "group_id": 1,
                            "comm_frac_start": 0.0,
                            "comm_frac_end": 1.0,
                        },
                    }
                ],
            },
            "grids": [
                {
                    "name": "test",
                    "grid": {
                        "spectrum": {"xfr": 1.1, "freq1": 0.04177, "nk": 25, "nth": 24},
                        "run": {
                            "flcx": True,
                            "flcy": True,
                            "flcth": True,
                            "flsou": True,
                        },
                        "timesteps": {
                            "dtmax": 900.0,
                            "dtxy": 300.0,
                            "dtkth": 450.0,
                            "dtmin": 30.0,
                        },
                        "grid": {
                            "name": "Test grid",
                            "type": "RECT",
                            "coord": "CART",
                            "clos": "NONE",
                            "zlim": -0.1,
                            "dmin": 0.25,
                        },
                        "rect": {
                            "nx": 50,
                            "ny": 50,
                            "sx": 10000,
                            "sy": 10000,
                            "x0": 0,
                            "y0": 0,
                        },
                        "depth": {"sf": -1, "filename": "test.depth", "idla": 3},
                    },
                }
            ],
        }

        # Create config from dict
        config = MultiConfig(**config_dict)

        # Verify it loads correctly
        assert config.model_type == "multi"
        assert len(config.grids) == 1
        assert config.grids[0].name == "test"

        # Test serialization to dict and back
        config_serialized = config.model_dump()
        config_reloaded = MultiConfig(**config_serialized)

        assert config_reloaded.model_type == config.model_type
        assert len(config_reloaded.grids) == len(config.grids)
        assert config_reloaded.grids[0].name == config.grids[0].name


class TestMultiConfigIntegration:
    """Integration tests with realistic multi-grid configurations."""

    def test_two_grid_configuration(self):
        """Test realistic 2-grid nested configuration."""
        config_dict = {
            "model_type": "multi",
            "multi": {
                "domain": {
                    "start": "20200101 000000",
                    "stop": "20200101 120000",
                    "iostyp": 1,
                    "nrinp": 0,
                    "nrgrd": 2,
                },
                "model_grids": [
                    {
                        "name": "coarse",
                        "forcing": {
                            "winds": "T",
                            "currents": "no",
                            "water_levels": "no",
                            "ice_conc": "no",
                        },
                        "resource": {
                            "rank_id": 1,
                            "group_id": 1,
                            "comm_frac_start": 0.0,
                            "comm_frac_end": 0.5,
                        },
                    },
                    {
                        "name": "fine",
                        "forcing": {
                            "winds": "T",
                            "currents": "no",
                            "water_levels": "no",
                            "ice_conc": "no",
                        },
                        "resource": {
                            "rank_id": 2,
                            "group_id": 1,
                            "comm_frac_start": 0.5,
                            "comm_frac_end": 1.0,
                        },
                    },
                ],
                "output_type": {"field": {"list": "HS FP DP DIR"}},
                "output_date": {
                    "field": {
                        "start": "20200101 000000",
                        "stride": "3600",
                        "stop": "20200101 120000",
                    }
                },
            },
            "grids": [
                {
                    "name": "coarse",
                    "grid": {
                        "spectrum": {"xfr": 1.1, "freq1": 0.04177, "nk": 25, "nth": 24},
                        "run": {
                            "flcx": True,
                            "flcy": True,
                            "flcth": True,
                            "flsou": True,
                        },
                        "timesteps": {
                            "dtmax": 1200.0,
                            "dtxy": 400.0,
                            "dtkth": 600.0,
                            "dtmin": 40.0,
                        },
                        "grid": {
                            "name": "Coarse grid",
                            "type": "RECT",
                            "coord": "CART",
                            "clos": "NONE",
                            "zlim": -0.1,
                            "dmin": 0.25,
                        },
                        "rect": {
                            "nx": 60,
                            "ny": 60,
                            "sx": 10000,
                            "sy": 10000,
                            "x0": 0,
                            "y0": 0,
                        },
                        "depth": {"sf": -1, "filename": "coarse.depth", "idla": 3},
                    },
                },
                {
                    "name": "fine",
                    "grid": {
                        "spectrum": {"xfr": 1.1, "freq1": 0.04177, "nk": 25, "nth": 24},
                        "run": {
                            "flcx": True,
                            "flcy": True,
                            "flcth": True,
                            "flsou": True,
                        },
                        "timesteps": {
                            "dtmax": 600.0,
                            "dtxy": 200.0,
                            "dtkth": 300.0,
                            "dtmin": 20.0,
                        },
                        "grid": {
                            "name": "Fine grid",
                            "type": "RECT",
                            "coord": "CART",
                            "clos": "NONE",
                            "zlim": -0.1,
                            "dmin": 0.25,
                        },
                        "rect": {
                            "nx": 30,
                            "ny": 30,
                            "sx": 10000,
                            "sy": 10000,
                            "x0": 0,
                            "y0": 0,
                        },
                        "depth": {"sf": -1, "filename": "fine.depth", "idla": 3},
                    },
                },
            ],
        }

        config = MultiConfig(**config_dict)

        with tempfile.TemporaryDirectory() as tmpdir:
            runtime_mock = type(
                "Runtime", (), {"staging_dir": Path(tmpdir), "period": None}
            )()

            # Write control files
            config.write_control_files(runtime_mock)

            # Generate scripts
            config.generate_run_script(runtime_mock)

            # Verify all expected files exist
            assert (Path(tmpdir) / "ww3_multi.nml").exists()
            assert (Path(tmpdir) / "ww3_grid_coarse.nml").exists()
            assert (Path(tmpdir) / "ww3_grid_fine.nml").exists()
            assert (Path(tmpdir) / "preprocess_ww3.sh").exists()
            assert (Path(tmpdir) / "run_ww3.sh").exists()
            assert (Path(tmpdir) / "postprocess_ww3.sh").exists()
            assert (Path(tmpdir) / "full_ww3.sh").exists()
