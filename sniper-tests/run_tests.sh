#!/bin/bash

# Sniper Trading Platform - Test Runner Script
# This script runs the complete test suite with various options

set -e

echo "🧪 Sniper Trading Platform - Test Suite"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Parse command line arguments
TEST_TYPE=${1:-all}
COVERAGE=${2:-no}

echo -e "${BLUE}Test Type: $TEST_TYPE${NC}"
echo ""

case $TEST_TYPE in
    unit)
        echo -e "${GREEN}Running Unit Tests...${NC}"
        if [ "$COVERAGE" = "coverage" ]; then
            pytest unit/ -v --cov=app --cov-report=term --cov-report=html
        else
            pytest unit/ -v
        fi
        ;;
    
    integration)
        echo -e "${GREEN}Running Integration Tests...${NC}"
        if [ "$COVERAGE" = "coverage" ]; then
            pytest integration/ -v --cov=app --cov-report=term --cov-report=html
        else
            pytest integration/ -v
        fi
        ;;
    
    performance)
        echo -e "${GREEN}Running Performance Tests...${NC}"
        pytest performance/ -v -s
        ;;
    
    system)
        echo -e "${GREEN}Running System Tests...${NC}"
        pytest system/ -v -s
        ;;
    
    quick)
        echo -e "${GREEN}Running Quick Test Suite (Unit + Integration)...${NC}"
        pytest unit/ integration/ -v
        ;;
    
    all)
        echo -e "${GREEN}Running Complete Test Suite...${NC}"
        if [ "$COVERAGE" = "coverage" ]; then
            pytest -v --cov=app --cov-report=term --cov-report=html --html=report.html --self-contained-html
        else
            pytest -v --html=report.html --self-contained-html
        fi
        ;;
    
    failed)
        echo -e "${YELLOW}Re-running Failed Tests...${NC}"
        pytest --lf -v
        ;;
    
    *)
        echo "Usage: ./run_tests.sh [test_type] [coverage]"
        echo ""
        echo "Test Types:"
        echo "  unit         - Run unit tests only"
        echo "  integration  - Run integration tests only"
        echo "  performance  - Run performance tests only"
        echo "  system       - Run system tests only"
        echo "  quick        - Run unit + integration tests"
        echo "  all          - Run complete test suite (default)"
        echo "  failed       - Re-run only failed tests"
        echo ""
        echo "Coverage:"
        echo "  coverage     - Generate coverage report"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh unit"
        echo "  ./run_tests.sh all coverage"
        echo "  ./run_tests.sh performance"
        exit 1
        ;;
esac

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Tests completed successfully!${NC}"
    
    if [ "$COVERAGE" = "coverage" ]; then
        echo ""
        echo -e "${BLUE}📊 Coverage report generated:${NC}"
        echo "   HTML: htmlcov/index.html"
    fi
    
    if [ "$TEST_TYPE" = "all" ]; then
        echo ""
        echo -e "${BLUE}📄 Test report generated:${NC}"
        echo "   HTML: report.html"
    fi
else
    echo -e "${YELLOW}⚠️  Some tests failed. Exit code: $EXIT_CODE${NC}"
fi

echo ""
exit $EXIT_CODE
