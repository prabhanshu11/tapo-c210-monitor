#!/bin/bash
# Discover Tapo camera IP by scanning for RTSP port 554
# Usage: ./discover_camera.sh [subnet]
# Example: ./discover_camera.sh 192.168.29

SUBNET="${1:-192.168.29}"
RTSP_PORT=554
TIMEOUT=0.5

echo "Scanning $SUBNET.0/24 for Tapo camera (port $RTSP_PORT)..."

for ip in $(seq 1 254); do
    FULL_IP="$SUBNET.$ip"
    if timeout $TIMEOUT bash -c "echo >/dev/tcp/$FULL_IP/$RTSP_PORT" 2>/dev/null; then
        echo "$FULL_IP"
        exit 0
    fi
done

echo "No camera found on $SUBNET.0/24" >&2
exit 1
