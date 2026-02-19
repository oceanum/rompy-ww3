from datetime import datetime

from rompy_ww3.namelists.basemodel import NamelistBaseModel


def test_render_datetime_basic():
    dt = datetime(2021, 12, 31, 23, 59, 59)
    rendered = NamelistBaseModel.render_datetime(dt)
    assert rendered == "20211231 235959"
