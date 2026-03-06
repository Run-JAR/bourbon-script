#!/usr/bin/env python3
# run_tests.py – Automated test runner for BourbonScript

import subprocess
import sys
import os

TESTS = [
    ("test_hello.bon",       "Hello World",          ["Hello, World!"]),
    ("test_arithmetic.bon",  "Arithmetic",            ["15", "50", "5", "2", "1", "30"]),
    ("test_loop.bon",        "While Loop",            ["0", "1", "2", "3", "4", "99"]),
    ("test_functions.bon",   "Functions + Recursion", ["7", "10", "720", "1", "0"]),
    ("test_fibonacci.bon",   "Fibonacci Sequence",    ["0", "1", "1", "2", "3", "5", "8", "13", "21", "34"]),
]

PASS = "✓"
FAIL = "✗"
SKIP = "⚠"

def run_test(filename, expected_lines):
    path = os.path.join("tests", filename)
    result = subprocess.run(
        [sys.executable, "bourbon.py", path],
        capture_output=True, text=True
    )
    output = result.stdout.strip().split('\n')
    # Filter out the banner and compile header lines
    actual = [l.strip() for l in output if l.strip() and not l.startswith('╔') 
              and not l.startswith('║') and not l.startswith('╚')
              and not l.strip().startswith('Compiling:')
              and not l.strip().startswith('  Compiling:')]
    
    if actual == expected_lines:
        return True, actual
    return False, actual

def main():
    print("╔══════════════════════════════════════╗")
    print("║   🍪  BourbonScript Test Runner      ║")
    print("╚══════════════════════════════════════╝\n")

    passed = 0
    failed = 0

    for filename, description, expected in TESTS:
        ok, actual = run_test(filename, expected)
        status = PASS if ok else FAIL
        color_start = "\033[92m" if ok else "\033[91m"
        color_end = "\033[0m"
        print(f"  {color_start}{status}{color_end} [{description}]")
        if not ok:
            print(f"      Expected: {expected}")
            print(f"      Got:      {actual}")
        if ok:
            passed += 1
        else:
            failed += 1

    print(f"\n  Results: {passed}/{passed+failed} tests passed")
    if failed == 0:
        print("  🍪 All tests passed! Dunked and delicious!\n")
    else:
        print(f"  ⚠️  {failed} test(s) failed\n")
    
    sys.exit(0 if failed == 0 else 1)

if __name__ == '__main__':
    main()
