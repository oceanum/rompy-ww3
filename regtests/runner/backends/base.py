from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict
from ..core.test import TestCase
from ..core.result import TestResult


class Backend(ABC):
    @abstractmethod
    def execute(self, test: TestCase, workdir: Path) -> TestResult:
        pass

    @abstractmethod
    def validate_env(self) -> bool:
        pass

    @abstractmethod
    def get_version_info(self) -> Dict[str, str]:
        pass
