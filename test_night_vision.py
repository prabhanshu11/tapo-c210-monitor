#!/usr/bin/env python3
"""Test pytapo night vision control for Tapo C210."""
import subprocess
import sys
sys.path.insert(0, 'src')

from pytapo import Tapo

HOST = '192.168.29.183'
USER = 'admin'

# Get password from pass
try:
    PASS = subprocess.check_output(['pass', 'show', 'tapo/cloud-password']).decode().strip()
except:
    PASS = input('Enter TP-Link cloud password: ')

print(f'Connecting to {HOST}...')
tapo = Tapo(HOST, USER, PASS)
print('Connected!')

# Get device info
info = tapo.getBasicInfo()
device_info = info.get('device_info', {}).get('basic_info', {})
print(f"Device: {device_info.get('device_alias', 'Unknown')}")
print(f"Model: {device_info.get('device_model', 'Unknown')}")
print(f"Firmware: {device_info.get('sw_version', 'Unknown')}")

# Get night vision capability
print('\n=== Night Vision Capability ===')
try:
    cap = tapo.getNightVisionCapability()
    print(f'Capability: {cap}')
except Exception as e:
    print(f'Error: {e}')

# Get current night vision config
print('\n=== Current Night Vision Config ===')
try:
    config = tapo.getNightVisionModeConfig()
    print(f'Config: {config}')
except Exception as e:
    print(f'Error: {e}')

# Get day/night mode
print('\n=== Day/Night Mode ===')
try:
    mode = tapo.getDayNightMode()
    print(f'Mode: {mode}')
except Exception as e:
    print(f'Error: {e}')

# Enable night vision (IR on)
print('\n=== Enabling Night Vision ===')
try:
    # Try setNightVisionModeConfig first
    result = tapo.setNightVisionModeConfig('on')  # or 'off', 'auto'
    print(f'setNightVisionModeConfig result: {result}')
except Exception as e:
    print(f'setNightVisionModeConfig error: {e}')
    try:
        # Fallback to setDayNightMode
        result = tapo.setDayNightMode('off')  # off = force night mode
        print(f'setDayNightMode result: {result}')
    except Exception as e2:
        print(f'setDayNightMode error: {e2}')

print('\nDone! Capture RTSP frame to verify.')
