"""WW3 Rompy data."""

import logging
from pathlib import Path
from typing import Literal, Optional, List, Union
from pydantic import Field

from rompy.core.data import DataBase

# Import the existing WW3 namelist objects


logger = logging.getLogger(__name__)

HERE = Path(__file__).parent


class DataAssimilation(DataBase):
    """Ww3 data class with WW3-specific data handling capabilities.

    This class extends DataBase with WW3-specific data handling for wave model inputs.
    It uses rompy Source objects to read large lazy datasets, crops the required
    area and time from the data, writes to the rompy WW3 workspace, and updates
    the appropriate nml objects internally to point to the processed files.
    """

    model_type: Literal["assimilation"] = Field(
        default="ww3",
        description="Model type discriminator",
    )

    assimilation_values: Optional[List[float]] = Field(
        default=None,
        description="Assimilation values for data (used when assim_flag = 'T')",
    )

    def assimilation_flag(self) -> str:
        """Return the assimilation flag for assimilation data."""
        return "T"

    def description(self) -> str:
        """Return a description of the assimilation data."""
        return "This class handles assimilation data specifically for the WW3 model."

    def get(self, destdir: Union[str, Path], *args, **kwargs) -> Path:
        """Retrieve, process and save WW3 assimilation data.

        This method will use the source to retrieve data, then process it
        by cropping to the required time and area, and save the processed
        netCDF file to the specified destination. It also creates the namelist
        file needed for external ww3_prnc processing.

        Args:
            destdir: Destination directory to save the processed file and namelist
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        Returns:
            Path to the WW3-ready output file (after external ww3_prnc processing)
        """
        raise NotImplementedError("Assimilation data handling is not yet implemented.")


# def WW3Forcing(RompyBaseModel):
#     """Combined forcing namelist component for WW3 preprocessing."""
#
#     model_type: Literal["forcing"] = Field(
#         default="forcing", description="Model type discriminator for forcing"
#     )
#     winds: Optional[Prnc] = Field(
#         default=None, description="Wind forcing input configuration"
#     )
#     currents: Optional[Prnc] = Field(
#         default=None, description="Current forcing input configuration"
#     )
#     water_levels: Optional[Prnc] = Field(
#         default=None, description="Water level forcing input configuration"
#     )
#     ice_conc: Optional[Prnc] = Field(
#         default=None, description="Ice concentration forcing input configuration"
#     )
#     air_density: Optional[Prnc] = Field(
#         default=None, description="Air density forcing input configuration"
#     )
#     atm_momentum: Optional[Prnc] = Field(
#         default=None, description="Atmospheric momentum forcing input configuration"
#     )
#     mud_density: Optional[Prnc] = Field(
#         default=None, description="Mud density forcing input configuration"
#     )
#     mud_thickness: Optional[Prnc] = Field(
#         default=None, description="Mud thickness forcing input configuration"
#     )
#     mud_viscosity: Optional[Prnc] = Field(
#         default=None, description="Mud viscosity forcing input configuration"
#     )
#
#     @model_validator(mode="before")
#     def set_forcing_field(cls, values):
#         # When a Prnc object is provided to a specific  field,
#         # automatically set the corresponding forcing field  variable
#         for field_name, prnc_obj in values.items():
#             if isinstance(prnc_obj, Prnc):
#                 # Create a ForcingField with the appropriate variable
#                 forcing_field = ForcingField(variable=field_name)
#                 # Update the prnc_obj.forcing.field to use  this forcing_field
#                 if prnc_obj.forcing is None:
#                     prnc_obj.forcing = Forcing(field=forcing_field)
#                 else:
#                     prnc_obj.forcing.field = forcing_field
#         return values
#
#     def get_forcingfield_nml(self):
#         """Get the Forcing namelist object."""
#         # Prepare field configuration
#         # loop through all possible forcing fields
#         field_config: Dict[str, Any] = {}
#         for field_name in FIELD_VARIABLE_CHOICES:
#             prnc_obj = getattr(self, field_name)
#             if isinstance(prnc_obj, Prnc) and prnc_obj.forcing is not None:
#                 field_config["variable"] = "T"
#             else:
#                 field_config["variable"] = "F"
#         forcing_field = ForcingField(**field_config)
#
#         # Create ForcingGrid based on grid_type
#         grid_params = {self.grid_type: True}
#         forcing_grid = ForcingGrid(**grid_params)
#
#         # Create the main Forcing object
#         forcing = Forcing(
#             field=forcing_field,
#             grid=forcing_grid,
#         )
#
#         return forcing
#
#
# AnyWW3Data = TypingUnion[DataGrid, DataAssimilation]
AnyWW3Data = Union[DataAssimilation]
