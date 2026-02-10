import subprocess
import time
from pathlib import Path
from typing import Dict
import logging

from .base import Backend
from ..core.test import TestCase
from ..core.result import TestResult, TestStatus


logger = logging.getLogger(__name__)


class LocalBackend(Backend):
    def __init__(self, ww3_dir: Path = None):
        self.ww3_dir = ww3_dir

    def execute(self, test: TestCase, workdir: Path) -> TestResult:
        logger.info(f"Executing {test.name} via local backend")

        start_time = time.time()

        try:
            result = subprocess.run(
                ["rompy", "run", str(test.config_path)],
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=3600,
            )

            execution_time = time.time() - start_time

            if result.returncode == 0:
                status = TestStatus.SUCCESS
                error_message = None
            else:
                status = TestStatus.FAILURE
                error_message = f"Exit code {result.returncode}"

            return TestResult(
                test_name=test.name,
                status=status,
                execution_time=execution_time,
                logs=result.stdout + result.stderr,
                error_message=error_message,
            )

        except subprocess.TimeoutExpired:
            return TestResult(
                test_name=test.name,
                status=TestStatus.ERROR,
                execution_time=3600,
                error_message="Execution timed out after 1 hour",
            )
        except Exception as e:
            return TestResult(
                test_name=test.name,
                status=TestStatus.ERROR,
                execution_time=time.time() - start_time,
                error_message=str(e),
            )

    def validate_env(self) -> bool:
        try:
            result = subprocess.run(
                ["rompy", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_version_info(self) -> Dict[str, str]:
        info = {}

        try:
            result = subprocess.run(
                ["rompy", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                info["rompy"] = result.stdout.strip()
        except Exception:
            pass

        return info
