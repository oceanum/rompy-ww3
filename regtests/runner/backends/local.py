import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Optional
import logging

from .base import Backend
from ..core.test import TestCase
from ..core.result import TestResult, TestStatus


logger = logging.getLogger(__name__)


class LocalBackend(Backend):
    def __init__(
        self,
        ww3_dir: Optional[Path] = None,
        backend_config: Optional[Path] = None,
        stream_output: bool = False,
    ):
        self.ww3_dir = ww3_dir
        # Use absolute path to backend config to ensure it works from any working directory
        self.backend_config = (
            backend_config
            or Path(__file__).parent.parent.parent / "backends" / "local_backend.yml"
        )
        self.stream_output = stream_output

    def execute(self, test: TestCase, workdir: Path) -> TestResult:
        logger.info(f"Executing {test.name} via local backend")

        start_time = time.time()

        try:
            # Get the regtests directory (parent of test directory)
            regtests_dir = test.config_path.parent.parent

            if self.stream_output:
                # Stream output in real-time
                return self._execute_streaming(test, regtests_dir, start_time)
            else:
                # Capture output and return at end
                return self._execute_buffered(test, regtests_dir, start_time)

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

    def _execute_buffered(
        self, test: TestCase, regtests_dir: Path, start_time: float
    ) -> TestResult:
        """Execute with buffered output (default behavior)."""
        result = subprocess.run(
            [
                "rompy",
                "run",
                str(test.config_path.absolute()),
                "--backend-config",
                str(self.backend_config.absolute()),
            ],
            cwd=regtests_dir,
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

    def _execute_streaming(
        self, test: TestCase, regtests_dir: Path, start_time: float
    ) -> TestResult:
        """Execute with streaming output (real-time)."""
        process = subprocess.Popen(
            [
                "rompy",
                "run",
                str(test.config_path.absolute()),
                "--backend-config",
                str(self.backend_config.absolute()),
            ],
            cwd=regtests_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
        )

        logs = []

        # Stream stdout in real-time
        if process.stdout:
            for line in process.stdout:
                line = line.rstrip()
                logs.append(line)
                print(line, flush=True)  # Stream to console

        # Wait for process to complete
        process.wait()
        execution_time = time.time() - start_time

        # Capture any remaining stderr
        stderr_output = ""
        if process.stderr:
            stderr_output = process.stderr.read()
            if stderr_output:
                print(stderr_output, file=sys.stderr, flush=True)
                logs.append(stderr_output)

        if process.returncode == 0:
            status = TestStatus.SUCCESS
            error_message = None
        else:
            status = TestStatus.FAILURE
            error_message = f"Exit code {process.returncode}"

        return TestResult(
            test_name=test.name,
            status=status,
            execution_time=execution_time,
            logs="\n".join(logs),
            error_message=error_message,
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
