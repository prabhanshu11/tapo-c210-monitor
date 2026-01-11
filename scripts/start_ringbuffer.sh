#!/bin/bash
# Start the ring buffer service for Tapo camera

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Load environment
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
fi

# Check required vars
if [ -z "$TAPO_HOST" ] || [ -z "$TAPO_USERNAME" ] || [ -z "$TAPO_PASSWORD" ]; then
    echo "ERROR: Missing environment variables"
    echo "Create .env file with:"
    echo "  TAPO_HOST=192.168.29.183"
    echo "  TAPO_USERNAME=your_username"
    echo "  TAPO_PASSWORD=your_password"
    exit 1
fi

# Build if needed
RINGBUFFER="$PROJECT_DIR/ringbuffer/ringbuffer"
if [ ! -f "$RINGBUFFER" ]; then
    echo "Building ring buffer..."
    cd "$PROJECT_DIR/ringbuffer"
    go build -o ringbuffer
fi

# Default parameters (can be overridden via command line)
BUFFER_MIN=${BUFFER_MIN:-30}
BUFFER_MB=${BUFFER_MB:-500}
SEGMENT_SEC=${SEGMENT_SEC:-5}
RESOLUTION=${RESOLUTION:-}
PORT=${PORT:-8085}

RTSP_URL="rtsp://${TAPO_USERNAME}:${TAPO_PASSWORD}@${TAPO_HOST}/stream1"

echo "Starting Ring Buffer Service"
echo "=============================="
echo "Camera: $TAPO_HOST"
echo "Buffer: ${BUFFER_MIN} min / ${BUFFER_MB} MB"
echo "Segment: ${SEGMENT_SEC}s"
echo "Port: $PORT"
echo ""

RESOLUTION_FLAG=""
if [ -n "$RESOLUTION" ]; then
    RESOLUTION_FLAG="-resolution $RESOLUTION"
fi

exec "$RINGBUFFER" \
    -rtsp "$RTSP_URL" \
    -max-buffer-min "$BUFFER_MIN" \
    -max-buffer-mb "$BUFFER_MB" \
    -segment-sec "$SEGMENT_SEC" \
    -port "$PORT" \
    $RESOLUTION_FLAG
