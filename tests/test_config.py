from importlib.metadata import entry_points
from rompy_ww3.config import Config


def test_config_entrypoint():
    eps = entry_points(group="rompy.config")
    names = [ep.name for ep in eps]
    assert "ww3" in names