"""Track component for WW3 configuration."""

from typing import Optional
from ..namelists.track import Track
from .basemodel import WW3ComponentBaseModel


class Trnc(WW3ComponentBaseModel):
    """Component for ww3_trnc.nml containing track output configuration."""

    track: Optional[Track] = None
