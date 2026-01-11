package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"sync"
	"syscall"
	"time"

	"github.com/gorilla/mux"
)

// Config holds the ring buffer configuration
type Config struct {
	RTSPUrl        string        // RTSP stream URL
	BufferDir      string        // Directory for segment files
	SegmentSeconds int           // Duration of each segment
	MaxBufferTime  time.Duration // Maximum buffer duration
	MaxBufferSize  int64         // Maximum buffer size in bytes
	Resolution     string        // Output resolution (e.g., "1280x720")
	Port           int           // HTTP API port
}

// Segment represents a recorded video segment
type Segment struct {
	Path      string
	StartTime time.Time
	Size      int64
}

// RingBuffer manages the circular buffer of video segments
type RingBuffer struct {
	config   Config
	segments []Segment
	mu       sync.RWMutex
	running  bool
	ffmpeg   *exec.Cmd
	stopCh   chan struct{}
}

// NewRingBuffer creates a new ring buffer
func NewRingBuffer(config Config) *RingBuffer {
	return &RingBuffer{
		config:   config,
		segments: make([]Segment, 0),
		stopCh:   make(chan struct{}),
	}
}

// Start begins recording to the ring buffer
func (rb *RingBuffer) Start() error {
	rb.mu.Lock()
	if rb.running {
		rb.mu.Unlock()
		return fmt.Errorf("already running")
	}
	rb.running = true
	rb.mu.Unlock()

	// Ensure buffer directory exists
	if err := os.MkdirAll(rb.config.BufferDir, 0755); err != nil {
		return fmt.Errorf("failed to create buffer dir: %w", err)
	}

	// Start ffmpeg in background
	go rb.runFFmpeg()

	// Start segment scanner
	go rb.scanSegments()

	// Start cleanup routine
	go rb.cleanup()

	return nil
}

// Stop stops the recording
func (rb *RingBuffer) Stop() {
	rb.mu.Lock()
	if !rb.running {
		rb.mu.Unlock()
		return
	}
	rb.running = false
	rb.mu.Unlock()

	close(rb.stopCh)

	if rb.ffmpeg != nil && rb.ffmpeg.Process != nil {
		rb.ffmpeg.Process.Signal(syscall.SIGTERM)
		rb.ffmpeg.Wait()
	}
}

// runFFmpeg starts ffmpeg to record RTSP stream into segments
func (rb *RingBuffer) runFFmpeg() {
	// Use sequential numbering - will be renamed to Unix timestamps by scanner
	segmentPattern := filepath.Join(rb.config.BufferDir, "segment_%05d.mp4")

	args := []string{
		"-rtsp_transport", "tcp",
		"-i", rb.config.RTSPUrl,
		"-c:v", "copy", // Copy video codec (no re-encoding)
		"-an",          // Drop audio (pcm_alaw not supported in mp4)
		"-f", "segment",
		"-segment_time", strconv.Itoa(rb.config.SegmentSeconds),
		"-segment_format", "mp4",
		"-reset_timestamps", "1",
	}

	// Add resolution scaling if specified
	if rb.config.Resolution != "" {
		args = []string{
			"-rtsp_transport", "tcp",
			"-i", rb.config.RTSPUrl,
			"-vf", fmt.Sprintf("scale=%s", rb.config.Resolution),
			"-c:v", "libx264",
			"-preset", "ultrafast",
			"-an", // Drop audio (pcm_alaw not supported in mp4)
			"-f", "segment",
			"-segment_time", strconv.Itoa(rb.config.SegmentSeconds),
			"-segment_format", "mp4",
			"-reset_timestamps", "1",
		}
	}

	args = append(args, segmentPattern)

	for {
		select {
		case <-rb.stopCh:
			return
		default:
		}

		log.Printf("Starting ffmpeg: ffmpeg %s", strings.Join(args, " "))
		rb.ffmpeg = exec.Command("ffmpeg", args...)
		rb.ffmpeg.Stdout = os.Stdout
		rb.ffmpeg.Stderr = os.Stderr

		err := rb.ffmpeg.Run()
		if err != nil {
			log.Printf("ffmpeg exited: %v, restarting in 5s...", err)
			time.Sleep(5 * time.Second)
		}
	}
}

// scanSegments periodically scans for new segment files
func (rb *RingBuffer) scanSegments() {
	ticker := time.NewTicker(time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-rb.stopCh:
			return
		case <-ticker.C:
			rb.updateSegments()
		}
	}
}

// updateSegments scans the buffer directory and updates segment list
func (rb *RingBuffer) updateSegments() {
	files, err := filepath.Glob(filepath.Join(rb.config.BufferDir, "segment_*.mp4"))
	if err != nil {
		log.Printf("Error scanning segments: %v", err)
		return
	}

	rb.mu.Lock()
	defer rb.mu.Unlock()

	// Build map of existing segments
	existing := make(map[string]bool)
	for _, s := range rb.segments {
		existing[s.Path] = true
	}

	// Add new segments
	for _, f := range files {
		if !existing[f] {
			info, err := os.Stat(f)
			if err != nil {
				continue
			}

			// Extract timestamp from filename or use ModTime
			name := filepath.Base(f)
			name = strings.TrimPrefix(name, "segment_")
			name = strings.TrimSuffix(name, ".mp4")

			var unixTimestamp int64
			var segmentPath string

			// Try to parse as Unix timestamp
			if ts, err := strconv.ParseInt(name, 10, 64); err == nil && ts > 1000000000 {
				// Valid Unix timestamp (after year 2001)
				unixTimestamp = ts
				segmentPath = f
			} else {
				// Sequential number or invalid - use ModTime and rename
				unixTimestamp = info.ModTime().Unix()
				newName := fmt.Sprintf("segment_%d.mp4", unixTimestamp)
				newPath := filepath.Join(rb.config.BufferDir, newName)

				// Rename file to use Unix timestamp
				if err := os.Rename(f, newPath); err != nil {
					log.Printf("Warning: failed to rename %s to %s: %v", f, newName, err)
					segmentPath = f // Keep old path
				} else {
					segmentPath = newPath
					log.Printf("Renamed segment: %s -> %s (Unix: %d)", filepath.Base(f), newName, unixTimestamp)
				}
			}

			rb.segments = append(rb.segments, Segment{
				Path:      segmentPath,
				StartTime: time.Unix(unixTimestamp, 0),
				Size:      info.Size(),
			})
		}
	}

	// Sort by time
	sort.Slice(rb.segments, func(i, j int) bool {
		return rb.segments[i].StartTime.Before(rb.segments[j].StartTime)
	})
}

// cleanup removes old segments that exceed buffer limits
func (rb *RingBuffer) cleanup() {
	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-rb.stopCh:
			return
		case <-ticker.C:
			rb.enforceBufferLimits()
		}
	}
}

// enforceBufferLimits removes oldest segments to stay within limits
func (rb *RingBuffer) enforceBufferLimits() {
	rb.mu.Lock()
	defer rb.mu.Unlock()

	now := time.Now()
	var totalSize int64
	var validSegments []Segment

	// Calculate total size and filter by time
	for _, s := range rb.segments {
		age := now.Sub(s.StartTime)
		if age <= rb.config.MaxBufferTime {
			totalSize += s.Size
			validSegments = append(validSegments, s)
		} else {
			// Remove old segment
			os.Remove(s.Path)
			log.Printf("Removed old segment: %s (age: %v)", filepath.Base(s.Path), age)
		}
	}

	rb.segments = validSegments

	// Enforce size limit (remove oldest first)
	for totalSize > rb.config.MaxBufferSize && len(rb.segments) > 0 {
		oldest := rb.segments[0]
		rb.segments = rb.segments[1:]
		totalSize -= oldest.Size
		os.Remove(oldest.Path)
		log.Printf("Removed segment for size limit: %s", filepath.Base(oldest.Path))
	}
}

// GetStatus returns current buffer status
func (rb *RingBuffer) GetStatus() map[string]interface{} {
	rb.mu.RLock()
	defer rb.mu.RUnlock()

	var totalSize int64
	var oldestTime, newestTime time.Time

	if len(rb.segments) > 0 {
		oldestTime = rb.segments[0].StartTime
		newestTime = rb.segments[len(rb.segments)-1].StartTime
		for _, s := range rb.segments {
			totalSize += s.Size
		}
	}

	return map[string]interface{}{
		"running":        rb.running,
		"segment_count":  len(rb.segments),
		"total_size_mb":  float64(totalSize) / 1024 / 1024,
		"buffer_seconds": newestTime.Sub(oldestTime).Seconds(),
		"oldest_segment": oldestTime.Format(time.RFC3339),
		"newest_segment": newestTime.Format(time.RFC3339),
	}
}

// SaveBuffer saves the buffer to a file with time/size constraints
func (rb *RingBuffer) SaveBuffer(maxSeconds int, maxSizeMB int, outputPath string) (string, error) {
	rb.mu.RLock()
	defer rb.mu.RUnlock()

	if len(rb.segments) == 0 {
		return "", fmt.Errorf("no segments available")
	}

	now := time.Now()
	maxDuration := time.Duration(maxSeconds) * time.Second
	maxSize := int64(maxSizeMB) * 1024 * 1024

	// Select segments within constraints (newest first, working backwards)
	var selectedSegments []Segment
	var selectedSize int64
	var selectedDuration time.Duration

	for i := len(rb.segments) - 1; i >= 0; i-- {
		s := rb.segments[i]
		segDuration := time.Duration(rb.config.SegmentSeconds) * time.Second
		age := now.Sub(s.StartTime)

		// Check time limit
		if maxSeconds > 0 && selectedDuration+segDuration > maxDuration {
			break
		}

		// Check size limit
		if maxSizeMB > 0 && selectedSize+s.Size > maxSize {
			break
		}

		// Check if segment is too old (beyond buffer time)
		if age > rb.config.MaxBufferTime {
			break
		}

		selectedSegments = append([]Segment{s}, selectedSegments...)
		selectedSize += s.Size
		selectedDuration += segDuration
	}

	if len(selectedSegments) == 0 {
		return "", fmt.Errorf("no segments match criteria")
	}

	// Generate output path if not specified
	if outputPath == "" {
		outputPath = filepath.Join(rb.config.BufferDir, "..", "saved",
			fmt.Sprintf("recording_%s.mp4", time.Now().Format("20060102_150405")))
	}

	// Ensure output directory exists
	os.MkdirAll(filepath.Dir(outputPath), 0755)

	// Create concat file for ffmpeg
	concatFile := filepath.Join(rb.config.BufferDir, "concat.txt")
	f, err := os.Create(concatFile)
	if err != nil {
		return "", fmt.Errorf("failed to create concat file: %w", err)
	}

	for _, s := range selectedSegments {
		fmt.Fprintf(f, "file '%s'\n", s.Path)
	}
	f.Close()

	// Concatenate segments
	cmd := exec.Command("ffmpeg", "-y",
		"-f", "concat",
		"-safe", "0",
		"-i", concatFile,
		"-c", "copy",
		outputPath)

	output, err := cmd.CombinedOutput()
	os.Remove(concatFile)

	if err != nil {
		return "", fmt.Errorf("ffmpeg concat failed: %v\n%s", err, output)
	}

	log.Printf("Saved %d segments (%.2f MB, %v) to %s",
		len(selectedSegments),
		float64(selectedSize)/1024/1024,
		selectedDuration,
		outputPath)

	return outputPath, nil
}

// GetFrames extracts frames from the buffer at specified times
func (rb *RingBuffer) GetFrames(secondsAgo []float64, outputDir string) ([]string, error) {
	rb.mu.RLock()
	defer rb.mu.RUnlock()

	if len(rb.segments) == 0 {
		return nil, fmt.Errorf("no segments available")
	}

	os.MkdirAll(outputDir, 0755)

	var framePaths []string
	now := time.Now()
	nowUnix := now.Unix()

	log.Printf("GetFrames: now=%d (%s), segments=%d, oldest=%d (%s), newest=%d (%s)",
		nowUnix, now.Local().Format("15:04:05"),
		len(rb.segments),
		rb.segments[0].StartTime.Unix(), rb.segments[0].StartTime.Local().Format("15:04:05"),
		rb.segments[len(rb.segments)-1].StartTime.Unix(), rb.segments[len(rb.segments)-1].StartTime.Local().Format("15:04:05"))

	// Debug: print all segment ranges
	log.Printf("  All segments:")
	for _, s := range rb.segments {
		segEnd := s.StartTime.Add(time.Duration(rb.config.SegmentSeconds) * time.Second)
		log.Printf("    %s: Unix %d-%d (%s - %s)",
			filepath.Base(s.Path),
			s.StartTime.Unix(), segEnd.Unix(),
			s.StartTime.Local().Format("15:04:05"), segEnd.Local().Format("15:04:05"))
	}

	for i, secAgo := range secondsAgo {
		targetTime := now.Add(-time.Duration(secAgo * float64(time.Second)))
		targetUnix := targetTime.Unix()
		log.Printf("  Looking for frame at %.1fs ago (Unix %d, local %s)", secAgo, targetUnix, targetTime.Local().Format("15:04:05"))

		// Find segment containing this time
		var targetSegment *Segment
		for j := range rb.segments {
			s := &rb.segments[j]
			segEnd := s.StartTime.Add(time.Duration(rb.config.SegmentSeconds) * time.Second)
			if !targetTime.Before(s.StartTime) && targetTime.Before(segEnd) {
				targetSegment = s
				log.Printf("    Found segment: %s (Unix %d-%d, local %s - %s)",
					filepath.Base(s.Path),
					s.StartTime.Unix(), segEnd.Unix(),
					s.StartTime.Local().Format("15:04:05"),
					segEnd.Local().Format("15:04:05"))
				break
			}
		}

		if targetSegment == nil {
			log.Printf("    No segment found for target Unix %d (local %s)", targetUnix, targetTime.Local().Format("15:04:05"))
			continue
		}

		// Calculate offset within segment
		offset := targetTime.Sub(targetSegment.StartTime).Seconds()

		// Extract frame
		outputPath := filepath.Join(outputDir, fmt.Sprintf("frame_%d_%.1fs_ago.jpg", i, secAgo))
		cmd := exec.Command("ffmpeg", "-y",
			"-ss", fmt.Sprintf("%.2f", offset),
			"-i", targetSegment.Path,
			"-vframes", "1",
			"-q:v", "2",
			outputPath)

		output, err := cmd.CombinedOutput()
		if err != nil {
			log.Printf("Failed to extract frame at %.1fs ago: %v\nFFmpeg output:\n%s", secAgo, err, string(output))
			continue
		}

		framePaths = append(framePaths, outputPath)
	}

	return framePaths, nil
}

// HTTP Handlers

func (rb *RingBuffer) handleStatus(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(rb.GetStatus())
}

func (rb *RingBuffer) handleSave(w http.ResponseWriter, r *http.Request) {
	maxSeconds, _ := strconv.Atoi(r.URL.Query().Get("seconds"))
	maxSizeMB, _ := strconv.Atoi(r.URL.Query().Get("size_mb"))
	outputPath := r.URL.Query().Get("output")

	// Default to 30 seconds if nothing specified
	if maxSeconds == 0 && maxSizeMB == 0 {
		maxSeconds = 30
	}

	savedPath, err := rb.SaveBuffer(maxSeconds, maxSizeMB, outputPath)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"saved_path": savedPath,
	})
}

func (rb *RingBuffer) handleFrames(w http.ResponseWriter, r *http.Request) {
	// Parse seconds_ago parameter (comma-separated)
	secondsStr := r.URL.Query().Get("seconds_ago")
	if secondsStr == "" {
		secondsStr = "0,5,10" // Default: now, 5s ago, 10s ago
	}

	var secondsAgo []float64
	for _, s := range strings.Split(secondsStr, ",") {
		if v, err := strconv.ParseFloat(strings.TrimSpace(s), 64); err == nil {
			secondsAgo = append(secondsAgo, v)
		}
	}

	outputDir := r.URL.Query().Get("output_dir")
	if outputDir == "" {
		outputDir = filepath.Join(rb.config.BufferDir, "..", "frames")
	}

	paths, err := rb.GetFrames(secondsAgo, outputDir)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"frames": paths,
	})
}

func main() {
	// Parse flags
	rtspUrl := flag.String("rtsp", "", "RTSP stream URL (required)")
	bufferDir := flag.String("buffer-dir", "/tmp/ringbuffer/segments", "Directory for segment files")
	segmentSec := flag.Int("segment-sec", 5, "Duration of each segment in seconds")
	maxBufferMin := flag.Int("max-buffer-min", 30, "Maximum buffer duration in minutes")
	maxBufferMB := flag.Int("max-buffer-mb", 500, "Maximum buffer size in MB")
	resolution := flag.String("resolution", "", "Output resolution (e.g., 1280x720). Empty = original")
	port := flag.Int("port", 8085, "HTTP API port")
	flag.Parse()

	if *rtspUrl == "" {
		log.Fatal("RTSP URL is required. Use -rtsp flag.")
	}

	config := Config{
		RTSPUrl:        *rtspUrl,
		BufferDir:      *bufferDir,
		SegmentSeconds: *segmentSec,
		MaxBufferTime:  time.Duration(*maxBufferMin) * time.Minute,
		MaxBufferSize:  int64(*maxBufferMB) * 1024 * 1024,
		Resolution:     *resolution,
		Port:           *port,
	}

	log.Printf("Ring Buffer Config:")
	log.Printf("  RTSP URL: %s", config.RTSPUrl)
	log.Printf("  Buffer Dir: %s", config.BufferDir)
	log.Printf("  Segment Duration: %ds", config.SegmentSeconds)
	log.Printf("  Max Buffer: %d min / %d MB", *maxBufferMin, *maxBufferMB)
	log.Printf("  Resolution: %s", config.Resolution)

	rb := NewRingBuffer(config)

	// Start recording
	if err := rb.Start(); err != nil {
		log.Fatalf("Failed to start: %v", err)
	}

	// Setup HTTP API
	r := mux.NewRouter()
	r.HandleFunc("/status", rb.handleStatus).Methods("GET")
	r.HandleFunc("/save", rb.handleSave).Methods("POST", "GET")
	r.HandleFunc("/frames", rb.handleFrames).Methods("GET")

	// Graceful shutdown
	go func() {
		sigCh := make(chan os.Signal, 1)
		signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)
		<-sigCh
		log.Println("Shutting down...")
		rb.Stop()
		os.Exit(0)
	}()

	log.Printf("HTTP API listening on :%d", config.Port)
	log.Printf("  GET  /status - Buffer status")
	log.Printf("  POST /save?seconds=30&size_mb=50 - Save buffer")
	log.Printf("  GET  /frames?seconds_ago=0,5,10 - Extract frames")

	log.Fatal(http.ListenAndServe(fmt.Sprintf(":%d", config.Port), r))
}
