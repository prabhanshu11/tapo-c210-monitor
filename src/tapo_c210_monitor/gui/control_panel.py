"""Control panel GUI for TAPO C210 camera operations."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import threading
import time
from pathlib import Path
from typing import Callable


class ControlPanel:
    """Main control panel GUI for camera operations."""

    def __init__(
        self,
        android_ui=None,
        camera=None,
        stream=None,
        sync=None,
    ):
        """Initialize control panel.

        Args:
            android_ui: UIAutomation instance for Android control
            camera: TapoCamera instance for direct API
            stream: StreamCapture instance for RTSP
            sync: RecordingSync instance
        """
        self.android_ui = android_ui
        self.camera = camera
        self.stream = stream
        self.sync = sync

        self.root = tk.Tk()
        self.root.title("TAPO C210 Monitor Control Panel")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2b2b2b")

        self._preview_active = False
        self._preview_thread = None
        self._current_image = None

        self._setup_styles()
        self._create_widgets()

    def _setup_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.theme_use("clam")

        # Dark theme colors
        bg_color = "#2b2b2b"
        fg_color = "#ffffff"
        button_bg = "#404040"
        accent_color = "#00a8e8"

        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color)
        style.configure(
            "TButton",
            background=button_bg,
            foreground=fg_color,
            padding=10,
        )
        style.map("TButton", background=[("active", accent_color)])

        style.configure(
            "Accent.TButton",
            background=accent_color,
            foreground=fg_color,
        )

        style.configure(
            "TLabelframe",
            background=bg_color,
            foreground=fg_color,
        )
        style.configure(
            "TLabelframe.Label",
            background=bg_color,
            foreground=fg_color,
            font=("Helvetica", 10, "bold"),
        )

    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel - Preview and Android screen
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._create_preview_panel(left_panel)
        self._create_android_panel(left_panel)

        # Right panel - Controls
        right_panel = ttk.Frame(main_frame, width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)

        self._create_connection_panel(right_panel)
        self._create_ptz_panel(right_panel)
        self._create_actions_panel(right_panel)
        self._create_sync_panel(right_panel)
        self._create_status_panel(right_panel)

    def _create_preview_panel(self, parent):
        """Create camera preview panel."""
        frame = ttk.LabelFrame(parent, text="Camera Preview (RTSP)")
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Preview canvas
        self.preview_canvas = tk.Canvas(
            frame,
            width=640,
            height=360,
            bg="#1a1a1a",
            highlightthickness=0,
        )
        self.preview_canvas.pack(padx=5, pady=5)

        # Preview controls
        controls = ttk.Frame(frame)
        controls.pack(fill=tk.X, padx=5, pady=5)

        self.preview_btn = ttk.Button(
            controls,
            text="Start Preview",
            command=self._toggle_preview,
        )
        self.preview_btn.pack(side=tk.LEFT, padx=2)

        ttk.Button(
            controls,
            text="Snapshot",
            command=self._take_snapshot,
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            controls,
            text="Record Clip",
            command=self._record_clip,
        ).pack(side=tk.LEFT, padx=2)

        # Stream quality selector
        ttk.Label(controls, text="Quality:").pack(side=tk.LEFT, padx=(10, 2))
        self.quality_var = tk.StringVar(value="hd")
        quality_combo = ttk.Combobox(
            controls,
            textvariable=self.quality_var,
            values=["hd", "sd"],
            width=5,
            state="readonly",
        )
        quality_combo.pack(side=tk.LEFT)

    def _create_android_panel(self, parent):
        """Create Android screen panel."""
        frame = ttk.LabelFrame(parent, text="Android Screen (Tapo App)")
        frame.pack(fill=tk.BOTH, expand=True)

        # Android screen canvas
        self.android_canvas = tk.Canvas(
            frame,
            width=320,
            height=569,  # 16:9 aspect ratio portrait
            bg="#1a1a1a",
            highlightthickness=0,
        )
        self.android_canvas.pack(padx=5, pady=5)

        # Bind click events for touch simulation
        self.android_canvas.bind("<Button-1>", self._on_android_click)

        # Android controls
        controls = ttk.Frame(frame)
        controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            controls,
            text="Refresh",
            command=self._refresh_android_screen,
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            controls,
            text="Launch Tapo",
            command=self._launch_tapo,
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            controls,
            text="Back",
            command=self._android_back,
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            controls,
            text="Home",
            command=self._android_home,
        ).pack(side=tk.LEFT, padx=2)

    def _create_connection_panel(self, parent):
        """Create connection settings panel."""
        frame = ttk.LabelFrame(parent, text="Connection")
        frame.pack(fill=tk.X, pady=(0, 10))

        # Camera IP
        row = ttk.Frame(frame)
        row.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(row, text="Camera IP:").pack(side=tk.LEFT)
        self.camera_ip_var = tk.StringVar(value="192.168.1.100")
        ttk.Entry(row, textvariable=self.camera_ip_var, width=15).pack(side=tk.RIGHT)

        # Username
        row = ttk.Frame(frame)
        row.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(row, text="Username:").pack(side=tk.LEFT)
        self.username_var = tk.StringVar(value="admin")
        ttk.Entry(row, textvariable=self.username_var, width=15).pack(side=tk.RIGHT)

        # Password
        row = ttk.Frame(frame)
        row.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(row, text="Password:").pack(side=tk.LEFT)
        self.password_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.password_var, width=15, show="*").pack(
            side=tk.RIGHT
        )

        # Connect buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            btn_frame,
            text="Connect Camera",
            command=self._connect_camera,
            style="Accent.TButton",
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            btn_frame,
            text="Connect Android",
            command=self._connect_android,
        ).pack(side=tk.LEFT, padx=2)

    def _create_ptz_panel(self, parent):
        """Create PTZ control panel."""
        frame = ttk.LabelFrame(parent, text="PTZ Control")
        frame.pack(fill=tk.X, pady=(0, 10))

        # Direction buttons grid
        ptz_frame = ttk.Frame(frame)
        ptz_frame.pack(pady=10)

        # Up button
        ttk.Button(
            ptz_frame,
            text="^",
            width=5,
            command=lambda: self._move_camera("up"),
        ).grid(row=0, column=1, pady=2)

        # Left button
        ttk.Button(
            ptz_frame,
            text="<",
            width=5,
            command=lambda: self._move_camera("left"),
        ).grid(row=1, column=0, padx=2)

        # Center/Stop button
        ttk.Button(
            ptz_frame,
            text="o",
            width=5,
            command=self._center_camera,
        ).grid(row=1, column=1)

        # Right button
        ttk.Button(
            ptz_frame,
            text=">",
            width=5,
            command=lambda: self._move_camera("right"),
        ).grid(row=1, column=2, padx=2)

        # Down button
        ttk.Button(
            ptz_frame,
            text="v",
            width=5,
            command=lambda: self._move_camera("down"),
        ).grid(row=2, column=1, pady=2)

        # Movement duration slider
        dur_frame = ttk.Frame(frame)
        dur_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(dur_frame, text="Move Duration:").pack(side=tk.LEFT)
        self.move_duration_var = tk.IntVar(value=300)
        ttk.Scale(
            dur_frame,
            from_=100,
            to=2000,
            variable=self.move_duration_var,
            orient=tk.HORIZONTAL,
        ).pack(side=tk.RIGHT, fill=tk.X, expand=True)

    def _create_actions_panel(self, parent):
        """Create camera actions panel."""
        frame = ttk.LabelFrame(parent, text="Camera Actions")
        frame.pack(fill=tk.X, pady=(0, 10))

        # First row
        row1 = ttk.Frame(frame)
        row1.pack(fill=tk.X, padx=5, pady=2)

        ttk.Button(row1, text="Privacy On", command=self._privacy_on).pack(
            side=tk.LEFT, padx=2, fill=tk.X, expand=True
        )
        ttk.Button(row1, text="Privacy Off", command=self._privacy_off).pack(
            side=tk.LEFT, padx=2, fill=tk.X, expand=True
        )

        # Second row
        row2 = ttk.Frame(frame)
        row2.pack(fill=tk.X, padx=5, pady=2)

        ttk.Button(row2, text="LED On", command=self._led_on).pack(
            side=tk.LEFT, padx=2, fill=tk.X, expand=True
        )
        ttk.Button(row2, text="LED Off", command=self._led_off).pack(
            side=tk.LEFT, padx=2, fill=tk.X, expand=True
        )

        # Third row
        row3 = ttk.Frame(frame)
        row3.pack(fill=tk.X, padx=5, pady=2)

        ttk.Button(row3, text="Motion On", command=self._motion_on).pack(
            side=tk.LEFT, padx=2, fill=tk.X, expand=True
        )
        ttk.Button(row3, text="Motion Off", command=self._motion_off).pack(
            side=tk.LEFT, padx=2, fill=tk.X, expand=True
        )

        # Fourth row
        row4 = ttk.Frame(frame)
        row4.pack(fill=tk.X, padx=5, pady=2)

        ttk.Button(row4, text="Get Info", command=self._get_camera_info).pack(
            side=tk.LEFT, padx=2, fill=tk.X, expand=True
        )
        ttk.Button(row4, text="Reboot", command=self._reboot_camera).pack(
            side=tk.LEFT, padx=2, fill=tk.X, expand=True
        )

    def _create_sync_panel(self, parent):
        """Create recording sync panel."""
        frame = ttk.LabelFrame(parent, text="Recording Sync")
        frame.pack(fill=tk.X, pady=(0, 10))

        # Output directory
        dir_frame = ttk.Frame(frame)
        dir_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(dir_frame, text="Output:").pack(side=tk.LEFT)
        self.output_dir_var = tk.StringVar(value="./recordings")
        ttk.Entry(dir_frame, textvariable=self.output_dir_var, width=15).pack(
            side=tk.LEFT, padx=2, fill=tk.X, expand=True
        )
        ttk.Button(dir_frame, text="...", width=3, command=self._browse_output).pack(
            side=tk.RIGHT
        )

        # Sync buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            btn_frame,
            text="Sync Today",
            command=self._sync_today,
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            btn_frame,
            text="Sync Week",
            command=self._sync_week,
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            btn_frame,
            text="Sync Android",
            command=self._sync_android,
        ).pack(side=tk.LEFT, padx=2)

    def _create_status_panel(self, parent):
        """Create status display panel."""
        frame = ttk.LabelFrame(parent, text="Status")
        frame.pack(fill=tk.BOTH, expand=True)

        self.status_text = tk.Text(
            frame,
            height=8,
            bg="#1a1a1a",
            fg="#00ff00",
            font=("Courier", 9),
            wrap=tk.WORD,
        )
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Clear button
        ttk.Button(frame, text="Clear Log", command=self._clear_status).pack(
            pady=(0, 5)
        )

    def log(self, message: str):
        """Log message to status panel."""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)

    def _clear_status(self):
        """Clear status log."""
        self.status_text.delete(1.0, tk.END)

    # --- Connection handlers ---

    def _connect_camera(self):
        """Connect to camera via pytapo."""
        if self.camera:
            if self.camera.connect():
                self.log("Camera connected successfully")
            else:
                self.log("Failed to connect to camera")
        else:
            self.log("Camera module not initialized")

    def _connect_android(self):
        """Connect to Android device."""
        if self.android_ui:
            if self.android_ui.connect():
                self.log("Android device connected")
                self._refresh_android_screen()
            else:
                self.log("Failed to connect to Android")
        else:
            self.log("Android module not initialized")

    # --- Preview handlers ---

    def _toggle_preview(self):
        """Toggle RTSP preview on/off."""
        if self._preview_active:
            self._stop_preview()
        else:
            self._start_preview()

    def _start_preview(self):
        """Start RTSP preview."""
        if not self.stream:
            self.log("Stream not configured")
            return

        self._preview_active = True
        self.preview_btn.configure(text="Stop Preview")
        self._preview_thread = threading.Thread(target=self._preview_loop, daemon=True)
        self._preview_thread.start()
        self.log("Preview started")

    def _stop_preview(self):
        """Stop RTSP preview."""
        self._preview_active = False
        self.preview_btn.configure(text="Start Preview")
        self.log("Preview stopped")

    def _preview_loop(self):
        """Preview update loop running in thread."""
        while self._preview_active:
            try:
                frame = self.stream.get_frame()
                if frame is not None:
                    # Convert to PIL Image
                    import cv2
                    from PIL import Image

                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(rgb)

                    # Resize to fit canvas
                    img = img.resize((640, 360), Image.Resampling.LANCZOS)

                    # Update canvas in main thread
                    self._current_image = ImageTk.PhotoImage(img)
                    self.root.after(0, self._update_preview_canvas)

            except Exception as e:
                self.root.after(0, lambda: self.log(f"Preview error: {e}"))

            time.sleep(0.033)  # ~30 FPS

    def _update_preview_canvas(self):
        """Update preview canvas with current image."""
        if self._current_image:
            self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=self._current_image)

    def _take_snapshot(self):
        """Take and save snapshot."""
        if self.stream:
            path = self.stream.save_snapshot()
            if path:
                self.log(f"Snapshot saved: {path}")
            else:
                self.log("Failed to take snapshot")

    def _record_clip(self):
        """Record video clip."""
        if self.stream:
            path = filedialog.asksaveasfilename(
                defaultextension=".mp4",
                filetypes=[("MP4 files", "*.mp4")],
            )
            if path:
                self.log("Recording 10 second clip...")
                threading.Thread(
                    target=lambda: self._do_record(path),
                    daemon=True,
                ).start()

    def _do_record(self, path: str):
        """Perform recording in background thread."""
        success = self.stream.record_clip(path, duration_seconds=10)
        self.root.after(
            0,
            lambda: self.log(f"Recording {'saved' if success else 'failed'}: {path}"),
        )

    # --- Android handlers ---

    def _refresh_android_screen(self):
        """Refresh Android screen capture."""
        if not self.android_ui:
            return

        try:
            img = self.android_ui.screen.capture()
            # Resize to fit canvas
            img = img.resize((320, 569), Image.Resampling.LANCZOS)
            self._android_image = ImageTk.PhotoImage(img)
            self.android_canvas.create_image(0, 0, anchor=tk.NW, image=self._android_image)
        except Exception as e:
            self.log(f"Android screen error: {e}")

    def _on_android_click(self, event):
        """Handle click on Android screen canvas."""
        if not self.android_ui:
            return

        # Scale coordinates to actual screen size
        canvas_w, canvas_h = 320, 569
        screen_w, screen_h = self.android_ui.screen.screen_size

        x = int(event.x * screen_w / canvas_w)
        y = int(event.y * screen_h / canvas_h)

        self.android_ui.controller.tap(x, y)
        self.log(f"Tapped Android screen at ({x}, {y})")

        # Refresh after tap
        self.root.after(500, self._refresh_android_screen)

    def _launch_tapo(self):
        """Launch Tapo app on Android."""
        if self.android_ui:
            self.android_ui.open_tapo_app()
            self.log("Launched Tapo app")
            self.root.after(2000, self._refresh_android_screen)

    def _android_back(self):
        """Press back button on Android."""
        if self.android_ui:
            self.android_ui.go_back()
            self.root.after(500, self._refresh_android_screen)

    def _android_home(self):
        """Press home button on Android."""
        if self.android_ui:
            self.android_ui.go_home()
            self.root.after(500, self._refresh_android_screen)

    # --- PTZ handlers ---

    def _move_camera(self, direction: str):
        """Move camera in direction."""
        duration = self.move_duration_var.get()

        if self.android_ui:
            self.android_ui.move_camera(direction, duration)
            self.log(f"Moving camera: {direction}")
            self.root.after(duration + 500, self._refresh_android_screen)
        elif self.camera:
            # Use direct API if available
            step_map = {"up": (0, 10), "down": (0, -10), "left": (-10, 0), "right": (10, 0)}
            if direction in step_map:
                x, y = step_map[direction]
                self.camera.move_motor(x, y)
                self.log(f"Moved camera: {direction}")

    def _center_camera(self):
        """Center/home camera position."""
        self.log("Centering camera")
        if self.camera:
            # Go to preset if available
            presets = self.camera.get_presets()
            if presets:
                self.camera.go_to_preset(list(presets.keys())[0])

    # --- Camera action handlers ---

    def _privacy_on(self):
        if self.camera:
            self.camera.set_privacy_mode(True)
            self.log("Privacy mode enabled")

    def _privacy_off(self):
        if self.camera:
            self.camera.set_privacy_mode(False)
            self.log("Privacy mode disabled")

    def _led_on(self):
        if self.camera:
            self.camera.set_led(True)
            self.log("LED enabled")

    def _led_off(self):
        if self.camera:
            self.camera.set_led(False)
            self.log("LED disabled")

    def _motion_on(self):
        if self.camera:
            self.camera.set_motion_detection(True)
            self.log("Motion detection enabled")

    def _motion_off(self):
        if self.camera:
            self.camera.set_motion_detection(False)
            self.log("Motion detection disabled")

    def _get_camera_info(self):
        """Get and display camera info."""
        if self.camera:
            try:
                info = self.camera.get_basic_info()
                self.log(f"Camera info: {info}")
            except Exception as e:
                self.log(f"Error getting info: {e}")

    def _reboot_camera(self):
        """Reboot camera."""
        if self.camera:
            if messagebox.askyesno("Confirm", "Reboot camera?"):
                self.camera.reboot()
                self.log("Camera rebooting...")

    # --- Sync handlers ---

    def _browse_output(self):
        """Browse for output directory."""
        path = filedialog.askdirectory()
        if path:
            self.output_dir_var.set(path)

    def _sync_today(self):
        """Sync today's recordings."""
        self.log("Syncing today's recordings...")
        if self.sync:
            threading.Thread(target=self._do_sync_today, daemon=True).start()

    def _do_sync_today(self):
        """Perform today's sync in background."""
        from datetime import datetime

        today = datetime.now().strftime("%Y%m%d")
        try:
            files = self.sync.sync_date(today)
            self.root.after(0, lambda: self.log(f"Synced {len(files)} recordings"))
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Sync error: {e}"))

    def _sync_week(self):
        """Sync last week's recordings."""
        self.log("Syncing last 7 days...")
        if self.sync:
            threading.Thread(target=self._do_sync_week, daemon=True).start()

    def _do_sync_week(self):
        """Perform week sync in background."""
        try:
            result = self.sync.sync_recent(days=7)
            total = sum(len(files) for files in result.values())
            self.root.after(0, lambda: self.log(f"Synced {total} recordings from {len(result)} days"))
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Sync error: {e}"))

    def _sync_android(self):
        """Sync media from Android device."""
        self.log("Syncing from Android...")
        if self.android_ui:
            from .file_transfer import FileTransfer

            transfer = FileTransfer(self.android_ui.controller)
            threading.Thread(
                target=lambda: self._do_android_sync(transfer),
                daemon=True,
            ).start()

    def _do_android_sync(self, transfer):
        """Perform Android sync in background."""
        try:
            output_dir = self.output_dir_var.get()
            files = transfer.sync_tapo_media(output_dir)
            self.root.after(0, lambda: self.log(f"Synced {len(files)} files from Android"))
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Android sync error: {e}"))

    def run(self):
        """Start the GUI main loop."""
        self.log("Control panel initialized")
        self.root.mainloop()
