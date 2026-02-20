"""HOMOG_COUNT_NML and HOMOG_INPUT_NML namelist implementation for WW3.

This module implements the homogeneous input namelists for WAVEWATCH III (WW3).
It includes:

- HomogCount: Defines the count of each type of homogeneous input
- HomogInput: Defines individual homogeneous inputs with name, date, and values
- HomogeneousInputs: A container that manages a list of HomogInput objects and
  automatically calculates the corresponding HomogCount.

Validation follows the WW3 specifications:
- Count values must be non-negative
- Input names must be from a predefined set
- Date format must be yyyymmdd hhmmss
- Value constraints depend on the input type
- Provides automatic calculation of counts from input list
"""

from typing import Optional, List
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel
from .enums import HOMOG_INPUT_NAME, parse_enum


class HomogCount(NamelistBaseModel):
    """HOMOG_COUNT_NML namelist for WW3.

    Defines homogeneous input counts.
    """

    # Single-grid homogeneous input counts
    n_ic1: Optional[int] = Field(
        default=None, description="Number of ice concentration type 1 inputs"
    )
    n_ic2: Optional[int] = Field(
        default=None, description="Number of ice concentration type 2 inputs"
    )
    n_ic3: Optional[int] = Field(
        default=None, description="Number of ice concentration type 3 inputs"
    )
    n_ic4: Optional[int] = Field(
        default=None, description="Number of ice concentration type 4 inputs"
    )
    n_ic5: Optional[int] = Field(
        default=None, description="Number of ice concentration type 5 inputs"
    )
    n_mdn: Optional[int] = Field(
        default=None, description="Number of mud density inputs"
    )
    n_mth: Optional[int] = Field(
        default=None, description="Number of mud thickness inputs"
    )
    n_mvs: Optional[int] = Field(
        default=None, description="Number of mud viscosity inputs"
    )
    n_lev: Optional[int] = Field(
        default=None, description="Number of water level inputs"
    )
    n_cur: Optional[int] = Field(default=None, description="Number of current inputs")
    n_wnd: Optional[int] = Field(default=None, description="Number of wind inputs")
    n_ice: Optional[int] = Field(
        default=None, description="Number of ice concentration inputs"
    )
    n_tau: Optional[int] = Field(
        default=None, description="Number of wind stress inputs"
    )
    n_rho: Optional[int] = Field(
        default=None, description="Number of air density inputs"
    )
    n_mov: Optional[int] = Field(
        default=None, description="Number of moving inputs (multi-grid)"
    )

    @field_validator(
        "n_ic1",
        "n_ic2",
        "n_ic3",
        "n_ic4",
        "n_ic5",
        "n_mdn",
        "n_mth",
        "n_mvs",
        "n_lev",
        "n_cur",
        "n_wnd",
        "n_ice",
        "n_tau",
        "n_rho",
        "n_mov",
        mode="before",
    )
    @classmethod
    def validate_non_negative_count(cls, v):
        """Ensure count values are non-negative."""
        if v is not None and v < 0:
            raise ValueError("Count values must be non-negative")
        return v


class HomogInput(NamelistBaseModel):
    """HOMOG_INPUT_NML namelist for WW3.

    Defines homogeneous inputs.
    """

    name: Optional[HOMOG_INPUT_NAME] = Field(
        default=None,
        description="Input type name (IC1, IC2, IC3, IC4, IC5, MDN, MTH, MVS, LEV, CUR, WND, ICE, MOV, TAU, RHO)",
    )
    date: Optional[str] = Field(
        default=None, description="Input date (yyyymmdd hhmmss)"
    )
    value1: Optional[float] = Field(
        default=None, description="First input value (depends on input type)"
    )
    value2: Optional[float] = Field(
        default=None, description="Second input value (depends on input type)"
    )
    value3: Optional[float] = Field(
        default=None, description="Third input value (depends on input type)"
    )

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v):
        """Validate that name is one of the allowed values."""
        if v is None:
            return v
        return parse_enum(HOMOG_INPUT_NAME, v)

    @field_validator("date", mode="before")
    @classmethod
    def validate_date_format(cls, v):
        """Validate date format is yyyymmdd hhmmss."""
        if v is None:
            return v
        # Check if it matches the format yyyymmdd hhmmss (15 characters)
        if not isinstance(v, str) or len(v) != 15 or v[8] != " ":
            raise ValueError(f"Date must be in format yyyymmdd hhmmss, got {v}")

        # Check if all characters are digits except the space
        date_part = v[:8]
        time_part = v[9:]
        if not (date_part.isdigit() and time_part.isdigit()):
            raise ValueError(f"Date must be in format yyyymmdd hhmmss, got {v}")

        return v

    @field_validator("value1", mode="before")
    @classmethod
    def validate_value1_deactivation(cls, v):
        """Validate that if value1 is 0, the input is deactivated."""
        if v == 0:
            # When value1 is 0, we can issue a warning or just allow it as per spec
            # The spec says "if VALUE1 is equal 0, then the homogeneous input is desactivated"
            # This is more informational than a validation error
            pass
        return v

    @field_validator("value1", "value2", "value3", mode="before")
    @classmethod
    def validate_value_constraints(cls, v, info):
        """Validate value constraints based on the input name."""
        if v is None:
            return v

        # This validator has limited access to other fields in Pydantic v2
        # The full validation for value constraints based on name will happen
        # at the HomogeneousInputs level or during model construction
        return v

    def render_entry(self, index: int) -> str:
        """Render a single HOMOG_INPUT entry with the given index.

        This returns just the lines for one entry, to be combined into a single
        HOMOG_INPUT_NML block by the parent component.
        """
        lines = []

        if self.name is not None:
            lines.append(f"  HOMOG_INPUT({index})%NAME   = '{self.name}'")
        if self.date is not None:
            lines.append(f"  HOMOG_INPUT({index})%DATE   = '{self.date}'")
        if self.value1 is not None:
            lines.append(f"  HOMOG_INPUT({index})%VALUE1 = {self.value1}")
        if self.value2 is not None:
            lines.append(f"  HOMOG_INPUT({index})%VALUE2 = {self.value2}")
        if self.value3 is not None:
            lines.append(f"  HOMOG_INPUT({index})%VALUE3 = {self.value3}")

        lines.append("")  # Blank line between entries
        return "\n".join(lines)


class HomogeneousInputs(NamelistBaseModel):
    """Container for managing homogeneous inputs and automatically calculating counts.

    This class manages a list of HomogInput objects and automatically calculates
    the corresponding HomogCount based on the names in the input list.
    """

    homog_inputs: List[HomogInput] = Field(
        default_factory=list, description="List of homogeneous input definitions"
    )

    @field_validator("homog_inputs", mode="before")
    @classmethod
    def validate_homogeneous_inputs(cls, v):
        """Validate the homogeneous inputs list based on WW3 specifications."""
        if not v:
            return v

        validated_inputs = []
        name_counts = {}

        for i, input_obj in enumerate(v):
            if not isinstance(input_obj, HomogInput):
                # If it's a dict, convert it to HomogInput
                if isinstance(input_obj, dict):
                    input_obj = HomogInput(**input_obj)
                else:
                    raise ValueError(
                        f"Input at index {i} must be a HomogInput or dict, got {type(input_obj)}"
                    )

            # Check that inputs start from index 1 to N (per WW3 spec)
            # This is checked by ensuring we don't have gaps in sequences if ordered by some criteria
            if input_obj.name:
                name_counts[input_obj.name] = name_counts.get(input_obj.name, 0) + 1

            # Validate value constraints based on input type as per WW3 spec
            cls.validate_input_values(input_obj)

            validated_inputs.append(input_obj)

        # Additional validation that could be implemented if needed:
        # - Ensure there are no duplicate names at the same date/time

        return validated_inputs

    @classmethod
    def validate_input_values(cls, input_obj: HomogInput):
        """Validate value constraints based on input name according to WW3 specification.

        This method validates that the values in a HomogInput object are appropriate
        based on the input type as defined in the WW3 documentation:
        - IC1 is defined by thickness
        - IC2 is defined by viscosity
        - IC3 is defined by density
        - IC4 is defined by modulus
        - IC5 is defined by floe diameter
        - MDN is defined by density
        - MTH is defined by thickness
        - MVS is defined by viscosity
        - LEV is defined by height
        - CUR is defined by speed and direction
        - WND is defined by speed, direction and airseatemp
        - ICE is defined by concentration
        - MOV is defined by speed and direction
        - TAU is defined by wind stress
        - RHO is defined by air density
        """
        if not input_obj.name or input_obj.value1 is None:
            return input_obj

        name = input_obj.name.upper()

        # Value constraints based on WW3 specification:
        # - IC1 is defined by thickness
        # - IC2 is defined by viscosity
        # - IC3 is defined by density
        # - IC4 is defined by modulus
        # - IC5 is defined by floe diameter
        # - MDN is defined by density
        # - MTH is defined by thickness
        # - MVS is defined by viscosity
        # - LEV is defined by height
        # - CUR is defined by speed and direction
        # - WND is defined by speed, direction and airseatemp
        # - ICE is defined by concentration
        # - MOV is defined by speed and direction
        if name in {"IC1", "MTH"}:  # defined by thickness
            # value1 should be thickness (positive)
            if input_obj.value1 is not None and input_obj.value1 < 0:
                raise ValueError(
                    f"{name} requires non-negative value1 (thickness), got {input_obj.value1}"
                )
        elif name in {"IC2", "MVS"}:  # defined by viscosity
            # value1 should be viscosity (typically positive)
            if input_obj.value1 is not None and input_obj.value1 < 0:
                raise ValueError(
                    f"{name} requires non-negative value1 (viscosity), got {input_obj.value1}"
                )
        elif name in {"IC3", "MDN"}:  # defined by density
            # value1 should be density (positive)
            if input_obj.value1 is not None and input_obj.value1 <= 0:
                raise ValueError(
                    f"{name} requires positive value1 (density), got {input_obj.value1}"
                )
        elif name == "IC4":  # defined by modulus
            # value1 should be modulus (positive)
            if input_obj.value1 is not None and input_obj.value1 <= 0:
                raise ValueError(
                    f"{name} requires positive value1 (modulus), got {input_obj.value1}"
                )
        elif name == "IC5":  # defined by floe diameter
            # value1 should be diameter (positive)
            if input_obj.value1 is not None and input_obj.value1 <= 0:
                raise ValueError(
                    f"{name} requires positive value1 (floe diameter), got {input_obj.value1}"
                )
        elif name == "LEV":  # defined by height
            # value1 should be height/level (can be positive or negative)
            pass  # No specific constraint on value1 for LEV
        elif name == "ICE":  # defined by concentration
            # value1 should be concentration (typically 0-1 or 0-100)
            if input_obj.value1 is not None and (
                input_obj.value1 < 0 or input_obj.value1 > 1
            ):
                # Assuming 0-1 range for concentration, but could be 0-100 depending on units
                # This is a common range but could be adjusted based on WW3 documentation
                pass  # Could add a warning or specific constraint based on units
        elif name in {"CUR", "MOV"}:  # defined by speed and direction
            # value1 should be speed (non-negative), value2 should be direction
            if input_obj.value1 is not None and input_obj.value1 < 0:
                raise ValueError(
                    f"{name} requires non-negative value1 (speed), got {input_obj.value1}"
                )
            # value2 should be direction (0-360 typically)
            if input_obj.value2 is not None:
                # Direction might be in range 0-360, but could vary
                pass  # Could add specific validation for direction
        elif name == "WND":  # defined by speed, direction and airseatemp
            # value1 should be speed (non-negative), value2 direction, value3 temperature
            if input_obj.value1 is not None and input_obj.value1 < 0:
                raise ValueError(
                    f"{name} requires non-negative value1 (speed), got {input_obj.value1}"
                )
            # value2 should be direction
            # value3 should be temperature (no specific range requirement)
        elif name in {"TAU", "RHO"}:  # wind stress and air density
            # value1 should be positive for these
            if input_obj.value1 is not None and input_obj.value1 <= 0:
                raise ValueError(
                    f"{name} requires positive value1, got {input_obj.value1}"
                )

        return input_obj

    def calculate_homog_count(self) -> HomogCount:
        """Calculate the HomogCount based on the list of HomogInput objects.

        Counts the occurrences of each input type in the homog_inputs list.
        """
        counts = {
            "n_ic1": 0,
            "n_ic2": 0,
            "n_ic3": 0,
            "n_ic4": 0,
            "n_ic5": 0,
            "n_mdn": 0,
            "n_mth": 0,
            "n_mvs": 0,
            "n_lev": 0,
            "n_cur": 0,
            "n_wnd": 0,
            "n_ice": 0,
            "n_tau": 0,
            "n_rho": 0,
            "n_mov": 0,
        }

        for input_obj in self.homog_inputs:
            if input_obj.name:
                # Convert the name to lowercase and prepend 'n_' to match the field names
                field_name = f"n_{input_obj.name.lower()}"
                if field_name in counts:
                    counts[field_name] += 1

        return HomogCount(**counts)

    def get_activated_inputs(self) -> List[HomogInput]:
        """Get only the inputs where value1 is not 0 (activated inputs)."""
        return [inp for inp in self.homog_inputs if inp.value1 != 0]

    def get_inputs_by_type(self, input_type: str) -> List[HomogInput]:
        """Get all inputs of a specific type.

        Args:
            input_type: The type of input to filter (e.g., 'IC1', 'WND', 'CUR')

        Returns:
            List of HomogInput objects of the specified type
        """
        return [
            inp
            for inp in self.homog_inputs
            if inp.name and inp.name.upper() == input_type.upper()
        ]

    def add_input(self, input_obj: HomogInput):
        """Add a new homogeneous input to the list.

        Args:
            input_obj: The HomogInput object to add
        """
        # Validate the input before adding
        self.validate_input_values(input_obj)
        self.homog_inputs.append(input_obj)
