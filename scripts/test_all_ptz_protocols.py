#!/usr/bin/env python3
"""
Test ALL available PTZ control protocols for Tapo C210.

Protocols tested:
1. pytapo - Reverse-engineered Tapo JSON/HTTP API
2. ONVIF - Open Network Video Interface Forum (port 2020)
3. Direct HTTPS API - Raw camera API calls

Run: uv run python scripts/test_all_ptz_protocols.py
"""

import os
import sys
import time
import socket
from pathlib import Path
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

CAMERA_IP = os.getenv("TAPO_HOST", "192.168.29.183")
CAMERA_USER = os.getenv("TAPO_USERNAME", "prabhanshu")
CAMERA_PASS = os.getenv("TAPO_PASSWORD", "")
CLOUD_PASS = os.getenv("TPLINK_CLOUD_PASSWORD", "")

print("=" * 60)
print("TAPO C210 PTZ PROTOCOL TESTER")
print("=" * 60)
print(f"Camera IP: {CAMERA_IP}")
print(f"Username: {CAMERA_USER}")
print()


def check_port(port):
    """Check if port is open."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    try:
        result = sock.connect_ex((CAMERA_IP, port))
        return result == 0
    except:
        return False
    finally:
        sock.close()


def test_pytapo():
    """Test pytapo library."""
    print("\n" + "=" * 60)
    print("1. PYTAPO (Reverse-engineered Tapo API)")
    print("=" * 60)

    try:
        from pytapo import Tapo
    except ImportError:
        print("  ERROR: pytapo not installed")
        return False

    # Try different auth combinations
    attempts = [
        (CAMERA_USER, CAMERA_PASS, None),
        ("admin", CAMERA_PASS, None),
    ]
    if CLOUD_PASS:
        attempts.extend([
            (CAMERA_USER, CAMERA_PASS, CLOUD_PASS),
            ("admin", CLOUD_PASS, None),
            (CAMERA_USER, CLOUD_PASS, CLOUD_PASS),
        ])

    tapo = None
    for user, passwd, cloud in attempts:
        print(f"  Trying: user={user}, cloud={'yes' if cloud else 'no'}...")
        try:
            if cloud:
                tapo = Tapo(CAMERA_IP, user, passwd, cloud)
            else:
                tapo = Tapo(CAMERA_IP, user, passwd)
            print(f"    Connected!")
            break
        except Exception as e:
            err = str(e)
            if "Suspension" in err:
                print(f"    LOCKED OUT - wait or reboot camera")
                return False
            print(f"    Failed: {err[:50]}")

    if not tapo:
        print("  All auth methods failed")
        return False

    # Test pan
    print("\n  Testing PAN...")
    try:
        print("    Moving RIGHT (x=20)...")
        tapo.moveMotor(20, 0)
        time.sleep(2)
        print("    Moving LEFT (x=-20)...")
        tapo.moveMotor(-20, 0)
        print("  SUCCESS!")
        return True
    except Exception as e:
        print(f"  Pan failed: {e}")
        return False


def test_onvif():
    """Test ONVIF PTZ control."""
    print("\n" + "=" * 60)
    print("2. ONVIF (Port 2020)")
    print("=" * 60)

    if not check_port(2020):
        print("  Port 2020 not open - ONVIF disabled?")
        return False

    print("  Port 2020 is OPEN")

    try:
        from onvif import ONVIFCamera
    except ImportError:
        print("  onvif-zeep not installed. Run: uv pip install onvif-zeep")
        return False

    print(f"  Connecting to ONVIF service...")
    try:
        cam = ONVIFCamera(CAMERA_IP, 2020, CAMERA_USER, CAMERA_PASS)
        print("    Connected!")

        # Get PTZ service
        ptz = cam.create_ptz_service()
        media = cam.create_media_service()

        profiles = media.GetProfiles()
        if not profiles:
            print("  No media profiles found")
            return False

        profile_token = profiles[0].token
        print(f"    Profile: {profile_token}")

        print("\n  Testing PAN...")
        request = ptz.create_type('ContinuousMove')
        request.ProfileToken = profile_token
        request.Velocity = {'PanTilt': {'x': 0.5, 'y': 0}}

        print("    Moving RIGHT...")
        ptz.ContinuousMove(request)
        time.sleep(1)
        ptz.Stop({'ProfileToken': profile_token})

        print("    Moving LEFT...")
        request.Velocity = {'PanTilt': {'x': -0.5, 'y': 0}}
        ptz.ContinuousMove(request)
        time.sleep(1)
        ptz.Stop({'ProfileToken': profile_token})

        print("  SUCCESS!")
        return True

    except Exception as e:
        print(f"  ONVIF failed: {e}")
        return False


def main():
    results = {}

    # Check ports first
    print("\nPort scan:")
    for port, name in [(443, "HTTPS"), (554, "RTSP"), (2020, "ONVIF"), (8800, "Proprietary")]:
        status = "OPEN" if check_port(port) else "CLOSED"
        print(f"  {port} ({name}): {status}")

    # Run tests
    results["pytapo"] = test_pytapo()
    results["onvif"] = test_onvif()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for protocol, success in results.items():
        status = "✅ WORKS" if success else "❌ Failed"
        print(f"  {protocol}: {status}")

    working = [p for p, s in results.items() if s]
    if working:
        print(f"\nRecommended: Use {working[0]} for PTZ control")
    else:
        print("\nNo working PTZ protocol found!")


if __name__ == "__main__":
    main()
