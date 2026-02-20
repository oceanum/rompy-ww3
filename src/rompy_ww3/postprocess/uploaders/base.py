"""Base uploader interface for WW3 postprocessor."""

from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import dataclass
from typing import Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class UploadResult:
    """Result of an upload operation.

    Attributes:
        success: Whether the upload succeeded
        message: Status message (error details if failed)
        bytes_uploaded: Number of bytes uploaded (0 if failed)
    """

    success: bool
    message: str
    bytes_uploaded: int = 0


class BaseUploader(ABC):
    """Abstract base class for file uploaders.

    All uploader implementations must inherit from this class and implement
    the upload() method. This ensures consistent interface across all upload
    destinations (filesystem, cloud, HTTP, Oceanum).
    """

    @abstractmethod
    def upload(self, file_path: Path, destination: Any) -> UploadResult:
        """Upload a file to the specified destination.

        Args:
            file_path: Path to the file to upload
            destination: Destination configuration object

        Returns:
            UploadResult with success status, message, and bytes uploaded

        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError("Subclasses must implement upload()")

    def log_upload(
        self, file_path: Path, destination: Any, result: UploadResult
    ) -> None:
        """Log upload result.

        Args:
            file_path: Path to the uploaded file
            destination: Destination configuration
            result: Upload result to log
        """
        if result.success:
            logger.info(
                f"Uploaded {file_path.name} to {destination.type} "
                f"({result.bytes_uploaded} bytes): {result.message}"
            )
        else:
            logger.error(
                f"Failed to upload {file_path.name} to {destination.type}: "
                f"{result.message}"
            )
