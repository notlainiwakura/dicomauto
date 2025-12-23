# tests/test_routing_throughput.py

"""
Throughput and routing performance tests.

These focus on:
- Hitting a target images/sec rate
- Checking Compass is reachable (C-ECHO) before the test
- Verifying error rate and latency bounds
"""

from __future__ import annotations

import os

import pytest

from metrics import PerfMetrics

MAX_ERROR_RATE = float(os.getenv("MAX_ERROR_RATE", "0.02"))
MAX_P95_LATENCY_MS = float(os.getenv("MAX_P95_LATENCY_MS_SHORT", "1500"))


@pytest.mark.load
@pytest.mark.parametrize("multiplier", [1.5, 2.0])
def test_routing_throughput_under_peak_plus(
    dicom_sender,
    dicom_datasets,
    metrics: PerfMetrics,
    perf_config,
    multiplier,
):
    """
    Push Compass to 150 percent and 200 percent of configured peak_images_per_second.
    """
    assert dicom_sender.ping(), "Compass did not respond to C-ECHO ping"

    target_peak = perf_config.load_profile.peak_images_per_second * multiplier
    duration = perf_config.load_profile.test_duration_seconds

    total_sent = dicom_sender.load_test_for_duration(
        datasets=dicom_datasets,
        metrics=metrics,
        duration_seconds=duration,
        concurrency=perf_config.load_profile.concurrency,
        rate_limit_images_per_second=target_peak,
    )

    snapshot = metrics.snapshot()
    actual_rate = metrics.throughput_per_second()

    assert total_sent > 0, "No messages were sent during throughput test"

    assert (
        actual_rate >= 0.95 * target_peak
    ), f"Effective throughput {actual_rate:.2f}/s is below 95 percent of target {target_peak:.2f}/s"

    assert (
        metrics.error_rate <= MAX_ERROR_RATE
    ), f"Error rate too high: {metrics.error_rate:.3f} > {MAX_ERROR_RATE:.3f}"

    p95 = metrics.p95_latency_ms
    assert (
        p95 is not None and p95 <= MAX_P95_LATENCY_MS
    ), f"p95 latency too high: {p95} ms > {MAX_P95_LATENCY_MS} ms"

    print("Throughput snapshot:", snapshot)

