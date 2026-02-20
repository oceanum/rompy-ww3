import pytest
from pathlib import Path

from rompy_ww3.postprocess.naming import (
    normalize_datestamp,
    compute_restart_valid_date,
    compute_target_name,
)


def test_normalize_datestamp_ww3_format():
    assert normalize_datestamp("20100101 000000") == "20100101_000000"


def test_normalize_datestamp_iso_format():
    assert normalize_datestamp("2010-01-01 00:00:00") == "20100101_000000"


def test_compute_restart_valid_date():
    result = compute_restart_valid_date(
        Path("restart.ww3"),
        "20100101 000000",
        3600,
    )
    assert result == "20100101_000000"


def test_compute_target_name_non_restart():
    result = compute_target_name(
        Path("out_grd.ww3"),
        date_str="20100101 000000",
    )
    assert result == "20100101_000000_out_grd.ww3"


def test_compute_target_name_restart():
    result = compute_target_name(
        Path("restart.ww3"),
        is_restart=True,
        start_date="20100101 000000",
        output_stride=3600,
    )
    assert result == "20100101_000000_restart.ww3"


def test_compute_target_name_missing_params_raises():
    with pytest.raises(ValueError, match="date_str required"):
        compute_target_name(Path("out_grd.ww3"))

    with pytest.raises(ValueError, match="start_date and output_stride required"):
        compute_target_name(Path("restart.ww3"), is_restart=True)
