#!/usr/bin/env python3
"""
Diagnostic script to check if the project structure is correct for running tests.
Run this from the project root directory.
"""

import sys
from pathlib import Path

print("="*60)
print("DICOM AUTO - PROJECT STRUCTURE DIAGNOSTIC")
print("="*60)

# Get project root
script_dir = Path(__file__).parent.absolute()
print(f"\n1. Current directory: {script_dir}")
print(f"   Python executable: {sys.executable}")
print(f"   Python version: {sys.version.split()[0]}")

# Check for required modules in root
print("\n2. Checking for required modules in project root:")
required_files = [
    "config.py",
    "data_loader.py", 
    "dicom_sender.py",
    "metrics.py",
    "dcmutl.py",
    "dicomsourceeval_send_dicom_cstore.py"
]

all_found = True
for filename in required_files:
    filepath = script_dir / filename
    exists = filepath.exists()
    status = "[OK]" if exists else "[MISSING]"
    print(f"   {status} {filename}")
    if not exists:
        all_found = False

# Check tests directory
print("\n3. Checking tests directory:")
tests_dir = script_dir / "tests"
if tests_dir.exists():
    print(f"   [OK] tests/ directory exists")
    
    test_files = ["conftest.py", "test_anonymize_and_send.py", "test_load_stability.py", "test_routing_throughput.py"]
    for filename in test_files:
        filepath = tests_dir / filename
        exists = filepath.exists()
        status = "[OK]" if exists else "[MISSING]"
        print(f"   {status} tests/{filename}")
else:
    print(f"   [MISSING] tests/ directory")
    all_found = False

# Check if modules can be imported
print("\n4. Testing module imports:")
sys.path.insert(0, str(script_dir))

import_tests = [
    ("config", "PerfConfig"),
    ("metrics", "PerfMetrics"),
    ("dicom_sender", "DicomSender"),
    ("data_loader", "find_dicom_files"),
    ("dcmutl", "get_dcm_files"),
]

for module_name, class_name in import_tests:
    try:
        module = __import__(module_name)
        if hasattr(module, class_name):
            print(f"   [OK] from {module_name} import {class_name}")
        else:
            print(f"   [ERROR] Module '{module_name}' exists but '{class_name}' not found")
            all_found = False
    except ImportError as e:
        print(f"   [ERROR] Cannot import {module_name}: {e}")
        all_found = False

# Check Python path
print("\n5. Python sys.path (first 5 entries):")
for i, path in enumerate(sys.path[:5], 1):
    print(f"   {i}. {path}")

# Final verdict
print("\n" + "="*60)
if all_found:
    print("✓ PROJECT STRUCTURE IS CORRECT")
    print("\nYou can run tests with:")
    print("  python3 -m pytest tests/ -v")
else:
    print("✗ PROJECT STRUCTURE HAS ISSUES")
    print("\nTO FIX:")
    print("1. Make sure you're in the project root directory")
    print("2. Pull latest changes: git pull origin main")
    print("3. Verify all files listed above exist")
print("="*60)

