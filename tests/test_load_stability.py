# tests/test_load_stability.py

"""
TS_04_Load_Stability

Simulating 3x peak production load (images/sec) to check for
stability and performance.
"""

from __future__ import annotations

import os

import pytest

from compass_perf.metrics import PerfMetrics

MAX_ERROR_RATE = float(os.getenv("MAX_ERROR_RATE", "0.02"))
MAX_P95_LATENCY_MS = float(os.getenv("MAX_P95_LATENCY_MS", "2000"))


@pytest.mark.load
def test_load_stability_3x_peak(
    dicom_sender,
    dicom_datasets,
    metrics: PerfMetrics,
    perf_config,
):
    """
    Drives approximate 3x-peak load for a configurable time window.
    """
    duration = perf_config.load_profile.test_duration_seconds

    total_sent = dicom_sender.load_test_for_duration(
        datasets=dicom_datasets,
        metrics=metrics,
        duration_seconds=duration,
        concurrency=perf_config.load_profile.concurrency,
        rate_limit_images_per_second=None,
    )

    snapshot = metrics.snapshot()

    assert total_sent > 0, "No messages were sent during load test"
    assert metrics.total == total_sent, "Mismatch total_sent vs metrics.total"

    assert (
        metrics.error_rate <= MAX_ERROR_RATE
    ), f"Error rate too high: {metrics.error_rate:.3f} > {MAX_ERROR_RATE:.3f}"

    p95 = metrics.p95_latency_ms
    assert (
        p95 is not None and p95 <= MAX_P95_LATENCY_MS
    ), f"p95 latency too high: {p95} ms > {MAX_P95_LATENCY_MS} ms"

    print("Load stability snapshot:", snapshot)
