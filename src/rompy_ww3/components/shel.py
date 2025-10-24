"""Shell component for WW3 configuration."""

from typing import List, Optional
from ..namelists.domain import Domain
from ..namelists.input import Input
from ..namelists.output_type import OutputType
from ..namelists.output_date import OutputDate
from ..namelists.homogeneous import HomogCount, HomogInput
from .basemodel import WW3ComponentBaseModel


class Shel(WW3ComponentBaseModel):
    """Component for ww3_shel.nml containing shell configuration."""

    domain: Optional[Domain] = None
    input_nml: Optional[Input] = None
    output_type: Optional[OutputType] = None
    output_date: Optional[OutputDate] = None
    homog_count: Optional[HomogCount] = None
    homog_input: Optional[List[HomogInput]] = None
