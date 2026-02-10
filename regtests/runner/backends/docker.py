import time
from pathlib import Path
from typing import Dict, Optional
import logging

from .base import Backend
from ..core.test import TestCase
from ..core.result import TestResult, TestStatus


logger = logging.getLogger(__name__)


class DockerBackend(Backend):
    def __init__(self, image: str = "rompy/ww3:latest", docker_client=None):
        self.image = image
        self.docker_client = docker_client

    def execute(self, test: TestCase, workdir: Path) -> TestResult:
        logger.info(f"Executing {test.name} via Docker backend")

        start_time = time.time()

        return TestResult(
            test_name=test.name,
            status=TestStatus.SKIPPED,
            execution_time=time.time() - start_time,
            error_message="Docker backend not yet implemented",
        )

    def validate_env(self) -> bool:
        try:
            import docker

            client = docker.from_env()
            client.ping()
            return True
        except Exception:
            return False

    def get_version_info(self) -> Dict[str, str]:
        info = {}

        try:
            import docker

            client = docker.from_env()
            info["docker"] = client.version()["Version"]
            info["image"] = self.image
        except Exception:
            pass

        return info
