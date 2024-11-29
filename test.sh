#!/bin/bash

# Test script for logs service HTTP handlers

# Set up variables
BASE_URL="http://localhost:8080/api/1/service"
SERVICE_ID="123"
START_DATE="2023-05-01-00-00-00"
END_DATE="2023-05-02-00-00-00"

# Test POST /logs endpoint
echo "Testing POST /logs endpoint"
curl -X POST "${BASE_URL}/${SERVICE_ID}/logs" \
    -H "Content-Type: application/json" \
    -d '{
        "logs": [
            {
                "message": "Test log message",
                "level": "INFO",
                "date": "1682956800"
            }
        ]
    }'

echo -e "\n"

# Test GET /logs endpoint
echo "Testing GET /logs endpoint"
curl -X GET "${BASE_URL}/${SERVICE_ID}/logs/${START_DATE}/${END_DATE}"

echo -e "\n"

# Test POST /logs with invalid data
echo "Testing POST /logs with invalid data"
curl -X POST "${BASE_URL}/${SERVICE_ID}/logs" \
    -H "Content-Type: application/json" \
    -d '{
        "invalid": "data"
    }'

echo -e "\n"

# Test GET /logs with invalid date range
echo "Testing GET /logs with invalid date range"
curl -X GET "${BASE_URL}/${SERVICE_ID}/logs/invalid-start-date/invalid-end-date"

echo -e "\n"

# Test GET /logs with non-existent service ID
echo "Testing GET /logs with non-existent service ID"
curl -X GET "${BASE_URL}/999/logs/${START_DATE}/${END_DATE}"

echo -e "\n"

echo "Tests completed"
