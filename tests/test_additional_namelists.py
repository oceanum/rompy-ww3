"""
Test cases for additional WW3 namelist classes.
"""

import tempfile
from pathlib import Path
from rompy_ww3.namelists import (
    Spectrum,
    Run,
    Timesteps,
    Grid,
    Bound,
    Forcing,
    ForcingField,
    Track,
    Field,
    Point,
    Restart,
    Update,
    RestartUpdate,
)


def test_spectrum_nml():
    """Test SPECTRUM_NML namelist."""
    spectrum = Spectrum(xfr=1.1, freq1=0.04118, nk=32, nth=24, thoff=0.0)

    rendered = spectrum.render()
    print("SPECTRUM_NML rendered:")
    print(rendered[:200] + "..." if len(rendered) > 200 else rendered)

    assert "&SPECTRUM_NML" in rendered
    assert "SPECTRUM%XFR" in rendered
    assert "SPECTRUM%FREQ1" in rendered
    assert "SPECTRUM%NK" in rendered
    assert "SPECTRUM%NTH" in rendered
    assert "/" in rendered

    print("SPECTRUM_NML test passed!")


def test_run_nml():
    """Test RUN_NML namelist."""
    run = Run(
        fldry=False,
        flcx=True,
        flcy=True,
        flcth=True,
        flck=True,
        flsou=True,
    )

    rendered = run.render()
    assert "&RUN_NML" in rendered
    assert "RUN%FLDRY = F" in rendered
    assert "RUN%FLCX = T" in rendered
    assert "RUN%FLCY = T" in rendered
    assert "RUN%FLCTH = T" in rendered
    assert "RUN%FLCK = T" in rendered
    assert "RUN%FLSOU = T" in rendered
    assert "/" in rendered


def test_timesteps_nml():
    """Test TIMESTEPS_NML namelist."""
    timesteps = Timesteps(
        dtmax=2700.0,  # Maximum CFL timestep (3 * dtxy)
        dtxy=900.0,  # Propagation timestep
        dtkth=1350.0,  # Refraction timestep (between dtmax/10 and dtmax/2)
        dtmin=10.0,  # Minimum time step
    )

    rendered = timesteps.render()
    print("\nTIMESTEPS_NML rendered:")
    print(rendered)

    assert "&TIMESTEPS_NML" in rendered
    assert "TIMESTEPS%DTMAX" in rendered
    assert "TIMESTEPS%DTXY" in rendered
    assert "TIMESTEPS%DTKTH" in rendered
    assert "TIMESTEPS%DTMIN" in rendered
    assert "/" in rendered

    print("TIMESTEPS_NML test passed!")


def test_grid_nml():
    """Test GRID_NML namelist."""
    grid = Grid(name="Test Grid", type="RECT", coord="SPHE")

    rendered = grid.render()
    print("\nGRID_NML rendered:")
    print(rendered)

    assert "&GRID_NML" in rendered
    assert "GRID%NAME" in rendered
    assert "GRID%TYPE" in rendered
    assert "GRID%COORD" in rendered
    assert "/" in rendered

    print("GRID_NML test passed!")


def test_bound_nml():
    """Test BOUND_NML namelist."""
    bound = Bound(mode="WRITE", interp=2, verbose=1, file="spec.list")

    rendered = bound.render()
    print("\nBOUND_NML rendered:")
    print(rendered)

    assert "&BOUND_NML" in rendered
    assert "BOUND%MODE" in rendered
    assert "BOUND%INTERP" in rendered
    assert "BOUND%VERBOSE" in rendered
    assert "BOUND%FILE" in rendered
    assert "/" in rendered

    print("BOUND_NML test passed!")


def test_forcing_nml():
    """Test FORCING_NML namelist."""
    forcing = Forcing(
        timestart="20230101 000000",
        timestop="20230107 000000",
        field={"winds": True},  # Only one field can be True
        grid={"latlon": True},
    )

    rendered = forcing.render()
    print("\nFORCING_NML rendered:")
    print(rendered)

    assert "&FORCING_NML" in rendered
    assert "FORCING%TIMESTART" in rendered
    assert "FORCING%TIMESTOP" in rendered
    assert "FORCING%FIELD%WINDS" in rendered
    assert "FORCING%GRID%LATLON" in rendered
    assert "/" in rendered

    print("FORCING_NML test passed!")


def test_track_nml():
    """Test TRACK_NML namelist."""
    track = Track(timestart="20230101 000000", timestride="3600", timesplit=8)

    rendered = track.render()
    print("\nTRACK_NML rendered:")
    print(rendered)

    assert "&TRACK_NML" in rendered
    assert "TRACK%TIMESTART" in rendered
    assert "TRACK%TIMESTRIDE" in rendered
    assert "TRACK%TIMESPLIT" in rendered
    assert "/" in rendered

    print("TRACK_NML test passed!")


def test_field_nml():
    """Test FIELD_NML namelist."""
    field = Field(
        timestart="20230101 000000",
        timestride="3600",
        list="HS DIR SPR WND ICE CUR LEV",
        samefile=True,
    )

    rendered = field.render()
    print("\nFIELD_NML rendered:")
    print(rendered)

    assert "&FIELD_NML" in rendered
    assert "FIELD%TIMESTART" in rendered
    assert "FIELD%TIMESTRIDE" in rendered
    assert "FIELD%LIST" in rendered
    assert "FIELD%SAMEFILE" in rendered
    assert "/" in rendered

    print("FIELD_NML test passed!")


def test_point_nml():
    """Test POINT_NML namelist."""
    point = Point(
        timestart="20230101 000000", timestride="3600", list="all", buffer=150
    )

    rendered = point.render()
    print("\nPOINT_NML rendered:")
    print(rendered)

    assert "&POINT_NML" in rendered
    assert "POINT%TIMESTART" in rendered
    assert "POINT%TIMESTRIDE" in rendered
    assert "POINT%LIST" in rendered
    assert "POINT%BUFFER" in rendered
    assert "/" in rendered

    print("POINT_NML test passed!")


def test_restart_nml():
    """Test RESTART_NML namelist."""
    restart = Restart(restarttime="20230101 000000")

    rendered = restart.render()
    print("\nRESTART_NML rendered:")
    print(rendered)

    assert "&RESTART_NML" in rendered
    assert "RESTART%RESTARTTIME" in rendered
    assert "/" in rendered

    print("RESTART_NML test passed!")


def test_file_writing():
    """Test namelist file writing."""

    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Test writing each namelist to a file
        # Spectrum
        spectrum = Spectrum(xfr=1.1, freq1=0.035714, nk=25, nth=24, thoff=0.0)
        spectrum.write_nml(tmp_path)
        assert (tmp_path / "spectrum.nml").exists()

        # Run
        run = Run(fldry=False, flcx=True, flcy=True, flcth=True, flck=True, flsou=True)
        run.write_nml(tmp_path)
        assert (tmp_path / "run.nml").exists()

        # Bound
        bound = Bound(mode="READ", file="bound_spec.nc", interp=2)
        bound.write_nml(tmp_path)
        assert (tmp_path / "bound.nml").exists()

        # Forcing
        forcing_field = ForcingField(winds=True, currents=False, water_levels=False)
        forcing = Forcing(field=forcing_field)
        forcing.write_nml(tmp_path)
        assert (tmp_path / "forcing.nml").exists()

        # Track
        track = Track(timestart="20230101 000000", timestride="3600")
        track.write_nml(tmp_path)
        assert (tmp_path / "track.nml").exists()

        # Field
        field = Field(list="HSIGN TMM10 TM02 PDIR PENT WNDIR WNDSP")
        field.write_nml(tmp_path)
        assert (tmp_path / "field.nml").exists()

        # Point
        point = Point(buffer=10, list="all")
        point.write_nml(tmp_path)
        assert (tmp_path / "point.nml").exists()

        # Restart
        restart = Restart(restarttime="20230101 000000")
        restart.write_nml(tmp_path)
        assert (tmp_path / "restart.nml").exists()

        # Update
        update = Update(prcntg=1.0, prcntg_cap=1.1)
        update.write_nml(tmp_path)
        # RestartUpdate
        restart_update = RestartUpdate(update_time="20230101 000000")
        restart_update.write_nml(tmp_path)
        assert (tmp_path / "restartupdate.nml").exists()


def test_all_namelist_names():
    """Test that all namelist classes generate correct namelist names."""
    # Test a few key classes to make sure names are correct
    spectrum = Spectrum()
    assert spectrum.get_namelist_name() == "SPECTRUM_NML"

    run = Run()
    assert run.get_namelist_name() == "RUN_NML"

    forcing = Forcing()
    assert forcing.get_namelist_name() == "FORCING_NML"

    restart = Restart()
    assert restart.get_namelist_name() == "RESTART_NML"

    print("All namelist names test passed!")


if __name__ == "__main__":
    test_spectrum_nml()
    test_run_nml()
    test_timesteps_nml()
    test_grid_nml()
    test_bound_nml()
    test_forcing_nml()
    test_track_nml()
    test_field_nml()
    test_point_nml()
    test_restart_nml()
    test_file_writing()
    test_all_namelist_names()
    print("\nAll additional namelist tests passed!")
