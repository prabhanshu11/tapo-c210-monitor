#!/usr/bin/env python3
"""Test pytapo direct pan control - no emulator needed."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

CAMERA_IP = os.getenv("TAPO_HOST", "192.168.29.183")
CAMERA_USER = os.getenv("TAPO_USERNAME", "admin")
CAMERA_PASS = os.getenv("TAPO_PASSWORD")
CLOUD_PASS = os.getenv("TPLINK_CLOUD_PASSWORD")

if not CAMERA_PASS:
    print("ERROR: Set TAPO_PASSWORD in .env file")
    sys.exit(1)

print(f"Camera IP: {CAMERA_IP}")
print(f"Username: {CAMERA_USER}")
print(f"Password: {'*' * len(CAMERA_PASS)}")
print()

from pytapo import Tapo

def try_connect(user, password, cloud_password=None):
    """Try to connect with given credentials."""
    try:
        if cloud_password:
            tapo = Tapo(CAMERA_IP, user, password, cloud_password)
        else:
            tapo = Tapo(CAMERA_IP, user, password)
        return tapo
    except Exception as e:
        return None

def main():
    tapo = None

    # Try different auth combinations
    attempts = [
        ("Camera account", CAMERA_USER, CAMERA_PASS, None),
        ("admin + camera pass", "admin", CAMERA_PASS, None),
    ]

    if CLOUD_PASS:
        attempts.extend([
            ("Camera + cloud pass", CAMERA_USER, CAMERA_PASS, CLOUD_PASS),
            ("admin + cloud pass", "admin", CLOUD_PASS, None),
        ])

    for desc, user, passwd, cloud in attempts:
        print(f"Trying: {desc}...")
        tapo = try_connect(user, passwd, cloud)
        if tapo:
            print(f"  SUCCESS!")
            break
        print(f"  Failed")

    if not tapo:
        print("\nAll authentication methods failed.")
        print("Check your credentials in .env file.")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("CONNECTED TO CAMERA")
    print("=" * 50)

    # Get info
    try:
        info = tapo.getBasicInfo()
        device_info = info.get("device_info", {}).get("basic_info", {})
        print(f"Model: {device_info.get('device_model', 'unknown')}")
        print(f"Name: {device_info.get('device_alias', 'unknown')}")
    except Exception as e:
        print(f"Could not get info: {e}")

    # Test pan
    print("\n" + "=" * 50)
    print("TESTING PAN CONTROL")
    print("=" * 50)

    try:
        print("\nPanning RIGHT...")
        tapo.moveMotor(20, 0)  # x=horizontal, y=vertical
        print("  Command sent!")

        import time
        time.sleep(2)

        print("\nPanning LEFT...")
        tapo.moveMotor(-20, 0)
        print("  Command sent!")

        print("\n SUCCESS - Did you hear/see the camera move?")

    except Exception as e:
        print(f"Pan failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
