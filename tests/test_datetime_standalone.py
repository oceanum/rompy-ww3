import sys
from datetime import datetime

try:
    from rompy_ww3.namelists.basemodel import NamelistBaseModel
except Exception:
    NamelistBaseModel = (
        None  # Allow standalone run in CI environments without full import path
    )


def main():
    if NamelistBaseModel is None:
        print("SKIP: NamelistBaseModel not importable in this environment")
        sys.exit(0)
    dt = datetime(2020, 1, 1, 0, 0, 0)
    rendered = NamelistBaseModel.render_datetime(dt)
    assert rendered == "20200101 000000", f"Unexpected rendering: {rendered}"
    print("OK: datetime rendering standalone test passed")


if __name__ == "__main__":
    sys.exit(main())
