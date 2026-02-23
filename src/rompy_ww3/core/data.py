from rompy.core.data import DataBlob, DataGrid
from rompy.core.boundary import BoundaryWaveStation
from pydantic import Field
from typing import Literal, Optional, Union
from pathlib import Path
from rompy.core.grid import RegularGrid
from rompy.core.time import TimeRange


class WW3DataBlob(DataBlob):
    """A data blob for WW3 model data."""

    model_type: Literal["data_blob", "data_link"] = Field(
        default="data_blob",
        description="Model type discriminator",
    )

    def get(self, *args, **kwargs):
        """Get the data blob.

        This method should be implemented to retrieve the data blob.
        """
        return super().get(*args, **kwargs).name


class WW3RestartBlob(DataBlob):
    """A data blob for WW3 restart files with datetime pattern support.

    The source URI can include a {start_time} placeholder that will be substituted
    with the model run start time (format: YYYYMMDD_HHMMSS) when the file is fetched.

    Example:
        WW3RestartBlob(source="s3://bucket/ww3/{start_time}_restart.ww3")
    """

    model_type: Literal["restart_blob"] = Field(
        default="restart_blob",
        description="Model type discriminator for WW3 restart files",
    )

    def get(
        self,
        destdir: Optional[Union[str, Path]] = None,
        time: Optional[TimeRange] = None,
        *args,
        **kwargs,
    ) -> Path:
        """Fetch the restart file, substituting datetime pattern with run start time.

        Args:
            destdir: Destination directory
            time: Runtime period (used to substitute datetime pattern in source)
            *args: Additional arguments passed to parent
            **kwargs: Additional keyword arguments passed to parent

        Returns:
            Path to the fetched file
        """
        import shutil

        source = str(self.source)

        if time is not None and time.start is not None:
            start_str = time.start.strftime("%Y%m%d_%H%M%S")
            source = source.replace("{start_time}", start_str)

        # Simple file copy using shutil
        source_path = Path(source)
        destdir = Path(destdir) if destdir else None
        if destdir is None:
            raise ValueError("destdir is required for fetching restart files")

        destdir.mkdir(parents=True, exist_ok=True)
        dest_path = destdir / source_path.name

        shutil.copy2(source_path, dest_path)

        return dest_path


class WW3DataGrid(DataGrid):
    """A data grid for WW3 model data."""

    model_type: Literal["data_grid", "data_link"] = Field(
        default="data_grid",
        description="Model type discriminator",
    )

    def get(self, *args, **kwargs):
        """Get the data grid.

        This method should be implemented to retrieve the data grid.
        """
        return super().get(*args, **kwargs).name


class WW3Boundary(BoundaryWaveStation):
    """A data grid for WW3 model data."""

    model_type: Literal["data_boundary", "data_link"] = Field(
        default="data_boundary",
        description="Model type discriminator",
    )
    id: str = Field(
        default="ww3_boundary", description="Unique identifier for the boundary model"
    )

    def get(
        self, destdir: str | Path, grid: RegularGrid, time: Optional[TimeRange] = None
    ) -> str:
        """Write the selected boundary data to a netcdf file.

        Parameters
        ----------
        destdir : str | Path
            Destination directory for the netcdf file.
        grid : RegularGrid
            Grid instance to use for selecting the boundary points.
        time: TimeRange, optional
            The times to filter the data to, only used if `self.crop_data` is True.

        Returns
        -------
        outfile : Path
            Path to the netcdf file.

        """
        if self.crop_data:
            if time is not None:
                self._filter_time(time)
            if grid is not None:
                self._filter_grid(grid)
        ds = self._sel_boundary(grid)
        outfile = Path(destdir) / f"{self.id}.nc"
        ds.spec.to_ww3(outfile)
        speclist = Path(destdir) / "spec.list"
        with open(speclist, "w") as f:
            f.write(f"{outfile.name}\n")
        return speclist.name
