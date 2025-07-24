#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Ensure all previous Python processes are killed
killall python3 || true

echo "Starting LEGACY authentication tests..."

# Ensure the server is running
if ! pgrep -f "src/template/main.py" > /dev/null; then
    echo "Server not running. Starting it..."
    SERVER_PID=$(./launch.sh)
    sleep 2 # Give it a moment to start up
fi

trap "kill $SERVER_PID || true" EXIT # Ensure server is killed on exit

# Temporarily enable dev mode for these tests (legacy behavior)
echo "Enabling dev mode for legacy tests..."
sed -i 's/DEV_MODE=false/DEV_MODE=true/' .env

# Temporarily enable legacy JWT verification
echo "Enabling legacy JWT verification..."
sed -i 's/SUPABASE_USE_LEGACY_JWT=False/SUPABASE_USE_LEGACY_JWT=True/' src/template/.env

# Restart server to apply .env changes
echo "Restarting server..."
pkill -f "src/template/main.py"
sleep 2 # Give it a moment to shut down
./launch.sh &
sleep 2 # Give it a moment to start up

# Generate tokens using legacy scripts
echo "Generating legacy JWT tokens..."
VALID_TOKEN=$(python3 legacy_create_jwt.py)
GUEST_TOKEN=$(python3 legacy_create_jwt_guest.py)

echo "Running tests..."

# Test 1: Valid token
echo "Test 1: Accessing /protected with a valid legacy token..."
response_valid=$(http --ignore-stdin --check-status GET http://127.0.0.1:8000/protected "Authorization: Bearer $VALID_TOKEN")
if [[ $(echo "$response_valid" | grep -c "user_id") -eq 1 ]]; then
    echo "Test 1 PASSED"
else
    echo "Test 1 FAILED"
    echo "Response: $response_valid"
    exit 1
fi

# Test 2: Insufficient role
echo "Test 2: Accessing /protected with a guest legacy token..."
# Capture full output (headers + body)
full_response=$(http --ignore-stdin GET http://127.0.0.1:8000/protected "Authorization: Bearer $GUEST_TOKEN" 2>&1 || true)

# Extract status code (e.g., "HTTP/1.1 403 Forbidden" -> "403")
response_status=$(echo "$full_response" | head -n 1 | grep -oP 'HTTP/1.\d \K\d{3}')

# Extract response body (assuming JSON starts with '{' and ends with '}')
response_body=$(echo "$full_response" | awk '/^{/,/}$/{print}')

# Use jq to check for the specific error message
error_message=$(echo "$response_body" | jq -r '.detail.message' || true)

echo "Debug - Test 2 Status: $response_status"
echo "Debug - Test 2 Body: $response_body"
echo "Debug - Test 2 Error Message: $error_message"

if [[ "$response_status" == "403" && "$error_message" == *"insufficient_permissions"* ]]; then
    echo "Test 2 PASSED"
else
    echo "Test 2 FAILED"
    echo "Status: $response_status"
    echo "Response Body: $response_body"
    echo "Error Message: $error_message"
    exit 1
fi

# Cleanup: Revert .env changes and stop the server
echo "Cleaning up..."
sed -i 's/DEV_MODE=true/DEV_MODE=false/' .env
sed -i 's/SUPABASE_USE_LEGACY_JWT=True/SUPABASE_USE_LEGACY_JWT=False/' src/template/.env
pkill -f "src/template/main.py"

echo "LEGACY authentication tests finished successfully."