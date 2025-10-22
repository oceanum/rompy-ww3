from rompy.core.data import DataBlob
from pydantic import Field
from typing import Literal


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
