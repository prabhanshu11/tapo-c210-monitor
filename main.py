#!/usr/bin/env python3
"""TAPO C210 Monitor - Main entry point."""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def main():
    """Main entry point for TAPO C210 Monitor."""
    parser = argparse.ArgumentParser(
        description="TAPO C210 Intelligent Monitoring System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Launch GUI control panel
    python main.py gui

    # Test camera connection
    python main.py test-camera

    # Test Android connection
    python main.py test-android

    # Sync recordings from camera
    python main.py sync --days 7

    # Capture RTSP stream snapshot
    python main.py snapshot --output capture.jpg

    # Watch Android Tapo folder for new files
    python main.py watch-android --output ./synced
""",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # GUI command
    gui_parser = subparsers.add_parser("gui", help="Launch control panel GUI")

    # Test camera command
    test_cam_parser = subparsers.add_parser("test-camera", help="Test camera connection")

    # Test Android command
    test_android_parser = subparsers.add_parser("test-android", help="Test Android connection")

    # Sync command
    sync_parser = subparsers.add_parser("sync", help="Sync recordings from camera")
    sync_parser.add_argument("--days", type=int, default=1, help="Number of days to sync")
    sync_parser.add_argument("--output", "-o", default="./recordings", help="Output directory")

    # Snapshot command
    snap_parser = subparsers.add_parser("snapshot", help="Take RTSP snapshot")
    snap_parser.add_argument("--output", "-o", help="Output file path")
    snap_parser.add_argument("--quality", choices=["hd", "sd"], default="hd", help="Stream quality")

    # Watch Android command
    watch_parser = subparsers.add_parser("watch-android", help="Watch Android for new Tapo files")
    watch_parser.add_argument("--output", "-o", default="./synced", help="Output directory")

    # Info command
    info_parser = subparsers.add_parser("info", help="Show camera and system info")

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    if args.command == "gui":
        run_gui()
    elif args.command == "test-camera":
        test_camera()
    elif args.command == "test-android":
        test_android()
    elif args.command == "sync":
        sync_recordings(args.days, args.output)
    elif args.command == "snapshot":
        take_snapshot(args.output, args.quality)
    elif args.command == "watch-android":
        watch_android(args.output)
    elif args.command == "info":
        show_info()
    else:
        parser.print_help()


def run_gui():
    """Launch the GUI control panel."""
    print("Launching control panel...")

    # Initialize components
    camera = None
    stream = None
    sync = None
    android_ui = None

    try:
        from src.tapo_c210_monitor.camera import TapoCamera
        camera = TapoCamera.from_env()
    except Exception as e:
        print(f"Camera init skipped: {e}")

    try:
        from src.tapo_c210_monitor.android.ui import UIAutomation
        android_ui = UIAutomation()
    except Exception as e:
        print(f"Android init skipped: {e}")

    if camera:
        try:
            from src.tapo_c210_monitor.stream import StreamCapture
            stream = StreamCapture(camera.get_rtsp_url("hd"))
        except Exception as e:
            print(f"Stream init skipped: {e}")

        try:
            from src.tapo_c210_monitor.sync import RecordingSync
            output_dir = os.getenv("RECORDINGS_OUTPUT_DIR", "./recordings")
            if camera.connect():
                sync = RecordingSync(camera.tapo, output_dir)
        except Exception as e:
            print(f"Sync init skipped: {e}")

    from src.tapo_c210_monitor.gui.control_panel import ControlPanel

    panel = ControlPanel(
        android_ui=android_ui,
        camera=camera,
        stream=stream,
        sync=sync,
    )
    panel.run()


def test_camera():
    """Test camera connection."""
    from src.tapo_c210_monitor.camera import TapoCamera

    print("Testing camera connection...")

    try:
        camera = TapoCamera.from_env()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("\nCreate a .env file with:")
        print("  TAPO_HOST=<camera ip>")
        print("  TAPO_USERNAME=<camera account username>")
        print("  TAPO_PASSWORD=<camera account password>")
        return

    if camera.connect():
        print("Connected successfully!")
        print("\nCamera Info:")
        info = camera.get_basic_info()
        for key, value in info.items():
            print(f"  {key}: {value}")

        print(f"\nRTSP URLs:")
        print(f"  HD: {camera.get_rtsp_url('hd')}")
        print(f"  SD: {camera.get_rtsp_url('sd')}")
        print(f"  ONVIF: {camera.get_onvif_url()}")
    else:
        print("Failed to connect to camera")
        print("\nTroubleshooting:")
        print("  1. Check camera IP is correct and reachable")
        print("  2. Verify camera account credentials (Settings > Advanced > Camera Account in Tapo app)")
        print("  3. Try using 'admin' as username with TP-Link cloud password")


def test_android():
    """Test Android connection."""
    from src.tapo_c210_monitor.android.controller import AndroidController

    print("Testing Android connection...")

    controller = AndroidController()

    if controller.connect():
        print("Connected successfully!")
        print("\nDevice Info:")
        info = controller.get_device_info()
        for key, value in info.items():
            print(f"  {key}: {value}")

        print("\nChecking Tapo app...")
        if controller.is_tapo_running():
            print("  Tapo app is running")
        else:
            print("  Tapo app is not running")

        print("\nCurrent activity:")
        print(f"  {controller.get_current_activity()}")
    else:
        print("Failed to connect to Android device")
        print("\nTroubleshooting:")
        print("  1. Enable USB debugging on Android device")
        print("  2. Connect device via USB or set up ADB over WiFi")
        print("  3. Run: adb devices (should show your device)")
        print("  4. Install android-tools: sudo pacman -S android-tools")


def sync_recordings(days: int, output_dir: str):
    """Sync recordings from camera."""
    from src.tapo_c210_monitor.camera import TapoCamera
    from src.tapo_c210_monitor.sync import RecordingSync

    print(f"Syncing last {days} days of recordings to {output_dir}...")

    try:
        camera = TapoCamera.from_env()
    except ValueError as e:
        print(f"Configuration error: {e}")
        return

    if not camera.connect():
        print("Failed to connect to camera")
        return

    sync = RecordingSync(camera.tapo, output_dir)
    result = sync.sync_recent(days=days)

    total = sum(len(files) for files in result.values())
    print(f"\nSynced {total} recordings from {len(result)} days")

    for date, files in result.items():
        print(f"  {date}: {len(files)} files")


def take_snapshot(output_path: str | None, quality: str):
    """Take RTSP snapshot."""
    from src.tapo_c210_monitor.camera import TapoCamera
    from src.tapo_c210_monitor.stream import StreamCapture

    print("Taking snapshot...")

    try:
        camera = TapoCamera.from_env()
    except ValueError as e:
        print(f"Configuration error: {e}")
        return

    rtsp_url = camera.get_rtsp_url(quality)
    print(f"Connecting to: {rtsp_url}")

    stream = StreamCapture(rtsp_url)
    path = stream.save_snapshot(output_path)

    if path:
        print(f"Snapshot saved: {path}")
    else:
        print("Failed to capture snapshot")


def watch_android(output_dir: str):
    """Watch Android Tapo folder for new files."""
    from src.tapo_c210_monitor.android.controller import AndroidController
    from src.tapo_c210_monitor.android.file_transfer import FileTransfer

    print(f"Watching Android Tapo folder, syncing to {output_dir}")
    print("Press Ctrl+C to stop\n")

    controller = AndroidController()
    if not controller.connect():
        print("Failed to connect to Android")
        return

    transfer = FileTransfer(controller)

    try:
        for path in transfer.watch_directory(
            "/sdcard/DCIM/Tapo",
            output_dir,
            poll_interval=5.0,
        ):
            print(f"Synced: {path}")
    except KeyboardInterrupt:
        print("\nStopped watching")


def show_info():
    """Show system and camera info."""
    print("TAPO C210 Monitor - System Info")
    print("=" * 40)

    # Check camera config
    print("\nCamera Configuration:")
    host = os.getenv("TAPO_HOST")
    username = os.getenv("TAPO_USERNAME")
    password = os.getenv("TAPO_PASSWORD")

    if host:
        print(f"  Host: {host}")
        print(f"  Username: {username or 'not set'}")
        print(f"  Password: {'*' * len(password) if password else 'not set'}")
    else:
        print("  Not configured (create .env file)")

    # Check ADB
    print("\nADB Status:")
    try:
        import subprocess

        result = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=5)
        devices = [l for l in result.stdout.split("\n") if "device" in l and "List" not in l]
        print(f"  Devices: {len(devices)} connected")
        for d in devices:
            print(f"    {d}")
    except FileNotFoundError:
        print("  ADB not found (install android-tools)")
    except Exception as e:
        print(f"  Error: {e}")

    # Check dependencies
    print("\nDependencies:")
    deps = [
        ("pytapo", "Camera API"),
        ("cv2", "OpenCV"),
        ("PIL", "Pillow"),
        ("pytesseract", "OCR"),
        ("ppadb", "Python ADB"),
    ]

    for module, name in deps:
        try:
            __import__(module)
            print(f"  {name}: OK")
        except ImportError:
            print(f"  {name}: NOT INSTALLED")


if __name__ == "__main__":
    main()
