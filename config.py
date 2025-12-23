# compass_perf/config.py

"""
Central configuration for Compass performance/load tests.

Values may be overridden with environment variables so that
the same code can be reused across environments.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def _env_str(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name)
    return value if value is not None else default


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass
class DicomEndpointConfig:
    """Configuration for a single DICOM destination (Compass listener)."""

    host: str
    port: int
    remote_ae_title: str
    local_ae_title: str = "PERF_SENDER"

    @classmethod
    def from_env(cls) -> "DicomEndpointConfig":
        return cls(
            host=_env_str("COMPASS_HOST", "127.0.0.1"),
            port=_env_int("COMPASS_PORT", 11112),
            remote_ae_title=_env_str("COMPASS_AE_TITLE", "COMPASS"),
            local_ae_title=_env_str("LOCAL_AE_TITLE", "PERF_SENDER") or "PERF_SENDER",
        )


@dataclass
class LoadProfileConfig:
    """High-level load profile settings."""

    peak_images_per_second: int
    load_multiplier: float
    test_duration_seconds: int
    concurrency: int

    @classmethod
    def from_env(cls) -> "LoadProfileConfig":
        return cls(
            peak_images_per_second=_env_int("PEAK_IMAGES_PER_SECOND", 50),
            load_multiplier=float(os.getenv("LOAD_MULTIPLIER", "3.0")),
            test_duration_seconds=_env_int("TEST_DURATION_SECONDS", 300),
            concurrency=_env_int("LOAD_CONCURRENCY", 8),
        )


@dataclass
class DatasetConfig:
    """Location of DICOM data on disk for replay."""

    dicom_root_dir: Path
    recursive: bool = True

    @classmethod
    def from_env(cls) -> "DatasetConfig":
        dicom_root = _env_str("DICOM_ROOT_DIR", "./dicom_samples")
        return cls(
            dicom_root_dir=Path(dicom_root).resolve(),
            recursive=True,
        )


@dataclass
class PerfConfig:
    """Top-level configuration object for perf tests."""

    endpoint: DicomEndpointConfig
    load_profile: LoadProfileConfig
    dataset: DatasetConfig

    @classmethod
    def from_env(cls) -> "PerfConfig":
        return cls(
            endpoint=DicomEndpointConfig.from_env(),
            load_profile=LoadProfileConfig.from_env(),
            dataset=DatasetConfig.from_env(),
        )
