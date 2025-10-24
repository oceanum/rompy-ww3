"""Physics parameter namelist implementations for WW3 model parameters.

This module contains the various physics parameter namelists used by WW3.
Each namelist corresponds to a specific aspect of the wave model physics.
"""

from typing import Optional, Literal
from pydantic import Field
from ..namelists.basemodel import NamelistBaseModel


class MISC(NamelistBaseModel):
    """&MISC namelist for WW3 miscellaneous parameters.

    Contains various parameters that don't fit into other specific categories.
    """

    # Partitioning parameters
    ptmeth: Optional[int] = Field(
        default=None,
        description="Partitioning method: 1=standard, 2=Met ext, 3=waves, 4=classic, 5=2-band",
    )
    ptfcut: Optional[float] = Field(
        default=None,
        description="Partitioning frequency cutoff for 2-band partitioning (Hz)",
    )

    # Wind correction parameters
    flagtr: Optional[int] = Field(
        default=None,
        description="Wind correction: 0=none, 1=const, 2=smooth, 3=smooth+shallow",
    )

    # Calendar type
    caltyp: Optional[int] = Field(
        default=None,
        description="Calendar type: 1=standard, 2=360-day, 3=365-day, 4=366-day",
    )

    # Output parameters
    cice0: Optional[float] = Field(
        default=None, description="Initial ice concentration for output"
    )
    cicen: Optional[float] = Field(
        default=None, description="Ice concentration normalization factor"
    )

    # Obstruction parameters
    xp: Optional[float] = Field(
        default=None, description="Obstruction fraction threshold"
    )


class FLX(NamelistBaseModel):
    """&FLX namelist for WW3 flux parameters.

    Parameters related to flux calculations and wind drag.
    """

    cdmax: Optional[float] = Field(
        default=None, description="Maximum wind drag coefficient"
    )
    cdrag: Optional[float] = Field(
        default=None, description="Constant wind drag coefficient"
    )
    cdu10n: Optional[float] = Field(
        default=None, description="Neutral 10-m drag coefficient"
    )
    alwmin: Optional[float] = Field(
        default=None, description="Lower limit for air-water temperature difference (K)"
    )
    alwmax: Optional[float] = Field(
        default=None, description="Upper limit for air-water temperature difference (K)"
    )
    cetype: Optional[int] = Field(
        default=None, description="Type of formulation for convective effects"
    )
    cdtype: Optional[int] = Field(
        default=None, description="Type of drag coefficient formulation"
    )


class SIN1(NamelistBaseModel):
    """&SIN1 namelist for WW3 first wind input physics parameters.

    Contains parameters for the first wind input physics (typically default or Komen).
    """

    cdwind: Optional[float] = Field(
        default=None, description="Wind drag coefficient for wind input"
    )
    ust_min: Optional[float] = Field(
        default=None, description="Minimum friction velocity (m/s)"
    )


class SIN2(NamelistBaseModel):
    """&SIN2 namelist for WW3 second wind input physics parameters.

    Contains parameters for the second wind input physics.
    """

    cdwind: Optional[float] = Field(
        default=None, description="Wind drag coefficient for wind input"
    )


class SIN3(NamelistBaseModel):
    """&SIN3 namelist for WW3 third wind input physics parameters.

    Contains parameters for the third wind input physics.
    """

    ust_min: Optional[float] = Field(
        default=None, description="Minimum friction velocity (m/s)"
    )


class SIN4(NamelistBaseModel):
    """&SIN4 namelist for WW3 fourth wind input physics parameters.

    Contains parameters for the fourth wind input physics.
    """

    cdwind: Optional[float] = Field(
        default=None, description="Wind drag coefficient for wind input"
    )


class SNL1(NamelistBaseModel):
    """&SNL1 namelist for WW3 first nonlinear interaction physics parameters.

    Contains parameters for the first nonlinear interaction computation (typically default).
    """

    nlnsta: Optional[int] = Field(
        default=None, description="Nonlinear interaction switch: 0=off, 1=on"
    )
    nlnint: Optional[Literal["DIS", "INT"]] = Field(
        default=None,
        description="Nonlinear interaction type: DIS=discrete, INT=integrated",
    )
    nlnsub: Optional[int] = Field(
        default=None, description="Nonlinear interaction subgrid method"
    )


class SNL2(NamelistBaseModel):
    """&SNL2 namelist for WW3 second nonlinear interaction physics parameters.

    Contains parameters for the second nonlinear interaction computation.
    """

    nlnsta: Optional[int] = Field(
        default=None, description="Nonlinear interaction switch: 0=off, 1=on"
    )


class SNL3(NamelistBaseModel):
    """&SNL3 namelist for WW3 third nonlinear interaction physics parameters.

    Contains parameters for the third nonlinear interaction computation.
    """

    nlnsta: Optional[int] = Field(
        default=None, description="Nonlinear interaction switch: 0=off, 1=on"
    )


class SNL4(NamelistBaseModel):
    """&SNL4 namelist for WW3 fourth nonlinear interaction physics parameters.

    Contains parameters for the fourth nonlinear interaction computation.
    """

    nlnsta: Optional[int] = Field(
        default=None, description="Nonlinear interaction switch: 0=off, 1=on"
    )


class SDS1(NamelistBaseModel):
    """&SDS1 namelist for WW3 first whitecapping physics parameters.

    Contains parameters for the first whitecapping physics (typically Komen formulation).
    """

    alpha_bc: Optional[float] = Field(
        default=None, description="Alpha parameter for Komen whitecapping formulation"
    )
    scale_bc: Optional[float] = Field(
        default=None, description="Scaling factor for Komen whitecapping"
    )
    frhchp: Optional[float] = Field(
        default=None, description="Frequency threshold for high frequency whitecapping"
    )


class SDS2(NamelistBaseModel):
    """&SDS2 namelist for WW3 second whitecapping physics parameters.

    Contains parameters for the second whitecapping physics (typically Janssen formulation).
    """

    alpha_j: Optional[float] = Field(
        default=None, description="Alpha parameter for Janssen whitecapping formulation"
    )
    csds2: Optional[float] = Field(
        default=None, description="Parameter for Janssen whitecapping"
    )


class SDS3(NamelistBaseModel):
    """&SDS3 namelist for WW3 third whitecapping physics parameters.

    Contains parameters for the third whitecapping physics (typically Westhuysen formulation).
    """

    alpha_w: Optional[float] = Field(
        default=None,
        description="Alpha parameter for Westhuysen whitecapping formulation",
    )
    cmax_w: Optional[float] = Field(
        default=None, description="Maximum wave steepness for Westhuysen formulation"
    )
    brbr_w: Optional[float] = Field(
        default=None, description="Breaking parameter for Westhuysen formulation"
    )


class SDS4(NamelistBaseModel):
    """&SDS4 namelist for WW3 fourth whitecapping physics parameters.

    Contains parameters for the fourth whitecapping physics.
    """

    alpha_bc: Optional[float] = Field(
        default=None, description="Alpha parameter for whitecapping formulation"
    )


class SBT(NamelistBaseModel):
    """&SBT namelist for WW3 bottom friction physics parameters.

    Contains parameters for bottom friction computation.
    """

    cfbot: Optional[float] = Field(
        default=None, description="Bottom friction coefficient"
    )
    fric_type: Optional[str] = Field(
        default=None, description="Type of bottom friction formulation"
    )


class SDB(NamelistBaseModel):
    """&SDB namelist for WW3 surf/depth-induced breaking physics parameters.

    Contains parameters for surf and depth-induced breaking.
    """

    cfshak: Optional[float] = Field(
        default=None, description="Shallow water wave breaking coefficient"
    )
    brkfac: Optional[float] = Field(
        default=None, description="Breaking factor for depth-induced breaking"
    )


class PRO1(NamelistBaseModel):
    """&PRO1 namelist for WW3 first propagation scheme parameters.

    Contains parameters for the first propagation scheme (typically default).
    """

    prop_scheme: Optional[str] = Field(
        default=None, description="Scheme for wave propagation"
    )


class PRO2(NamelistBaseModel):
    """&PRO2 namelist for WW3 second propagation scheme parameters.

    Contains parameters for the second propagation scheme.
    """

    dtime: Optional[float] = Field(
        default=None, description="Time step for propagation (seconds)"
    )


class PRO3(NamelistBaseModel):
    """&PRO3 namelist for WW3 third propagation scheme parameters.

    Contains parameters for the third propagation scheme (typically for CG/WRT).
    """

    wdthcg: Optional[float] = Field(
        default=None, description="Width of CG region for propagation"
    )
    wdthth: Optional[float] = Field(
        default=None, description="Width of theta region for propagation"
    )


class PRO4(NamelistBaseModel):
    """&PRO4 namelist for WW3 fourth propagation scheme parameters.

    Contains parameters for the fourth propagation scheme (typically for refraction).
    """

    rnfac: Optional[float] = Field(default=None, description="Refraction factor")
    rsfac: Optional[float] = Field(
        default=None, description="Refraction smoothing factor"
    )


class Namelists(NamelistBaseModel):
    """Container for all WW3 physics parameter namelists.

    This model contains all the individual physics parameter components
    that make up the namelists.nml file in WW3.
    """

    misc: Optional[MISC] = Field(
        default=None, description="MISC namelist for miscellaneous parameters"
    )
    flx: Optional[FLX] = Field(
        default=None, description="FLX namelist for flux parameters"
    )
    sin1: Optional[SIN1] = Field(
        default=None,
        description="SIN1 namelist for first wind input physics parameters",
    )
    sin2: Optional[SIN2] = Field(
        default=None,
        description="SIN2 namelist for second wind input physics parameters",
    )
    sin3: Optional[SIN3] = Field(
        default=None,
        description="SIN3 namelist for third wind input physics parameters",
    )
    sin4: Optional[SIN4] = Field(
        default=None,
        description="SIN4 namelist for fourth wind input physics parameters",
    )
    snl1: Optional[SNL1] = Field(
        default=None,
        description="SNL1 namelist for first nonlinear interaction physics parameters",
    )
    snl2: Optional[SNL2] = Field(
        default=None,
        description="SNL2 namelist for second nonlinear interaction physics parameters",
    )
    snl3: Optional[SNL3] = Field(
        default=None,
        description="SNL3 namelist for third nonlinear interaction physics parameters",
    )
    snl4: Optional[SNL4] = Field(
        default=None,
        description="SNL4 namelist for fourth nonlinear interaction physics parameters",
    )
    sds1: Optional[SDS1] = Field(
        default=None,
        description="SDS1 namelist for first whitecapping physics parameters",
    )
    sds2: Optional[SDS2] = Field(
        default=None,
        description="SDS2 namelist for second whitecapping physics parameters",
    )
    sds3: Optional[SDS3] = Field(
        default=None,
        description="SDS3 namelist for third whitecapping physics parameters",
    )
    sds4: Optional[SDS4] = Field(
        default=None,
        description="SDS4 namelist for fourth whitecapping physics parameters",
    )
    sbt: Optional[SBT] = Field(
        default=None, description="SBT namelist for bottom friction physics parameters"
    )
    sdb: Optional[SDB] = Field(
        default=None,
        description="SDB namelist for surf/depth-induced breaking physics parameters",
    )
    pro1: Optional[PRO1] = Field(
        default=None,
        description="PRO1 namelist for first propagation scheme parameters",
    )
    pro2: Optional[PRO2] = Field(
        default=None,
        description="PRO2 namelist for second propagation scheme parameters",
    )
    pro3: Optional[PRO3] = Field(
        default=None,
        description="PRO3 namelist for third propagation scheme parameters",
    )
    pro4: Optional[PRO4] = Field(
        default=None,
        description="PRO4 namelist for fourth propagation scheme parameters",
    )

    def render(self, *args, **kwargs) -> str:
        """Custom render  for namelists as a string."""

        content = []
        # Get the model data
        model_data = self.model_dump()
        for key, value in model_data.items():
            if value is None:
                continue
            line = f"&{key.upper()}"
            separator = " "
            for sub_key, sub_value in value.items():
                line += f"{separator}{sub_key.upper()} = {sub_value}"
                separator = ", "
            line += " /"
            content.append(line)

        content.append("END OF NAMELISTS")
        return "\n".join(content)
