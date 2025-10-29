from rompy.core.data import DataBlob, DataGrid
from rompy.core.boundary import BoundaryWaveStation
from pydantic import Field
from typing import Literal, Optional
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
