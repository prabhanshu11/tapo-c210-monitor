# Ring Buffer Video Service

Gaming-style "save last N seconds" feature for RTSP camera streams.

## Features

- Continuous RTSP recording to circular buffer
- Configurable buffer limits (time OR size - whichever is smaller)
- HTTP API to save buffer or extract frames
- Automatic cleanup of old segments

## Usage

```bash
# Build
cd ringbuffer
go build -o ringbuffer

# Run (with camera credentials from .env)
source ../.env
./ringbuffer -rtsp "rtsp://${TAPO_USERNAME}:${TAPO_PASSWORD}@${TAPO_HOST}/stream1"

# Or with options
./ringbuffer \
  -rtsp "rtsp://user:pass@192.168.29.183/stream1" \
  -buffer-dir /tmp/ringbuffer/segments \
  -segment-sec 5 \
  -max-buffer-min 30 \
  -max-buffer-mb 500 \
  -resolution 1280x720 \
  -port 8085
```

## API

### GET /status
Returns buffer status:
```json
{
  "running": true,
  "segment_count": 42,
  "total_size_mb": 156.3,
  "buffer_seconds": 210,
  "oldest_segment": "2026-01-11T14:30:00Z",
  "newest_segment": "2026-01-11T14:33:30Z"
}
```

### POST /save?seconds=30&size_mb=50
Save buffer to file. Uses whichever limit is hit first.
- `seconds` - Maximum duration to save (default: 30)
- `size_mb` - Maximum size in MB (optional)
- `output` - Output file path (optional, auto-generated if not specified)

```json
{
  "saved_path": "/tmp/ringbuffer/saved/recording_20260111_143052.mp4"
}
```

### GET /frames?seconds_ago=0,5,10
Extract frames at specific times.
- `seconds_ago` - Comma-separated list of seconds ago to extract (default: 0,5,10)
- `output_dir` - Directory to save frames (optional)

```json
{
  "frames": [
    "/tmp/ringbuffer/frames/frame_0_0.0s_ago.jpg",
    "/tmp/ringbuffer/frames/frame_1_5.0s_ago.jpg",
    "/tmp/ringbuffer/frames/frame_2_10.0s_ago.jpg"
  ]
}
```

## Architecture

```
RTSP Stream → ffmpeg (5s segments) → Ring Buffer (manages files) → API
                                           ↓
                              Cleanup (enforces time/size limits)
```

## Dependencies

- ffmpeg (for RTSP recording and frame extraction)
- Go 1.21+
