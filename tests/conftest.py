# tests/conftest.py

"""
Global pytest fixtures for testing.
Works with flat project structure - compass_perf modules in root directory.
"""

import os
from pathlib import Path
from typing import List

import pytest
from dotenv import load_dotenv

# Import from root-level modules (compass_perf contents moved to root)
from config import PerfConfig
from data_loader import find_dicom_files, load_dataset
from dicom_sender import DicomSender
from metrics import PerfMetrics

# Load .env file from project root
project_root = Path(__file__).resolve().parent.parent
dotenv_path = project_root / ".env"

if dotenv_path.exists():
    load_dotenv(dotenv_path)
else:
    print(f"WARNING: .env file not found at {dotenv_path}")


@pytest.fixture(scope="session")
def perf_config() -> PerfConfig:
    """Performance configuration from environment variables."""
    cfg = PerfConfig.from_env()
    return cfg


@pytest.fixture(scope="session")
def dicom_files(perf_config: PerfConfig) -> List[Path]:
    """List of DICOM files for testing."""
    return find_dicom_files(
        perf_config.dataset.dicom_root_dir,
        recursive=perf_config.dataset.recursive,
    )


@pytest.fixture(scope="session")
def dicom_datasets(dicom_files: List[Path]):
    """Loaded DICOM datasets."""
    return [load_dataset(p) for p in dicom_files]


@pytest.fixture
def metrics() -> PerfMetrics:
    """Metrics collector for tracking performance."""
    return PerfMetrics()


@pytest.fixture(scope="session")
def dicom_sender(perf_config: PerfConfig) -> DicomSender:
    """DICOM sender for C-STORE operations."""
    return DicomSender(
        endpoint=perf_config.endpoint,
        load_profile=perf_config.load_profile,
    )


# Legacy fixtures for backward compatibility
@pytest.fixture(scope="session")
def compass_config(perf_config):
    """Configuration for Compass server connection (legacy compatibility)."""
    return {
        'host': perf_config.endpoint.host,
        'port': perf_config.endpoint.port,
        'ae_title': perf_config.endpoint.remote_ae_title,
        'local_ae_title': perf_config.endpoint.local_ae_title
    }


@pytest.fixture
def send_dicom_func():
    """Returns the send_dicom function from the project (legacy compatibility)."""
    from dicomsourceeval_send_dicom_cstore import send_dicom
    return send_dicom
