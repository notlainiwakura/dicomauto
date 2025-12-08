# compass_perf/__init__.py

"""
Performance / Load testing helpers for Laurel Bridge Compass.

This package is focused on non-functional requirements from the
'UltraRAD to Compass Routing Migration' test plan, specifically:

- TS_04_Load_Stability (3x peak for extended duration)
- Throughput / latency measurement
- Error rate monitoring under load
"""

__all__ = [
    "config",
    "data_loader",
    "dicom_sender",
    "metrics",
]
