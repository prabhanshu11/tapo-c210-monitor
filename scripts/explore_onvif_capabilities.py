#!/usr/bin/env python3
"""Deep exploration of ONVIF capabilities.

Checks for:
- Auxiliary commands (vendor-specific like calibration)
- Presets
- PTZ configuration options
- Any calibration-related functions
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from onvif import ONVIFCamera

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

CAMERA_IP = os.getenv("TAPO_HOST", "192.168.29.183")
CAMERA_USER = os.getenv("TAPO_USERNAME", "")
CAMERA_PASS = os.getenv("TAPO_PASSWORD", "")

print("=" * 60)
print("ONVIF DEEP CAPABILITY EXPLORATION")
print("=" * 60)
print(f"Camera: {CAMERA_IP}:2020")
print()

cam = ONVIFCamera(CAMERA_IP, 2020, CAMERA_USER, CAMERA_PASS)
ptz = cam.create_ptz_service()
media = cam.create_media_service()

profiles = media.GetProfiles()
profile_token = profiles[0].token
print(f"Profile: {profile_token}")

# Get PTZ node details
print("\n" + "=" * 60)
print("PTZ NODE DETAILS")
print("=" * 60)

nodes = ptz.GetNodes()
for node in nodes:
    print(f"\nNode: {node.Name} ({node.token})")
    print(f"  Fixed Home: {getattr(node, 'FixedHomePosition', 'N/A')}")
    print(f"  Max Presets: {getattr(node, 'MaximumNumberOfPresets', 'N/A')}")
    print(f"  Home Supported: {getattr(node, 'HomeSupported', 'N/A')}")

    # Auxiliary commands (vendor-specific)
    if hasattr(node, 'AuxiliaryCommands'):
        aux = node.AuxiliaryCommands
        if aux:
            print(f"  Auxiliary Commands: {aux}")
        else:
            print("  Auxiliary Commands: None")
    else:
        print("  Auxiliary Commands: Not reported")

    # Extension data
    if hasattr(node, 'Extension'):
        print(f"  Extension: {node.Extension}")

# Get PTZ configuration
print("\n" + "=" * 60)
print("PTZ CONFIGURATION")
print("=" * 60)

configs = ptz.GetConfigurations()
for cfg in configs:
    print(f"\nConfig: {cfg.Name}")
    print(f"  Token: {cfg.token}")
    print(f"  Node Token: {cfg.NodeToken}")
    print(f"  Default Speed:")
    if hasattr(cfg, 'DefaultPTZSpeed') and cfg.DefaultPTZSpeed:
        speed = cfg.DefaultPTZSpeed
        if hasattr(speed, 'PanTilt') and speed.PanTilt:
            print(f"    Pan/Tilt: ({speed.PanTilt.x}, {speed.PanTilt.y})")
        if hasattr(speed, 'Zoom') and speed.Zoom:
            print(f"    Zoom: {speed.Zoom.x}")

    # Default timeout
    if hasattr(cfg, 'DefaultPTZTimeout'):
        print(f"  Default Timeout: {cfg.DefaultPTZTimeout}")

# Check presets
print("\n" + "=" * 60)
print("PRESETS")
print("=" * 60)

try:
    presets = ptz.GetPresets({'ProfileToken': profile_token})
    if presets:
        for preset in presets:
            print(f"  Preset: {preset.Name} (token: {preset.token})")
            if hasattr(preset, 'PTZPosition') and preset.PTZPosition:
                pos = preset.PTZPosition
                if hasattr(pos, 'PanTilt') and pos.PanTilt:
                    print(f"    Position: ({pos.PanTilt.x}, {pos.PanTilt.y})")
    else:
        print("  No presets defined")
except Exception as e:
    print(f"  Error getting presets: {e}")

# Check for service capabilities
print("\n" + "=" * 60)
print("SERVICE CAPABILITIES")
print("=" * 60)

try:
    caps = ptz.GetServiceCapabilities()
    print(f"Capabilities object: {caps}")

    # Check each capability
    for attr in dir(caps):
        if not attr.startswith('_'):
            val = getattr(caps, attr, None)
            if val is not None and not callable(val):
                print(f"  {attr}: {val}")
except Exception as e:
    print(f"  Error: {e}")

# Check available PTZ operations
print("\n" + "=" * 60)
print("AVAILABLE OPERATIONS")
print("=" * 60)

# List all ptz service methods
ptz_methods = [m for m in dir(ptz) if not m.startswith('_') and callable(getattr(ptz, m))]
print("PTZ Service methods:")
for m in sorted(ptz_methods):
    if any(kw in m.lower() for kw in ['move', 'home', 'preset', 'stop', 'status', 'aux', 'calibr']):
        print(f"  -> {m}")

# Test SendAuxiliaryCommand (if supported)
print("\n" + "=" * 60)
print("AUXILIARY COMMAND TEST")
print("=" * 60)

# Common auxiliary commands to try
aux_commands = [
    "tt:calibrate",
    "tt:HomePositionCalibration",
    "tt:AutoFocus",
    "tt:ResetPanTilt",
    "tapo:calibrate",
    "tplink:calibrate",
]

for cmd in aux_commands:
    try:
        result = ptz.SendAuxiliaryCommand({
            'ProfileToken': profile_token,
            'AuxiliaryData': cmd
        })
        print(f"  {cmd}: SUCCESS - {result}")
    except Exception as e:
        err = str(e)
        if "not supported" in err.lower() or "invalid" in err.lower():
            print(f"  {cmd}: Not supported")
        else:
            print(f"  {cmd}: Error - {err[:60]}")

# Get current status with details
print("\n" + "=" * 60)
print("CURRENT STATUS (DETAILED)")
print("=" * 60)

status = ptz.GetStatus({'ProfileToken': profile_token})
print(f"Position:")
if status.Position:
    if status.Position.PanTilt:
        print(f"  Pan: {status.Position.PanTilt.x}")
        print(f"  Tilt: {status.Position.PanTilt.y}")
    if status.Position.Zoom:
        print(f"  Zoom: {status.Position.Zoom.x}")

print(f"MoveStatus:")
if hasattr(status, 'MoveStatus') and status.MoveStatus:
    print(f"  PanTilt: {status.MoveStatus.PanTilt}")
    if hasattr(status.MoveStatus, 'Zoom'):
        print(f"  Zoom: {status.MoveStatus.Zoom}")

if hasattr(status, 'Error') and status.Error:
    print(f"Error: {status.Error}")

print("\n" + "=" * 60)
print("CONCLUSION")
print("=" * 60)
print("""
The Tapo C210's 'Pan and Tilt Correction' in the app likely does:
1. Re-calibrates motor encoder positions against physical limits
2. Resets any drift accumulated over time
3. Uses proprietary TP-Link protocol (not exposed via ONVIF)

ONVIF provides position FEEDBACK but the internal calibration
that maps encoder ticks to physical position is proprietary.
""")
