# tests/conftest.py

"""
Global pytest fixtures for testing.
Works with flat project structure (no compass_perf module).
"""

import os
from pathlib import Path
from typing import List

import pytest
from dotenv import load_dotenv

# Load .env file from project root
project_root = Path(__file__).resolve().parent.parent
dotenv_path = project_root / ".env"

if dotenv_path.exists():
    load_dotenv(dotenv_path)
else:
    print(f"WARNING: .env file not found at {dotenv_path}")


@pytest.fixture(scope="session")
def compass_config():
    """Configuration for Compass server connection."""
    return {
        'host': os.getenv('COMPASS_HOST', '129.176.169.25'),
        'port': int(os.getenv('COMPASS_PORT', '11112')),
        'ae_title': os.getenv('COMPASS_AE_TITLE', 'COMPASS'),
        'local_ae_title': os.getenv('LOCAL_AE_TITLE', 'TEST_SENDER')
    }


@pytest.fixture(scope="session")
def dicom_root_dir():
    """Root directory containing DICOM test files."""
    root = os.getenv('DICOM_ROOT_DIR', './dicom_samples')
    return Path(root).resolve()


@pytest.fixture(scope="session")
def dicom_files(dicom_root_dir):
    """List of DICOM files for testing."""
    from dcmutl import get_dcm_files
    
    files = get_dcm_files(str(dicom_root_dir))
    if not files:
        pytest.skip(f"No DICOM files found in {dicom_root_dir}")
    
    return [Path(f) for f in files]


@pytest.fixture
def send_dicom_func():
    """Returns the send_dicom function from the project."""
    from dicomsourceeval_send_dicom_cstore import send_dicom
    return send_dicom
