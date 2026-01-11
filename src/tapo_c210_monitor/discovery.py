"""
Camera Discovery Module

Discovers Tapo camera IP on local network by scanning for RTSP port.
Includes wake mechanism for sleeping cameras.
"""

import socket
import subprocess
import time
import concurrent.futures
from typing import Optional


def check_port(ip: str, port: int = 554, timeout: float = 2.0) -> bool:
    """Check if a port is open on the given IP."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((ip, port))
        return result == 0
    except socket.error:
        return False
    finally:
        sock.close()


def discover_camera(
    subnet: str = "192.168.29",
    port: int = 554,
    timeout: float = 2.0,
    max_workers: int = 50
) -> Optional[str]:
    """
    Discover camera IP by scanning subnet for open RTSP port.

    Args:
        subnet: Network subnet prefix (e.g., "192.168.29")
        port: Port to scan (default: 554 for RTSP)
        timeout: Socket timeout in seconds
        max_workers: Number of parallel workers for scanning

    Returns:
        Camera IP address if found, None otherwise
    """
    ips = [f"{subnet}.{i}" for i in range(1, 255)]

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ip = {
            executor.submit(check_port, ip, port, timeout): ip
            for ip in ips
        }

        for future in concurrent.futures.as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                if future.result():
                    return ip
            except Exception:
                pass

    return None


def get_rtsp_url(
    camera_ip: str,
    username: str = "prabhanshu",
    password: str = "iamapantar",
    stream: str = "stream1"
) -> str:
    """
    Get RTSP URL for the camera.

    Args:
        camera_ip: Camera IP address
        username: Camera account username
        password: Camera account password
        stream: Stream type ("stream1" for HD, "stream2" for SD)

    Returns:
        RTSP URL string
    """
    return f"rtsp://{username}:{password}@{camera_ip}/{stream}"


if __name__ == "__main__":
    import sys

    print("Discovering camera...")
    camera_ip = discover_camera()

    if camera_ip:
        print(f"Camera found: {camera_ip}")
        print(f"RTSP URL: {get_rtsp_url(camera_ip)}")
        sys.exit(0)
    else:
        print("No camera found on network")
        sys.exit(1)
