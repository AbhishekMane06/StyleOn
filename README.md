# 🎨 StyleOn — Style Studio: Advanced AR Beauty & Try-On

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![MediaPipe](https://img.shields.io/badge/MediaPipe-FaceMesh-green?logo=google)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-red?logo=opencv)
![License](https://img.shields.io/badge/License-MIT-purple)

> **Real-time AR face filter app** powered by MediaPipe FaceMesh (468 landmarks), OpenCV pixel manipulation, and multi-modal control via voice commands and GUI buttons.

</div>

---

## 🚀 Quick Download

💾 **[Click here to download the StyleOn `.exe` Release](https://github.com/AbhishekMane06/StyleOn/releases)**  
</br>*(Note: Make sure to upload your built `.exe` file to the GitHub Releases tab!)*

---

## ✨ Features


### 💄 Virtual Beauty Studio
| Feature | Description |
|---|---|
| **Virtual Lipstick** | Extracts precise lip polygon from 40+ FaceMesh landmarks → alpha-blends color onto actual skin pixels |
| **Skin Smoothing** | Bilateral filter applied only to the face oval (eyes & lips stay sharp) for a flawless beauty filter |
| **Contouring** | Darkens cheekbone hollow regions using landmark coordinates for a sculpted, chiselled look |
| **Warm Filter** | Boosts red/yellow channels → golden hour glow |
| **Cool Filter** | Boosts blue channel, reduces red → crisp cinematic look |
| **Vintage Filter** | Sepia matrix + faded wash → classic retro feel |

### 🕶️ AR Accessories (Head-Tilt Aware)
| Accessory | Description |
|---|---|
| Sunglasses | Aligned to eye center, rotates with face tilt |
| Hat | Sits above head, scales with face width |
| Mask | Aligned to nose/mouth region |
| Dog Ears | Cute dog filter overlay |
| Cat Ears | Whiskers & ears overlay |
| Moustache | Tracks nose-tip landmark precisely |

> All accessories **rotate automatically** to match your head tilt angle, calculated from left/right eye coordinates.

### 🎤 Voice Control (Push-to-Talk)
Click the mic button, speak once, done — no infinite listening loop.

### 🎞️ Film Strip Gallery
- Every captured photo appears instantly as a **scrollable thumbnail** at the bottom
- Click any thumbnail to open the **full-screen photo viewer**
- Navigate between photos with **◀ Prev / Next ▶**
- **⬇ Download** opens a native Windows "Save As" dialog

---

## 🚀 Setup & Run

### 1. Clone the repository
```bash
git clone https://github.com/AbhishekMane06/StyleOn.git
cd StyleOn
```

### 2. Create a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> **Note (Windows):** If `pyaudio` fails to install, run:
> ```bash
> pip install pipwin
> pipwin install pyaudio
> ```

### 4. Run the app
```bash
python main.py
```

---

## 🎤 Voice Commands

Press **🎤 Voice Command** and say:

| Command | Action |
|---|---|
| `"sunglasses"` | Sunglasses accessory |
| `"hat"` / `"cap"` | Hat accessory |
| `"mask"` | Face mask |
| `"dog"` / `"cat"` / `"moustache"` | Animal overlays |
| `"lipstick"` / `"lips"` | Apply red lipstick |
| `"smooth"` / `"beauty"` | Skin smoothing on |
| `"contour"` / `"sculpt"` | Contouring on |
| `"warm"` / `"golden"` | Warm color filter |
| `"cool"` / `"cold"` | Cool color filter |
| `"vintage"` / `"retro"` / `"sepia"` | Vintage filter |
| `"no filter"` / `"normal"` | Remove color filter |
| `"snap"` / `"capture"` / `"photo"` | Take a photo |
| `"clear"` / `"reset"` | Remove all filters |

---

## 📁 Project Structure

```
StyleOn/
├── main.py                    ← Entry point
├── config.py                  ← All constants, paths, color settings
├── requirements.txt
├── README.md
├── .gitignore
│
├── core/
│   ├── face_tracker.py        ← MediaPipe FaceMesh wrapper (468 landmarks)
│   ├── beauty_engine.py       ← Lipstick, smoothing, contouring, color filters
│   └── overlay_engine.py      ← PNG accessory overlay with rotation
│
├── ui/
│   └── app_window.py          ← Tkinter GUI (Film Strip, Photo Viewer, Controls)
│
├── voice/
│   └── voice_controller.py    ← Push-to-talk SpeechRecognition (thread-safe)
│
├── images/                    ← Accessory PNG assets (with alpha channel)
│   ├── specs.png
│   ├── hat.png
│   ├── emask.png
│   ├── dog.png
│   ├── cats.png
│   └── moustache.png
│
└── captures/                  ← Auto-created; stores timestamped photos
```

---

## 🧠 Tech Stack

| Library | Usage |
|---|---|
| **MediaPipe** | FaceMesh — 468 3D facial landmarks with iris refinement |
| **OpenCV** | Webcam capture, bilateral filter, polygon fill, color channel ops |
| **NumPy** | Vectorized alpha blending (100× faster than pixel loops) |
| **Tkinter** | Cross-platform GUI window, film strip, photo viewer popup |
| **Pillow** | Frame conversion from OpenCV BGR to Tkinter-compatible format |
| **SpeechRecognition** | Google Speech API — push-to-talk voice control |




---

## 📩 Contact

📧 Email: **[maneabhishek2003@gmail.com](mailto:maneabhishek2003@gmail.com)**

🔗 Socials:  
**[LinkedIn](https://www.linkedin.com/in/abhishek-mane-9491422b8)** | **[GitHub](https://github.com/AbhishekMane06)**

---

<p align="center">
  <strong>Built with ❤️ using Python · OpenCV · MediaPipe FaceMesh · SpeechRecognition
</strong>
</p>
