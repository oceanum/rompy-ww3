"""Configuration models for WW3 upload postprocessor."""

from pathlib import Path
from typing import List, Optional, Dict, Literal, Union
from pydantic import BaseModel, Field


class FileSelection(BaseModel):
    """File selection criteria for upload postprocessor.

    Specifies which WW3 output files should be uploaded based on output types
    and optional glob patterns.
    """

    output_types: List[str] = Field(
        description=(
            "WW3 output types to upload. Valid types: 'field', 'point', 'track', "
            "'partition', 'coupling', 'restart'"
        )
    )
    patterns: Optional[List[str]] = Field(
        default=None, description="Optional glob patterns for additional file filtering"
    )


class RetryConfig(BaseModel):
    """Retry configuration for upload operations.

    Defines retry behavior with exponential backoff for transient failures.
    """

    max_retries: int = Field(
        default=3,
        ge=0,
        description="Maximum number of retry attempts for failed uploads",
    )
    backoff_factor: float = Field(
        default=2.0,
        gt=0.0,
        description="Exponential backoff factor (delay = backoff_factor ** attempt)",
    )


class FilesystemDestination(BaseModel):
    """Filesystem upload destination.

    Uploads files to a local or network-mounted filesystem path.
    """

    type: Literal["filesystem"] = "filesystem"
    path: Path = Field(description="Destination directory path for uploaded files")
    create_dirs: bool = Field(
        default=True, description="Create destination directories if they don't exist"
    )


class CloudDestination(BaseModel):
    """Cloud storage destination via CloudPath/fsspec.

    Supports S3, GCS, and Azure Blob Storage through unified CloudPath interface.
    Credentials are provided via environment variables:
    - S3: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
    - GCS: GOOGLE_APPLICATION_CREDENTIALS
    - Azure: AZURE_STORAGE_CONNECTION_STRING
    """

    type: Literal["cloud"] = "cloud"
    uri: str = Field(
        description=(
            "Cloud storage URI. Supported formats: "
            "s3://bucket/prefix/, gs://bucket/prefix/, az://container/prefix/"
        )
    )
    endpoint_url: Optional[str] = Field(
        default=None,
        description="Custom endpoint URL for S3-compatible storage (e.g., MinIO)",
    )


class HTTPDestination(BaseModel):
    """HTTP upload destination.

    Uploads files via HTTP POST to a specified endpoint.
    """

    type: Literal["http"] = "http"
    url: str = Field(description="HTTP endpoint URL for file upload")
    headers: Dict[str, str] = Field(
        default_factory=dict,
        description="HTTP headers to include in upload request (e.g., auth tokens)",
    )
    timeout: int = Field(default=30, gt=0, description="Request timeout in seconds")


class OceanumDestination(BaseModel):
    """Oceanum storage destination.

    Uploads files to Oceanum Datamesh via oceanum-python library.
    Requires DATAMESH_TOKEN environment variable for authentication.
    """

    type: Literal["oceanum"] = "oceanum"
    catalog: str = Field(description="Oceanum catalog name for file upload")
    dataset: str = Field(description="Oceanum dataset name within the catalog")


# Union type for all destination types
Destination = Union[
    FilesystemDestination, CloudDestination, HTTPDestination, OceanumDestination
]


class UploadConfig(BaseModel):
    """Main configuration for WW3 upload postprocessor.

    Defines destinations, file selection criteria, retry behavior, and failure handling
    for uploading WW3 model output files.
    """

    destinations: List[Destination] = Field(
        description="List of upload destinations (filesystem, cloud, HTTP, Oceanum)"
    )
    file_selection: FileSelection = Field(
        description="File selection criteria (output types and patterns)"
    )
    retry: RetryConfig = Field(
        default_factory=RetryConfig,
        description="Retry configuration for upload failures",
    )
    failure_mode: Literal["strict", "lenient"] = Field(
        default="strict",
        description=(
            "Failure handling mode. "
            "'strict': upload failure causes postprocessor to fail. "
            "'lenient': upload failure logged as warning, processing continues"
        ),
    )
