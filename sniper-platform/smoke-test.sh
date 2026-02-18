#!/bin/bash
set -e

echo "=== SMOKE TEST SUITE ==="
echo ""

# Test 1: Backend health
echo "✓ Testing backend health endpoint..."
curl -sf http://localhost:8000/health > /dev/null
echo "  ✓ Backend health OK"

# Test 2: Strategy API
echo "✓ Testing strategy API..."
curl -sf http://localhost:8000/api/v1/strategy/ > /dev/null
echo "  ✓ Strategy API OK"

# Test 3: Risk API
echo "✓ Testing risk metrics API..."
curl -sf http://localhost:8000/api/v1/risk/metrics > /dev/null
echo "  ✓ Risk metrics API OK"

# Test 4: Execution API
echo "✓ Testing execution API..."
curl -sf http://localhost:8000/api/v1/execution/orders > /dev/null
echo "  ✓ Execution API OK"

# Test 5: Quantum API
echo "✓ Testing quantum API..."
curl -sf http://localhost:8000/api/v1/quantum/status > /dev/null
echo "  ✓ Quantum API OK"

# Test 6: Frontend
echo "✓ Testing frontend..."
curl -sf http://localhost:3000 > /dev/null
echo "  ✓ Frontend OK"

echo ""
echo "=== ALL SMOKE TESTS PASSED ==="
