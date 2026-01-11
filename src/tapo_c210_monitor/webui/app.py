"""
Web UI for Tapo C210 Monitor Configuration

A simple web interface to collect camera settings and test connections.
"""

import os
import json
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from ..discovery import discover_camera, check_port, get_rtsp_url

app = FastAPI(title="Tapo C210 Monitor Setup")

CONFIG_FILE = Path.home() / ".tapo_c210_config.json"


def load_config() -> dict:
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}


def save_config(config: dict):
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


@app.get("/", response_class=HTMLResponse)
async def index():
    config = load_config()
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Tapo C210 Setup</title>
    <style>
        body {{ font-family: system-ui; background: #0d1117; color: #c9d1d9; padding: 2rem; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        h1 {{ text-align: center; }}
        .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1.5rem; margin: 1rem 0; }}
        input {{ width: 100%; padding: 0.5rem; margin: 0.5rem 0; background: #0d1117; border: 1px solid #30363d; color: #c9d1d9; border-radius: 4px; }}
        button {{ padding: 0.75rem 1.5rem; background: #58a6ff; border: none; border-radius: 6px; color: #0d1117; cursor: pointer; margin: 0.25rem; }}
        .result {{ padding: 1rem; margin-top: 1rem; border-radius: 6px; }}
        .success {{ background: rgba(63,185,80,0.2); color: #3fb950; }}
        .error {{ background: rgba(248,81,73,0.2); color: #f85149; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Tapo C210 Monitor Setup</h1>

        <div class="card">
            <h3>1. Mobile App Setup</h3>
            <ul>
                <li>Enable Third-Party Compatibility (Me > Settings)</li>
                <li>Create Camera Account (Camera > Settings > Advanced)</li>
                <li>Reboot camera (unplug/replug)</li>
            </ul>
        </div>

        <div class="card">
            <h3>2. Camera Credentials</h3>
            <label>Username:</label>
            <input type="text" id="username" value="{config.get('camera_username', '')}">
            <label>Password:</label>
            <input type="password" id="password" value="{config.get('camera_password', '')}">
            <label>Subnet:</label>
            <input type="text" id="subnet" value="{config.get('subnet', '192.168.29')}">
        </div>

        <div class="card">
            <h3>3. Test Connection</h3>
            <button onclick="discover()">Discover Camera</button>
            <button onclick="test()">Test RTSP</button>
            <button onclick="save()">Save Config</button>
            <div id="result"></div>
        </div>
    </div>

    <script>
        const result = document.getElementById('result');

        async function discover() {{
            const subnet = document.getElementById('subnet').value;
            result.className = 'result';
            result.textContent = 'Scanning...';
            const r = await fetch('/api/discover?subnet=' + subnet);
            const d = await r.json();
            if (d.camera_ip) {{
                result.className = 'result success';
                result.textContent = 'Found: ' + d.camera_ip + ' (ports: ' + d.ports_open.join(', ') + ')';
            }} else {{
                result.className = 'result error';
                result.textContent = 'No camera found';
            }}
        }}

        async function test() {{
            result.className = 'result';
            result.textContent = 'Testing...';
            const r = await fetch('/api/test', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    username: document.getElementById('username').value,
                    password: document.getElementById('password').value,
                    subnet: document.getElementById('subnet').value
                }})
            }});
            const d = await r.json();
            result.className = 'result ' + (d.success ? 'success' : 'error');
            result.textContent = d.success ? 'RTSP works! Camera: ' + d.camera_ip : d.error;
        }}

        async function save() {{
            const r = await fetch('/api/save', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    camera_username: document.getElementById('username').value,
                    camera_password: document.getElementById('password').value,
                    subnet: document.getElementById('subnet').value
                }})
            }});
            const d = await r.json();
            result.className = 'result ' + (d.success ? 'success' : 'error');
            result.textContent = d.success ? 'Saved!' : d.error;
        }}
    </script>
</body>
</html>"""


@app.get("/api/discover")
async def api_discover(subnet: str = "192.168.29"):
    camera_ip = discover_camera(subnet=subnet)
    if camera_ip:
        ports_open = [p for p in [554, 2020, 443, 8800] if check_port(camera_ip, p)]
        return {"camera_ip": camera_ip, "ports_open": ports_open}
    return {"camera_ip": None, "ports_open": []}


@app.post("/api/test")
async def api_test(request: Request):
    import subprocess
    data = await request.json()
    camera_ip = discover_camera(subnet=data.get("subnet", "192.168.29"))
    if not camera_ip:
        return {"success": False, "error": "Camera not found"}
    url = f"rtsp://{data['username']}:{data['password']}@{camera_ip}/stream1"
    try:
        r = subprocess.run(["ffprobe", "-v", "quiet", url], timeout=10)
        return {"success": r.returncode == 0, "camera_ip": camera_ip, "error": "Check credentials" if r.returncode else None}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/save")
async def api_save(request: Request):
    try:
        data = await request.json()
        save_config(data)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_server(host: str = "0.0.0.0", port: int = 8080):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
