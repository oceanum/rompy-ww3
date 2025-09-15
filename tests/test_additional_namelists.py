"""
Test cases for additional WW3 namelist classes.
"""

import tempfile
from pathlib import Path
from rompy_ww3.namelists import (
    Spectrum, Run, Timesteps, Grid, Rect, Bound, Forcing, Track, Field, Point, Restart
)


def test_spectrum_nml():
    """Test SPECTRUM_NML namelist."""
    spectrum = Spectrum(
        xfr=1.1,
        freq1=0.04118,
        nk=32,
        nth=24,
        thoff=0.0
    )
    
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
        flcx=True,
        flcy=True,
        flcth=True,
        flsou=True
    )
    
    rendered = run.render()
    print("\nRUN_NML rendered:")
    print(rendered)
    
    assert "&RUN_NML" in rendered
    assert "RUN%FLCX" in rendered
    assert "RUN%FLCY" in rendered
    assert "RUN%FLCTH" in rendered
    assert "RUN%FLSOU" in rendered
    assert "/" in rendered
    
    print("RUN_NML test passed!")


def test_timesteps_nml():
    """Test TIMESTEPS_NML namelist."""
    timesteps = Timesteps(
        dt=600.0,
        dtfld=3600.0,
        dtpnt=3600.0
    )
    
    rendered = timesteps.render()
    print("\nTIMESTEPS_NML rendered:")
    print(rendered)
    
    assert "&TIMESTEPS_NML" in rendered
    assert "TIMESTEPS%DT" in rendered
    assert "TIMESTEPS%DTFLD" in rendered
    assert "TIMESTEPS%DTPNT" in rendered
    assert "/" in rendered
    
    print("TIMESTEPS_NML test passed!")


def test_grid_nml():
    """Test GRID_NML namelist."""
    grid = Grid(
        name="Test Grid",
        type="RECT",
        coord="SPHE",
        nx=100,
        ny=50
    )
    
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
    bound = Bound(
        mode="WRITE",
        interp=2,
        verbose=1,
        file="spec.list"
    )
    
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
        field={
            "winds": True,
            "water_levels": True
        },
        grid={
            "latlon": True
        }
    )
    
    rendered = forcing.render()
    print("\nFORCING_NML rendered:")
    print(rendered)
    
    assert "&FORCING_NML" in rendered
    assert "FORCING%TIMESTART" in rendered
    assert "FORCING%TIMESTOP" in rendered
    assert "FORCING%FIELD%WINDS" in rendered
    assert "FORCING%FIELD%WATER_LEVELS" in rendered
    assert "FORCING%GRID%LATLON" in rendered
    assert "/" in rendered
    
    print("FORCING_NML test passed!")


def test_track_nml():
    """Test TRACK_NML namelist."""
    track = Track(
        timestart="20230101 000000",
        timestride="3600",
        timesplit=8
    )
    
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
        samefile=True
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
        timestart="20230101 000000",
        timestride="3600",
        list="all",
        buffer=150
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
    restart = Restart(
        restarttime="20230101 000000"
    )
    
    rendered = restart.render()
    print("\nRESTART_NML rendered:")
    print(rendered)
    
    assert "&RESTART_NML" in rendered
    assert "RESTART%RESTARTTIME" in rendered
    assert "/" in rendered
    
    print("RESTART_NML test passed!")


def test_file_writing():
    """Test writing namelists to files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workdir = Path(tmpdir)
        
        # Test writing a few namelists to files
        spectrum = Spectrum(xfr=1.1, freq1=0.04118, nk=32)
        run = Run(flcx=True, flcy=True)
        
        spectrum.write_nml(workdir)
        run.write_nml(workdir)
        
        # Check that files were created
        spectrum_file = workdir / "spectrum.nml"
        run_file = workdir / "run.nml"
        
        assert spectrum_file.exists()
        assert run_file.exists()
        
        # Check file contents
        spectrum_content = spectrum_file.read_text()
        run_content = run_file.read_text()
        
        assert "&SPECTRUM_NML" in spectrum_content
        assert "&RUN_NML" in run_content
        
        print(f"Created namelist files in {workdir}")


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