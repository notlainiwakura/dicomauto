# tests/conftest.py

"""
Global pytest fixtures for performance testing.

This version automatically loads a .env file located in the project root.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

import pytest
from dotenv import load_dotenv

from compass_perf.config import PerfConfig
from compass_perf.data_loader import find_dicom_files, load_dataset
from compass_perf.dicom_sender import DicomSender
from compass_perf.metrics import PerfMetrics

project_root = Path(__file__).resolve().parent.parent
dotenv_path = project_root / ".env"

if dotenv_path.exists():
    load_dotenv(dotenv_path)
else:
    print(f"WARNING: .env file not found at {dotenv_path}")


@pytest.fixture(scope="session")
def perf_config() -> PerfConfig:
    cfg = PerfConfig.from_env()
    return cfg


@pytest.fixture(scope="session")
def dicom_files(perf_config: PerfConfig) -> List[Path]:
    return find_dicom_files(
        perf_config.dataset.dicom_root_dir,
        recursive=perf_config.dataset.recursive,
    )


@pytest.fixture(scope="session")
def dicom_datasets(dicom_files: List[Path]):
    return [load_dataset(p) for p in dicom_files]


@pytest.fixture
def metrics() -> PerfMetrics:
    return PerfMetrics()


@pytest.fixture(scope="session")
def dicom_sender(perf_config: PerfConfig) -> DicomSender:
    return DicomSender(
        endpoint=perf_config.endpoint,
        load_profile=perf_config.load_profile,
    )
