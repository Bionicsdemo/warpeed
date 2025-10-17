#!/bin/bash
# Master test runner for lightsail optimization project

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║          LIGHTSAIL OPTIMIZATION - TEST SUITE RUNNER             ║"
echo "║                                                                  ║"
echo "║  Running comprehensive validation tests                          ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Track test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Change to project directory
cd "$(dirname "$0")"

# Test 1: Physics Validation
echo "Running Test Suite 1: Physics Validation..."
python3 tests/test_physics_validation.py
if [ $? -eq 0 ]; then
    ((PASSED_TESTS++))
    echo "✓ Physics validation PASSED"
else
    ((FAILED_TESTS++))
    echo "✗ Physics validation FAILED"
fi
((TOTAL_TESTS++))
echo ""

# Test 2: Data Validation
echo "Running Test Suite 2: Data Validation..."
python3 tests/test_data_validation.py
if [ $? -eq 0 ]; then
    ((PASSED_TESTS++))
    echo "✓ Data validation PASSED"
else
    ((FAILED_TESTS++))
    echo "✗ Data validation FAILED"
fi
((TOTAL_TESTS++))
echo ""

# Summary
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                       TEST RESULTS SUMMARY                       ║"
echo "╠══════════════════════════════════════════════════════════════════╣"
echo "║  Total Test Suites: $TOTAL_TESTS                                          ║"
echo "║  Passed: $PASSED_TESTS                                                     ║"
echo "║  Failed: $FAILED_TESTS                                                     ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo "✓✓✓ ALL TESTS PASSED ✓✓✓"
    echo "The lightsail optimization project is validated and ready!"
    exit 0
else
    echo "✗✗✗ SOME TESTS FAILED ✗✗✗"
    echo "Please review the test output above."
    exit 1
fi
