import tkinter as tk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
import time
import os
import shutil
from datetime import datetime

class StyleStudioApp:
    def __init__(self, root, config, face_tracker, beauty_engine, overlay_engine, voice_controller):
        self.root = root
        self.root.title("Style Studio: Advanced AR Try-On")
        self.root.geometry("1080x900")
        self.root.configure(bg="#121212")

        self.config = config
        self.face_tracker = face_tracker
        self.beauty_engine = beauty_engine
        self.overlay_engine = overlay_engine
        self.voice_controller = voice_controller
        self.voice_controller.callback = self.voice_callback

        # State
        self.current_accessory   = "None"
        self.current_lipstick    = "None"
        self.current_color_filter = "None"   # Warm / Cool / Vintage / None
        self.contouring_on       = False
        self.smoothing_intensity = 0.0
        self.needs_capture       = False

        # Flash state
        self.flash_time   = 0
        self.frozen_frame = None

        # Photo records: list of {"path": ..., "thumb_img": PIL Image}
        self.photos = []

        self.cap = cv2.VideoCapture(0)

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self._start_video_loop()

    # ──────────────────────────────────────────────────────────────────────────
    # UI BUILD
    # ──────────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Status bar ─────────────────────────────────────────────────────
        self.status_label = tk.Label(
            self.root, text="✨ Welcome to Style Studio",
            fg="cyan", bg="#121212", font=("Helvetica", 15, "bold")
        )
        self.status_label.pack(pady=(10, 4))

        # ── Video feed ─────────────────────────────────────────────────────
        self.video_container = tk.Frame(self.root, bg="#222", bd=2, relief="ridge")
        self.video_container.pack(pady=4)
        self.video_label = tk.Label(self.video_container, bg="#000")
        self.video_label.pack()

        # ── Row 1: Accessory + Beauty controls ────────────────────────────
        controls_frame = tk.Frame(self.root, bg="#121212")
        controls_frame.pack(pady=(6, 2), fill=tk.X, padx=20)

        # Accessories
        acc_frame = tk.Frame(controls_frame, bg="#121212")
        acc_frame.pack(side=tk.LEFT, padx=6)
        tk.Label(acc_frame, text="Accessories", fg="#aaa", bg="#121212",
                 font=("Helvetica", 9)).pack()
        for acc in ["None", "Sunglasses", "Hat", "Mask", "Dog", "Cat", "Moustache"]:
            tk.Button(
                acc_frame, text=acc, width=9,
                command=lambda a=acc: self.set_state("accessory", a),
                bg="#2a2a2a", fg="white", activebackground="#444",
                relief="flat", cursor="hand2"
            ).pack(side=tk.LEFT, padx=2)

        # Beauty
        beauty_frame = tk.Frame(controls_frame, bg="#121212")
        beauty_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(beauty_frame, text="Beauty", fg="#aaa", bg="#121212",
                 font=("Helvetica", 9)).pack()
        for label, cmd in [
            ("💄 Red Lips",    lambda: self.set_state("lipstick", "Classic Red")),
            ("🔲 Contour",     lambda: self.set_state("contouring", True)),
            ("✨ Smooth Skin", lambda: self.set_state("smoothing", 0.6)),
            ("❌ Clear",       self.clear_beauty),
        ]:
            tk.Button(
                beauty_frame, text=label, command=cmd,
                bg="#2a2a2a", fg="white", activebackground="#555",
                relief="flat", cursor="hand2"
            ).pack(side=tk.LEFT, padx=2)

        # Color Filters row
        filter_frame = tk.Frame(controls_frame, bg="#121212")
        filter_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(filter_frame, text="Color Filter", fg="#aaa", bg="#121212",
                 font=("Helvetica", 9)).pack()
        for fname, color in [("🌅 Warm", "#ff9966"), ("❄ Cool", "#66ccff"),
                             ("📷 Vintage", "#c9a96e"), ("⬛ None", "white")]:
            filter_key = fname.split()[-1]  # extract "Warm", "Cool", "Vintage", "None"
            tk.Button(
                filter_frame, text=fname,
                command=lambda k=filter_key: self.set_state("color_filter", k),
                bg="#2a2a2a", fg=color, activebackground="#555",
                relief="flat", cursor="hand2"
            ).pack(side=tk.LEFT, padx=2)

        # ── Row 2: Action buttons on their own dedicated row ───────────────
        action_row = tk.Frame(self.root, bg="#121212")
        action_row.pack(pady=(2, 6), fill=tk.X, padx=20)

        tk.Button(
            action_row, text="🎤 Voice Command",
            command=self.voice_controller.listen,
            bg="#a855f7", fg="white", font=("Arial", 10, "bold"),
            relief="flat", cursor="hand2", padx=12, pady=4
        ).pack(side=tk.LEFT, padx=6)
        tk.Button(
            action_row, text="📸 Capture",
            command=self.capture_photo,
            bg="#00ff88", fg="#000", font=("Arial", 12, "bold"),
            relief="flat", cursor="hand2", padx=16, pady=4
        ).pack(side=tk.LEFT, padx=6)

        # ── Film Strip ─────────────────────────────────────────────────────
        strip_header = tk.Frame(self.root, bg="#121212")
        strip_header.pack(fill=tk.X, padx=20, pady=(10, 2))
        tk.Label(strip_header, text="🎞  Film Strip",
                 fg="white", bg="#121212", font=("Helvetica", 11, "bold")).pack(side=tk.LEFT)

        # Outer frame holds canvas + scrollbar
        strip_outer = tk.Frame(self.root, bg="#1a1a1a", height=148)
        strip_outer.pack(fill=tk.X, padx=20, pady=(0, 10))
        strip_outer.pack_propagate(False)

        # Horizontal scrollbar
        self.strip_scrollbar = tk.Scrollbar(strip_outer, orient=tk.HORIZONTAL, bg="#333")
        self.strip_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Canvas for the strip
        self.strip_canvas = tk.Canvas(
            strip_outer, bg="#1a1a1a", height=130,
            highlightthickness=0,
            xscrollcommand=self.strip_scrollbar.set
        )
        self.strip_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.strip_scrollbar.config(command=self.strip_canvas.xview)

        # Inner frame that lives inside the canvas
        self.film_strip = tk.Frame(self.strip_canvas, bg="#1a1a1a")
        self._strip_window = self.strip_canvas.create_window(
            (0, 0), window=self.film_strip, anchor="nw"
        )

        # Bind resize to keep scroll region updated
        self.film_strip.bind("<Configure>", self._on_strip_resize)

        # Mouse wheel → horizontal scroll on Windows
        self.strip_canvas.bind("<MouseWheel>",  self._on_mouse_wheel)
        self.strip_canvas.bind("<Shift-MouseWheel>", self._on_mouse_wheel)

    # ──────────────────────────────────────────────────────────────────────────
    # FILM STRIP HELPERS
    # ──────────────────────────────────────────────────────────────────────────
    def _on_strip_resize(self, event):
        self.strip_canvas.configure(scrollregion=self.strip_canvas.bbox("all"))

    def _on_mouse_wheel(self, event):
        self.strip_canvas.xview_scroll(-1 * (event.delta // 120), "units")

    # ──────────────────────────────────────────────────────────────────────────
    # STATE MANAGEMENT
    # ──────────────────────────────────────────────────────────────────────────
    def set_state(self, key, value):
        if key == "accessory":     self.current_accessory    = value
        elif key == "lipstick":    self.current_lipstick     = value
        elif key == "color_filter":self.current_color_filter = value
        elif key == "contouring":  self.contouring_on        = bool(value)
        elif key == "smoothing":   self.smoothing_intensity  = value

    def clear_beauty(self):
        self.current_lipstick     = "None"
        self.current_color_filter = "None"
        self.contouring_on        = False
        self.smoothing_intensity  = 0.0

    def voice_callback(self, msg, color, actions=None):
        # Voice runs on a background thread — MUST use root.after() to
        # safely update Tkinter widgets and state from the main thread.
        self.root.after(0, lambda: self._apply_voice_result(msg, color, actions))

    def _apply_voice_result(self, msg, color, actions):
        """Called on the main thread — safe to touch all Tkinter state."""
        self.status_label.config(text=msg, fg=color)
        if actions:
            for k, v in actions.items():
                if k == "action" and v == "snap":
                    self.capture_photo()
                else:
                    self.set_state(k, v)

    # ──────────────────────────────────────────────────────────────────────────
    # CAPTURE + FILM STRIP
    # ──────────────────────────────────────────────────────────────────────────
    def capture_photo(self):
        self.needs_capture = True

    def _add_to_film_strip(self, frame_bgr):
        # Save full-res image
        ts    = datetime.now()
        fname = os.path.join(self.config.CAPTURES_DIR,
                             f"cap_{ts.strftime('%Y%m%d_%H%M%S')}.jpg")
        cv2.imwrite(fname, frame_bgr)

        # Build thumbnail PIL image
        img_rgb   = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        pil_full  = Image.fromarray(img_rgb)      # keep full-res for viewer
        pil_thumb = pil_full.copy()
        pil_thumb.thumbnail((150, 112))
        tk_thumb  = ImageTk.PhotoImage(pil_thumb)

        # Record
        record = {"path": fname, "pil_full": pil_full}
        idx    = len(self.photos)
        self.photos.append(record)

        # Thumbnail label with click binding
        card = tk.Frame(self.film_strip, bg="#1a1a1a", padx=4, pady=6)
        card.pack(side=tk.LEFT, padx=5)

        lbl = tk.Label(card, image=tk_thumb, bg="#000",
                       bd=2, relief="solid", cursor="hand2")
        lbl.image = tk_thumb          # prevent GC
        lbl.pack()
        lbl.bind("<Button-1>", lambda e, i=idx: self._open_photo_viewer(i))
        card.bind("<Button-1>", lambda e, i=idx: self._open_photo_viewer(i))

        # Scroll all the way right so newest photo is visible
        self.root.after(100, lambda: self.strip_canvas.xview_moveto(1.0))

        self.status_label.config(
            text=f"📸 Photo {len(self.photos)} saved! Click to view.", fg="#00ff88"
        )

    # ──────────────────────────────────────────────────────────────────────────
    # PHOTO VIEWER (full-screen overlay)
    # ──────────────────────────────────────────────────────────────────────────
    def _open_photo_viewer(self, index):
        record = self.photos[index]

        # Create a top-level modal window
        viewer = tk.Toplevel(self.root)
        viewer.title(f"Photo {index + 1}")
        viewer.configure(bg="#0d0d12")
        viewer.grab_set()               # block interaction with main window
        viewer.resizable(False, False)

        # Center the viewer on screen
        vw, vh = 760, 620
        sx = self.root.winfo_x() + (self.root.winfo_width()  - vw) // 2
        sy = self.root.winfo_y() + (self.root.winfo_height() - vh) // 2
        viewer.geometry(f"{vw}x{vh}+{sx}+{sy}")

        # ── Title bar ──────────────────────────────────────────────────────
        title_bar = tk.Frame(viewer, bg="#1a1a2a", pady=8)
        title_bar.pack(fill=tk.X)
        tk.Label(
            title_bar, text=f"📷  Photo {index + 1} of {len(self.photos)}",
            fg="white", bg="#1a1a2a", font=("Helvetica", 13, "bold")
        ).pack(side=tk.LEFT, padx=16)

        # Close (X) button top-right
        tk.Button(
            title_bar, text="  ✕  Close  ", command=viewer.destroy,
            bg="#e53e3e", fg="white", font=("Arial", 10, "bold"),
            relief="flat", cursor="hand2", padx=6
        ).pack(side=tk.RIGHT, padx=12)

        # ── Photo display ──────────────────────────────────────────────────
        photo_frame = tk.Frame(viewer, bg="#0d0d12")
        photo_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=12)

        pil_view = record["pil_full"].copy()
        pil_view.thumbnail((720, 480))
        tk_view = ImageTk.PhotoImage(pil_view)

        photo_lbl = tk.Label(photo_frame, image=tk_view, bg="#0d0d12")
        photo_lbl.image = tk_view
        photo_lbl.pack(expand=True)

        # ── Bottom action bar ──────────────────────────────────────────────
        action_bar = tk.Frame(viewer, bg="#1a1a2a", pady=10)
        action_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # File info
        fname_short = os.path.basename(record["path"])
        tk.Label(
            action_bar, text=f"💾  {fname_short}",
            fg="#888", bg="#1a1a2a", font=("Helvetica", 9)
        ).pack(side=tk.LEFT, padx=14)

        # Download button → opens native Save As dialog
        def download():
            fname_short = os.path.basename(record["path"])
            # Open the native Windows Save As dialog
            save_path = filedialog.asksaveasfilename(
                parent=viewer,
                title="Save Photo As",
                initialfile=fname_short,
                defaultextension=".jpg",
                filetypes=[("JPEG Image", "*.jpg"), ("PNG Image", "*.png"), ("All Files", "*.*")]
            )
            if not save_path:   # user cancelled
                return
            shutil.copy2(record["path"], save_path)
            self.status_label.config(
                text=f"✅ Saved: {os.path.basename(save_path)}", fg="#00ff88"
            )
            viewer.destroy()

        tk.Button(
            action_bar, text="⬇ Download",
            command=download,
            bg="#00d4ff", fg="#000", font=("Arial", 11, "bold"),
            relief="flat", cursor="hand2", padx=12, pady=4
        ).pack(side=tk.RIGHT, padx=14)

        # Navigate between photos
        nav_frame = tk.Frame(action_bar, bg="#1a1a2a")
        nav_frame.pack(side=tk.RIGHT, padx=8)
        if index > 0:
            tk.Button(
                nav_frame, text="◀  Prev",
                command=lambda: [viewer.destroy(), self._open_photo_viewer(index - 1)],
                bg="#333", fg="white", relief="flat", cursor="hand2"
            ).pack(side=tk.LEFT, padx=4)
        if index < len(self.photos) - 1:
            tk.Button(
                nav_frame, text="Next  ▶",
                command=lambda: [viewer.destroy(), self._open_photo_viewer(index + 1)],
                bg="#333", fg="white", relief="flat", cursor="hand2"
            ).pack(side=tk.LEFT, padx=4)

    # ──────────────────────────────────────────────────────────────────────────
    # VIDEO LOOP
    # ──────────────────────────────────────────────────────────────────────────
    def _start_video_loop(self):
        self._update_frame()

    def _update_frame(self):
        now = time.time()

        # Flash / freeze handling
        if self.flash_time > 0:
            elapsed = now - self.flash_time
            if elapsed < 0.08:
                img   = Image.new('RGB', (640, 480), color='white')
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
                self.root.after(15, self._update_frame)
                return
            elif elapsed < 1.0:
                if self.frozen_frame is not None:
                    imgtk = ImageTk.PhotoImage(image=self.frozen_frame)
                    self.video_label.imgtk = imgtk
                    self.video_label.configure(image=imgtk)
                self.root.after(15, self._update_frame)
                return
            else:
                self.flash_time   = 0
                self.frozen_frame = None

        ret, frame = self.cap.read()
        if ret:
            frame         = cv2.flip(frame, 1)
            display_frame = frame.copy()

            faces = self.face_tracker.process(display_frame)
            for face in faces:
                if self.smoothing_intensity > 0:
                    display_frame = self.beauty_engine.apply_skin_smoothing(
                        display_frame, face, self.smoothing_intensity)
                if self.contouring_on:
                    display_frame = self.beauty_engine.apply_contouring(display_frame, face)
                if self.current_lipstick != "None":
                    display_frame = self.beauty_engine.apply_lipstick(
                        display_frame, face, self.config.LIPSTICK_COLORS[self.current_lipstick])
                acc_path = self.config.ACCESSORIES.get(self.current_accessory)
                self.overlay_engine.apply_accessory(
                    display_frame, face, acc_path, self.current_accessory)

            # Full-frame color filter (applied after face effects)
            if self.current_color_filter == "Warm":
                display_frame = self.beauty_engine.apply_warm_filter(display_frame)
            elif self.current_color_filter == "Cool":
                display_frame = self.beauty_engine.apply_cool_filter(display_frame)
            elif self.current_color_filter == "Vintage":
                display_frame = self.beauty_engine.apply_vintage_filter(display_frame)

            cv2image = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            pil_img  = Image.fromarray(cv2image)

            if self.needs_capture:
                self.needs_capture = False
                self.flash_time    = time.time()
                self.frozen_frame  = pil_img
                self._add_to_film_strip(display_frame)
            else:
                imgtk = ImageTk.PhotoImage(image=pil_img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)

        self.root.after(15, self._update_frame)

    # ──────────────────────────────────────────────────────────────────────────
    # CLEANUP
    # ──────────────────────────────────────────────────────────────────────────
    def on_close(self):
        self.voice_controller.stop()
        self.face_tracker.close()
        self.cap.release()
        self.root.destroy()
