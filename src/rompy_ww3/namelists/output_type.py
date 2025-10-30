"""OUTPUT_TYPE_NML namelist implementation for WW3."""

from typing import Optional, Union
from pydantic import Field, field_validator

from .basemodel import NamelistBaseModel
from ..core.data import WW3DataBlob


class OutputTypeField(NamelistBaseModel):
    """Field output parameters for WW3.

    The TYPE%FIELD namelist defines which field parameters to output in the wave model.
    The list can include various parameters from different groups like forcing fields,
    mean wave parameters, spectral parameters, etc. The full list of available field
    parameters can be extensive and includes items like:
    - Water depth (DPT)
    - Current velocity (CUR)
    - Wind speed (WND)
    - Wave height (HS)
    - Mean wave period (T02, T0M1, T01)
    - Peak frequency (FP0)
    - Mean wave direction (DIR)
    - Mean directional spread (SPR)
    - Peak direction (DP)
    - Wave frequency spectrum (EF)
    - Partitioned wave parameters (PHS, PTP, PLP, etc.)
    - Various other atmospheric, oceanic and wave parameters
    """

    list: Optional[Union[str, WW3DataBlob]] = Field(
        default=None,
        description=(
            "List of field parameters to output as space-separated values. "
            "This specifies which wave model parameters to write to the output files. "
            "Examples include: 'HS DIR SPR WND ICE CUR LEV' for significant wave height, "
            "direction, spread, wind speed, ice concentration, current velocity, and water levels."
        )
    )

    @field_validator('list')
    @classmethod
    def validate_field_list(cls, v):
        """Validate field list is a string if provided."""
        if v is not None and not isinstance(v, (str, WW3DataBlob)):
            raise ValueError(f"Field list must be a string or WW3DataBlob, got {type(v)}")
        return v


class OutputTypePoint(NamelistBaseModel):
    """Point output parameters for WW3.

    The TYPE%POINT namelist defines parameters for point output in WW3.
    The point file is a space separated values per line format: longitude latitude 'name'.
    """

    file: Optional[Union[str, WW3DataBlob]] = Field(
        default=None,
        description=(
            "Point output file specification containing space-separated values: "
            "longitude latitude 'name'. This file defines the specific points "
            "where output will be written during the simulation."
        )
    )
    name: Optional[str] = Field(
        default=None,
        description="Point output name, used to identify this point output configuration"
    )


class OutputTypeTrack(NamelistBaseModel):
    """Track output parameters for WW3.

    The TYPE%TRACK namelist controls track file output format in WW3.
    """

    format: Optional[bool] = Field(
        default=None,
        description=(
            "Track file format flag. If true, output track file is formatted (human-readable text). "
            "If false, output track file is unformatted (binary format). "
            "Formatted files are easier to read but take more disk space."
        )
    )

    @field_validator('format')
    @classmethod
    def validate_format_flag(cls, v):
        """Validate format flag is a boolean value."""
        if v is not None and not isinstance(v, bool):
            raise ValueError(f"Format flag must be a boolean value, got {type(v)}")
        return v


class OutputTypePartition(NamelistBaseModel):
    """Partition output parameters for WW3.

    The TYPE%PARTITION namelist defines parameters for partitioned output in WW3.
    """

    x0: Optional[int] = Field(
        default=None,
        description="Partition start X index, defines the starting X coordinate of the partition region",
        ge=0
    )
    xn: Optional[int] = Field(
        default=None,
        description="Partition end X index, defines the ending X coordinate of the partition region",
        ge=0
    )
    nx: Optional[int] = Field(
        default=None,
        description="Partition X resolution, defines the number of X cells in the partition",
        ge=0
    )
    y0: Optional[int] = Field(
        default=None,
        description="Partition start Y index, defines the starting Y coordinate of the partition region",
        ge=0
    )
    yn: Optional[int] = Field(
        default=None,
        description="Partition end Y index, defines the ending Y coordinate of the partition region",
        ge=0
    )
    ny: Optional[int] = Field(
        default=None,
        description="Partition Y resolution, defines the number of Y cells in the partition",
        ge=0
    )
    format: Optional[bool] = Field(
        default=None,
        description=(
            "Partition file format flag. If true, partition output file is formatted (human-readable text). "
            "If false, partition output file is unformatted (binary format)."
        )
    )

    @field_validator('format')
    @classmethod
    def validate_format_flag(cls, v):
        """Validate format flag is a boolean value."""
        if v is not None and not isinstance(v, bool):
            raise ValueError(f"Format flag must be a boolean value, got {type(v)}")
        return v


class OutputTypeCoupling(NamelistBaseModel):
    """Coupling output parameters for WW3.

    The TYPE%COUPLING namelist defines parameters for coupled model exchanges in WW3.
    """

    sent: Optional[str] = Field(
        default=None,
        description=(
            "List of fields sent in coupling exchange. This specifies which fields "
            "are sent from WW3 to the coupled model. Commonly sent fields include: "
            "T0M1 OCHA OHS DIR BHD TWO UBR FOC TAW TUS USS LM DRY to ocean models, "
            "ACHA AHS TP (or FP) FWS to atmospheric models, "
            "IC5 TWI to ice models."
        )
    )
    received: Optional[str] = Field(
        default=None,
        description=(
            "List of fields received in coupling exchange. This specifies which fields "
            "are received by WW3 from the coupled model. Commonly received fields include: "
            "SSH CUR from ocean models, WND from atmospheric models, "
            "ICE IC1 IC5 from ice models."
        )
    )
    couplet0: Optional[bool] = Field(
        default=None,
        description="Coupling at T+0 flag, controls whether coupling occurs at initial time step"
    )

    @field_validator('couplet0')
    @classmethod
    def validate_couplet0_flag(cls, v):
        """Validate couplet0 flag is a boolean value."""
        if v is not None and not isinstance(v, bool):
            raise ValueError(f"Couplet0 flag must be a boolean value, got {type(v)}")
        return v


class OutputTypeRestart(NamelistBaseModel):
    """Restart output parameters for WW3.

    The TYPE%RESTART section of the namelist defines parameters for restart output in WW3.
    """

    extra: Optional[str] = Field(
        default=None,
        description=(
            "Extra fields to write to restart file. This specifies additional fields "
            "beyond the standard restart fields that should be included in restart output."
        )
    )


class OutputType(NamelistBaseModel):
    """TYPE section of OUTPUT_TYPE_NML for WW3 (single-grid).

    The OUTPUT_TYPE_NML namelist defines the output types and parameters for 
    single-grid WAVEWATCH III runs. This namelist is read by the ww3_shel program.

    The namelist contains:
    - FIELD: Field output parameters specifying which parameters to output
    - POINT: Point output parameters defining specific point locations
    - TRACK: Track output format parameters
    - PARTITION: Partitioned output region parameters
    - COUPLING: Coupling exchange parameters for coupled models
    - RESTART: Restart output parameters
    """

    field: Optional[OutputTypeField] = Field(
        default=None, description="Field output parameters specifying which wave model parameters to output"
    )
    point: Optional[OutputTypePoint] = Field(
        default=None, description="Point output parameters defining specific point locations for output"
    )
    track: Optional[OutputTypeTrack] = Field(
        default=None, description="Track output format parameters (formatted/unformatted)"
    )
    partition: Optional[OutputTypePartition] = Field(
        default=None, description="Partitioned output region parameters defining sub-regions for output"
    )
    coupling: Optional[OutputTypeCoupling] = Field(
        default=None, description="Coupling exchange parameters for coupled model interactions"
    )
    restart: Optional[OutputTypeRestart] = Field(
        default=None, description="Restart output parameters specifying additional fields for restart files"
    )


class AllType(NamelistBaseModel):
    """ALLTYPE section of OUTPUT_TYPE_NML for WW3 (multi-grid).

    The ALLTYPE section applies output type parameters uniformly to all grids in multi-grid runs.
    """

    field: Optional[OutputTypeField] = Field(
        default=None, description="Field output parameters applied to all grids in multi-grid runs"
    )
    point: Optional[OutputTypePoint] = Field(
        default=None, description="Point output parameters applied to all grids in multi-grid runs"
    )
    track: Optional[OutputTypeTrack] = Field(
        default=None, description="Track output parameters applied to all grids in multi-grid runs"
    )
    partition: Optional[OutputTypePartition] = Field(
        default=None, description="Partition output parameters applied to all grids in multi-grid runs"
    )


class IType(NamelistBaseModel):
    """ITYPE(I) section of OUTPUT_TYPE_NML for WW3 (multi-grid).

    The ITYPE(I) section applies output type parameters to a specific grid I in multi-grid runs.
    """

    field: Optional[OutputTypeField] = Field(
        default=None, description="Field output parameters for specific grid I in multi-grid runs"
    )
    point: Optional[OutputTypePoint] = Field(
        default=None, description="Point output parameters for specific grid I in multi-grid runs"
    )
    track: Optional[OutputTypeTrack] = Field(
        default=None, description="Track output parameters for specific grid I in multi-grid runs"
    )
    partition: Optional[OutputTypePartition] = Field(
        default=None, description="Partition output parameters for specific grid I in multi-grid runs"
    )
