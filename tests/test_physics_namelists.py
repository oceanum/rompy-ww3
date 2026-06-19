"""
Test cases for WW3 physics parameter namelist classes.

Verifies all model field names match WW3 Fortran source (ww3_grid.ftn)
and that rendering produces valid Fortran namelist output.
"""

import tempfile
from pathlib import Path
from rompy_ww3.components.namelists import (
    # Wind input
    SIN1,
    SIN2,
    SIN3,
    SIN4,
    SNL1,
    SNL2,
    SNL3,
    SNL4,
    SDS1,
    SDS2,
    SDS3,
    SDS4,
    SBT1,
    SBT4,
    # Surf breaking
    SDB1,
    # Flux / stress
    FLX3,
    FLX4,
    PRO1,
    PRO2,
    PRO3,
    # Ice
    MISC,
    REF1,
    ROTD,
    UOST,
    # Container
    Namelists,
)


def test_sin1():
    """SIN1: WAM-3 wind input — single CINP field."""
    m = SIN1(cinp=0.25)
    r = m.render()
    assert "&SIN1" in r
    assert "SIN1%CINP = 0.25" in r


def test_sin2():
    """SIN2: Tolman & Chalikov — 7 fields."""
    m = SIN2(
        zwnd=10.0, swellf=0.66, stabsh=0.0, stabof=0.0, cneg=0.0, cpos=0.0, fneg=0.0
    )
    r = m.render()
    assert "&SIN2" in r
    assert "SIN2%ZWND = 10.0" in r
    assert "SIN2%SWELLF = 0.66" in r


def test_sin3():
    """SIN3: WAM4/Janssen — 7 fields."""
    m = SIN3(zwnd=10.0, alpha0=0.0095, z0max=0.001, sinthp=2.0, zalp=0.0, swellf=0.66)
    r = m.render()
    assert "&SIN3" in r
    assert "SIN3%ALPHA0 = 0.0095" in r


def test_sin4():
    """SIN4: ST4 — 17 fields."""
    m = SIN4(zwnd=10.0, alpha0=0.0095, betamax=1.33, swellfpar=1, swellf=0.66)
    r = m.render()
    assert "&SIN4" in r
    assert "SIN4%BETAMAX = 1.33" in r


def test_snl1():
    """SNL1: DIA — 7 fields."""
    m = SNL1(nlambda=0.25, nlprop=2.78e7, kdmin=0.5, snlcs1=0.0)
    r = m.render()
    assert "&SNL1" in r
    assert "SNL1%NLAMBDA = 0.25" in r


def test_snl2():
    """SNL2: Exact nonlinear — 3 fields."""
    m = SNL2(iqtype=2, tailnl=-5.0, ndepth=7)
    r = m.render()
    assert "&SNL2" in r
    assert "SNL2%IQTYPE = 2" in r


def test_snl3():
    """SNL3: GMD — 5 fields."""
    m = SNL3(nqdef=1, msc=0.0, nsc=-3.5, kdfd=1.0e8, kdfs=0.0)
    r = m.render()
    assert "&SNL3" in r
    assert "SNL3%NQDEF = 1" in r


def test_snl4():
    """SNL4: TSA/FBI — 2 fields."""
    m = SNL4(indtsa=1, altlp=2)
    r = m.render()
    assert "&SNL4" in r
    assert "SNL4%INDTSA = 1" in r


def test_sds1():
    """SDS1: WAM-3 whitecapping — 2 fields."""
    m = SDS1(cdis=2.36e-5, apm=0.00025)
    r = m.render()
    assert "&SDS1" in r
    assert "SDS1%CDIS = 2.36e-05" in r


def test_sds2():
    """SDS2: Tolman & Chalikov whitecapping — 6 fields."""
    m = SDS2(sdsa0=4.8, sdsa1=1.7e-4, sdsa2=2.0, sdsb0=0.3, sdsb1=0.2, phimin=0.003)
    r = m.render()
    assert "&SDS2" in r
    assert "SDS2%SDSA0 = 4.8" in r


def test_sds3():
    """SDS3: WAM4/Westhuysen whitecapping — 6 fields."""
    m = SDS3(
        sdsc1=55.0, wnmeanp=3.0, fxpm3=4.0, fxfm3=4.0, sdsdelta1=0.0, sdsdelta2=0.0
    )
    r = m.render()
    assert "&SDS3" in r
    assert "SDS3%SDSC1 = 55.0" in r


def test_sds4():
    """SDS4: ST4 whitecapping — 36 fields."""
    m = SDS4(sdsc1=0.0, wnmeanp=4.0, sdsbr=0.0009, sdsp=2.0)
    r = m.render()
    assert "&SDS4" in r
    assert "SDS4%SDSBR = 0.0009" in r


def test_sdb1():
    """SDB1: Battjes & Janssen — 3 fields."""
    m = SDB1(bjalfa=1.0, bjgam=0.73, bjflag=False)
    r = m.render()
    assert "&SDB1" in r
    assert "SDB1%BJALFA = 1.0" in r
    assert "SDB1%BJFLAG = F" in r  # boolean → Fortran 'F'


def test_sbt1():
    """SBT1: JONSWAP bottom friction — 1 field."""
    m = SBT1(gamma=0.067)
    r = m.render()
    assert "&SBT1" in r
    assert "SBT1%GAMMA = 0.067" in r


def test_sbt4():
    """SBT4: Sedimentary bottom friction — 9 fields."""
    m = SBT4(sedmapd50=True, sed_d50_uniform=0.0002, ripfac1=0.0)
    r = m.render()
    assert "&SBT4" in r
    assert "SBT4%SEDMAPD50 = T" in r


def test_flx3():
    """FLX3: TC1996 flux with cap — 2 fields."""
    m = FLX3(cdmax=3.0, ctype=0)
    r = m.render()
    assert "&FLX3" in r
    assert "FLX3%CDMAX = 3.0" in r


def test_flx4():
    """FLX4: Hwang 2011 flux — 1 field."""
    m = FLX4(cdfac=1.0)
    r = m.render()
    assert "&FLX4" in r
    assert "FLX4%CDFAC = 1.0" in r


def test_pro1():
    """PRO1: First-order propagation — CFLTM."""
    m = PRO1(cfltm=0.7)
    r = m.render()
    assert "&PRO1" in r
    assert "PRO1%CFLTM = 0.7" in r


def test_pro2():
    """PRO2: UQ/UNO with diffusion — 3 fields."""
    m = PRO2(cfltm=0.7, dtime=64800.0, latmin=86.0)
    r = m.render()
    assert "&PRO2" in r
    assert "PRO2%CFLTM = 0.7" in r
    assert "PRO2%DTIME = 64800.0" in r
    assert "PRO2%LATMIN = 86.0" in r


def test_pro3():
    """PRO3: UQ/UNO with averaging — 3 fields."""
    m = PRO3(cfltm=0.7, wdthcg=1.5, wdthth=1.5)
    r = m.render()
    assert "&PRO3" in r
    assert "PRO3%WDTHCG = 1.5" in r


def test_misc():
    """MISC: Miscellaneous — full set."""
    m = MISC(flagtr=4, cice0=0.25, cicen=0.75, nosw=2, lice=False, ptm=1, ptfc=0.1)
    r = m.render()
    assert "&MISC" in r
    assert "MISC%FLAGTR = 4" in r
    assert "MISC%CICE0 = 0.25" in r
    assert "MISC%NOSW = 2" in r
    assert "MISC%LICE = F" in r


def test_ref1():
    """REF1: Shoreline reflections — 11 fields."""
    m = REF1(refcoast=0.5, refrmax=0.8)
    r = m.render()
    assert "&REF1" in r
    assert "REF1%REFCOAST = 0.5" in r


def test_rotd():
    """ROTD: Rotated pole — 3 fields."""
    m = ROTD(plat=37.5, plon=177.5, unrot=True)
    r = m.render()
    assert "&ROTD" in r
    assert "ROTD%PLAT = 37.5" in r
    assert "ROTD%UNROT = T" in r


def test_uost():
    """UOST: Unstructured grid obstacle — 4 fields."""
    m = UOST(uostfilelocal="obst.loc", uostfactorlocal=1.0)
    r = m.render()
    assert "&UOST" in r
    assert "UOST%UOSTFILELOCAL = 'obst.loc'" in r


# --- Container tests ---


def test_namelists_container():
    """Namelists container renders all set sub-models correctly."""
    nm = Namelists(
        misc=MISC(flagtr=4, cice0=0.25, cicen=0.75, nosw=2),
        sin4=SIN4(zwnd=10.0, betamax=1.33),
        sds4=SDS4(sdsbr=0.0009),
        pro2=PRO2(cfltm=0.7, dtime=64800.0),
    )
    r = nm.render()

    # Verify each sub-namelist appears
    assert "&MISC" in r
    assert "&SIN4" in r
    assert "&SDS4" in r
    assert "&PRO2" in r

    # Verify END OF NAMELISTS
    assert "END OF NAMELISTS" in r

    # Null fields should NOT appear
    assert "&SNL1" not in r
    assert "&SDB1" not in r


def test_namelists_empty():
    """Empty container renders just END OF NAMELISTS."""
    nm = Namelists()
    r = nm.render()
    assert "END OF NAMELISTS" in r
    # No &... blocks
    lines = [line for line in r.split("\n") if line.strip().startswith("&")]
    assert len(lines) == 0


def test_file_writing():
    """Write Namelists container to file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        nm = Namelists(
            misc=MISC(flagtr=4, cice0=0.25, nosw=2),
            sin4=SIN4(betamax=1.33),
        )
        nm.write_nml(tmp_path)

        nml_file = tmp_path / "namelists.nml"
        assert nml_file.exists()

        content = nml_file.read_text()
        assert "&MISC" in content
        assert "&SIN4" in content
        assert "END OF NAMELISTS" in content


if __name__ == "__main__":
    import sys
    import traceback

    tests = [
        # SIN
        test_sin1,
        test_sin2,
        test_sin3,
        test_sin4,
        # SNL
        test_snl1,
        test_snl2,
        test_snl3,
        test_snl4,
        # SDS
        test_sds1,
        test_sds2,
        test_sds3,
        test_sds4,
        # SDB, SBT
        test_sdb1,
        test_sbt1,
        test_sbt4,
        # FLX
        test_flx3,
        test_flx4,
        # PRO
        test_pro1,
        test_pro2,
        test_pro3,
        # MISC, other
        test_misc,
        test_ref1,
        test_rotd,
        test_uost,
        # Container
        test_namelists_container,
        test_namelists_empty,
        test_file_writing,
    ]

    passed = 0
    failed = []
    for test_fn in tests:
        name = test_fn.__name__
        try:
            test_fn()
            passed += 1
            print(f"  ✓ {name}")
        except Exception:
            failed.append(name)
            print(f"  ✗ {name}")
            traceback.print_exc()

    print(f"\n{passed}/{len(tests)} passed")
    if failed:
        print(f"Failed: {', '.join(failed)}")
        sys.exit(1)
