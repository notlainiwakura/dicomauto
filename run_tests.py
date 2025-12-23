#!/usr/bin/env python3
"""
Simple test runner script for the Compass performance test suite.
This script runs pytest using the Python module syntax, which works
even when pytest isn't directly available as a command.

Usage:
    python3 run_tests.py              # Run all load tests
    python3 run_tests.py --quick      # Run with 10 second duration
    python3 run_tests.py --stability # Run only stability test
    python3 run_tests.py --throughput # Run only throughput test
"""

import sys
import subprocess
import os

def main():
    """Run pytest tests with appropriate arguments."""
    
    # Default pytest arguments
    pytest_args = ["-m", "load", "-vv"]
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg == "--quick":
            # Quick test with short duration
            os.environ["TEST_DURATION_SECONDS"] = "10"
            os.environ["LOAD_CONCURRENCY"] = "4"
            print("Running quick test (10 seconds)...")
            
        elif arg == "--stability":
            # Run only stability test
            pytest_args = ["tests/test_load_stability.py", "-vv"]
            print("Running load stability test...")
            
        elif arg == "--throughput":
            # Run only throughput test
            pytest_args = ["tests/test_routing_throughput.py", "-vv"]
            print("Running throughput test...")
            
        elif arg in ["-h", "--help"]:
            print(__doc__)
            sys.exit(0)
        else:
            print(f"Unknown argument: {arg}")
            print(__doc__)
            sys.exit(1)
    
    # Run pytest using Python module syntax
    cmd = [sys.executable, "-m", "pytest"] + pytest_args
    
    print(f"Running: {' '.join(cmd)}")
    print()
    
    # Execute pytest
    result = subprocess.run(cmd)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()

