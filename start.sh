#!/bin/sh
set -e

# Start the REST receiver in the background
cd /app/rest-receiver
echo "Starting HL7 REST Receiver..."
node server.js &
REST_PID=$!

# Wait for REST receiver to initialize
sleep 3
echo "REST Receiver started with PID: $REST_PID"

# Start the web interface
cd /app/web-interface
echo "Starting Web Interface..."
node server.js &
WEB_PID=$!

# Wait for Web Interface to initialize
sleep 2
echo "Web Interface started with PID: $WEB_PID"

# Check if the web interface is actually running
if ! kill -0 $WEB_PID 2>/dev/null; then
    echo "ERROR: Web Interface failed to start. Exiting..."
    kill $REST_PID
    exit 1
fi

# Generate initial sample HL7 messages
cd /app/hl7-sender
echo "Generating sample HL7 messages..."
/app/venv/bin/python generate_hl7.py --count 5 --output sample_messages.txt

echo "HL7 Integration system ready!"
echo "REST Receiver: http://localhost:3000"
echo "Web Interface: http://localhost:5000"

# Keep the container running and capture signals
trap "kill $REST_PID $WEB_PID; exit" SIGINT SIGTERM
wait $REST_PID $WEB_PID 