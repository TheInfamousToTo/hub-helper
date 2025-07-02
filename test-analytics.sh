#!/bin/bash

echo "Testing Hub Helper Analytics API..."
echo

# Get the container IP or use localhost
if [ -z "$1" ]; then
    HOST="localhost:5000"
else
    HOST="$1"
fi

echo "Testing host: $HOST"
echo

# Test health endpoint
echo "1. Testing health endpoint..."
curl -s "http://$HOST/health" | python3 -m json.tool
echo

# Test analytics endpoint
echo "2. Testing analytics endpoint..."
curl -s "http://$HOST/analytics/counters" | python3 -m json.tool
echo

# Test external analytics API directly
echo "3. Testing external analytics API directly..."
curl -s "https://hub-backend.satrawi.cc/analytics/hub-helper" | python3 -m json.tool
echo

echo "Test completed!"
