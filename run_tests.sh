#!/bin/bash
# Script to run tests with coverage

echo "Running tests with coverage..."
echo "================================"

# Run pytest with coverage
pytest

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "================================"
    echo "✅ All tests passed!"
    echo ""
    echo "Coverage report generated:"
    echo "  - Terminal: See above"
    echo "  - HTML: htmlcov/index.html"
    echo ""
    echo "To view HTML coverage report:"
    echo "  open htmlcov/index.html"
else
    echo ""
    echo "================================"
    echo "❌ Some tests failed. Please review the output above."
    exit 1
fi
