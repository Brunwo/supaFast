#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Ensure all previous Python processes are killed
killall python3 || true

echo "Starting NEW JWT (JWKS) authentication tests..."

# --- IMPORTANT: Manual Configuration Required ---
# Before running this script, please ensure the following:
# 1. In src/template/.env, set: SUPABASE_USE_LEGACY_JWT=False
# 2. In src/template/.env, set: SUPABASE_URL="https://your-supabase-url.supabase.co"
# 3. In src/template/.env, set: SUPABASE_ANON_KEY="your-supabase-anon-key"
# 4. Ensure the FastAPI server is running with these settings (e.g., via ./launch.sh in a separate terminal).
# ------------------------------------------------

# Check for jq installation
if ! command -v jq &> /dev/null
then
    echo "jq could not be found. Please install it (e.g., sudo apt-get install jq or brew install jq)."
    exit 1
fi

# Ensure the server is running
if ! pgrep -f "src/template/main.py" > /dev/null; then
    echo "Server not running. Starting it..."
    SERVER_PID=$(./launch.sh)
    sleep 2 # Give it a moment to start up
fi

trap "kill $SERVER_PID || true" EXIT # Ensure server is killed on exit

# Wait for the server to be ready
echo "Waiting for FastAPI server to be ready..."
MAX_RETRIES=10
RETRY_INTERVAL=2
for i in $(seq 1 $MAX_RETRIES);
do
    if http --ignore-stdin --check-status GET http://127.0.0.1:8000/health &> /dev/null; then
        echo "Server is ready."
        break
    else
        echo "Attempt $i/$MAX_RETRIES: Server not ready yet. Waiting $RETRY_INTERVAL seconds..."
        sleep $RETRY_INTERVAL
    fi
    if [ $i -eq $MAX_RETRIES ]; then
        echo "Server did not become ready within the expected time. Exiting."
        exit 1
    fi
done

# Generate a valid JWT using the Node.js script
echo "Generating a valid JWT from Supabase..."
(cd supabase_tests && npm run get-jwt)
VALID_TOKEN=$(cat supabase_tests/jwt.token)

echo "Running tests..."

# Test 1: Accessing /protected with a valid token
echo "Test 1: Accessing /protected with a valid token..."
if http --ignore-stdin --check-status GET http://127.0.0.1:8000/protected "Authorization: Bearer $VALID_TOKEN" &> /dev/null; then
    response_body=$(http --ignore-stdin --print=b GET http://127.0.0.1:8000/protected "Authorization: Bearer $VALID_TOKEN")
    if [[ "$response_body" == *"user_id"* ]]; then
        echo "Test 1 PASSED"
    else
        echo "Test 1 FAILED: Missing user_id in response body."
        echo "Response: $response_body"
        exit 1
    fi
else
    echo "Test 1 FAILED: Non-2xx status code."
    exit 1
fi

# Test 2: Accessing /not_anonymous with a valid token (assuming it's not an anonymous user)
echo "Test 2: Accessing /not_anonymous with a valid token..."
if http --ignore-stdin --check-status GET http://127.0.0.1:8000/not_anonymous "Authorization: Bearer $VALID_TOKEN" &> /dev/null; then
    response_body=$(http --ignore-stdin --print=b GET http://127.0.0.1:8000/not_anonymous "Authorization: Bearer $VALID_TOKEN")
    if [[ "$response_body" == *"This is a protected endpoint"* ]]; then
        echo "Test 2 PASSED"
    else
        echo "Test 2 FAILED: Missing \"This is a protected endpoint\" in response body."
        echo "Response: $response_body"
        exit 1
    fi
else
    echo "Test 2 FAILED: Non-2xx status code."
    exit 1
fi

# Cleanup: Stop the server
echo "Cleaning up..."
pkill -f "src/template/main.py"

echo "NEW JWT (JWKS) authentication tests finished successfully."