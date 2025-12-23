#!/usr/bin/env python3
"""
Test script to verify .env file is being loaded correctly.
Run from project root: python test_env.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Get project root
project_root = Path(__file__).parent.absolute()
dotenv_path = project_root / ".env"

print("="*60)
print("ENVIRONMENT VARIABLE TEST")
print("="*60)
print(f"Project root: {project_root}")
print(f".env file path: {dotenv_path}")
print(f".env file exists: {dotenv_path.exists()}")

if dotenv_path.exists():
    print(f"\n.env file contents:")
    with open(dotenv_path, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                print(f"  {line.strip()}")
else:
    print("\n[WARNING] .env file not found!")

print(f"\nLoading .env file...")
load_dotenv(dotenv_path)

print(f"\nDICOM_ROOT_DIR value:")
dicom_root = os.getenv('DICOM_ROOT_DIR', './dicom_samples')
print(f"  From env: {dicom_root}")
print(f"  Resolved path: {Path(dicom_root).resolve()}")
print(f"  Path exists: {Path(dicom_root).resolve().exists()}")

# Check other important variables
print(f"\nOther configuration:")
print(f"  COMPASS_HOST: {os.getenv('COMPASS_HOST', 'NOT SET')}")
print(f"  COMPASS_PORT: {os.getenv('COMPASS_PORT', 'NOT SET')}")
print(f"  TEST_DICOM_FILE: {os.getenv('TEST_DICOM_FILE', 'NOT SET')}")

print("="*60)

