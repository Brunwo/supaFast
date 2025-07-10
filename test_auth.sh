#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Starting authentication tests..."

# Ensure the server is running
if ! pgrep -f "src/template/main.py" > /dev/null; then
    echo "Server not running. Starting it..."
    ./launch.sh &
    sleep 2 # Give it a moment to start up
fi

# Temporarily disable dev mode for these tests
echo "Disabling dev mode..."
sed -i 's/DEV_MODE=true/DEV_MODE=false/' .env

# Restart server to apply .env changes
echo "Restarting server..."
pkill -f "src/template/main.py"
sleep 2 # Give it a moment to shut down
./launch.sh &
sleep 2 # Give it a moment to start up

# Generate tokens
echo "Generating JWT tokens..."
VALID_TOKEN=$(python3 create_jwt.py)
GUEST_TOKEN=$(python3 create_jwt_guest.py)

echo "Running tests..."

# Test 1: Valid token
echo "Test 1: Accessing /protected with a valid token..."
response_valid=$(http --ignore-stdin --check-status GET http://127.0.0.1:8000/protected "Authorization: Bearer $VALID_TOKEN")
if [[ $(echo "$response_valid" | grep -c "test-user") -eq 1 ]]; then
    echo "Test 1 PASSED"
else
    echo "Test 1 FAILED"
    echo "Response: $response_valid"
    exit 1
fi

# Test 2: Insufficient role
echo "Test 2: Accessing /protected with a guest token..."
response_guest=$(http --ignore-stdin --check-status --print=hHbs GET http://127.0.0.1:8000/protected "Authorization: Bearer $GUEST_TOKEN" || true)
if [[ $(echo "$response_guest" | grep -c "403 Forbidden") -eq 1 && $(echo "$response_guest" | grep -c "insufficient_permissions") -eq 1 ]]; then
    echo "Test 2 PASSED"
else
    echo "Test 2 FAILED"
    echo "Response: $response_guest"
    exit 1
fi

# Cleanup: Re-enable dev mode and stop the server
echo "Cleaning up..."
sed -i 's/DEV_MODE=false/DEV_MODE=true/' .env
pkill -f "src/template/main.py"

echo "Authentication tests finished successfully."
