import os
import sys

# Base paths
if getattr(sys, 'frozen', False):
    # If the app is run from a bundle (PyInstaller .exe)
    BASE_DIR = sys._MEIPASS
else:
    # If the app is run from a normal Python environment
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# We want the captures folder to be next to the EXE, not inside the temp folder
EXE_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else BASE_DIR
CAPTURES_DIR = os.path.join(EXE_DIR, "captures")
os.makedirs(CAPTURES_DIR, exist_ok=True)

# Accessories Data
ACCESSORIES = {
    "None": None,
    "Sunglasses": os.path.join(BASE_DIR, "images", "specs.png"),
    "Hat": os.path.join(BASE_DIR, "images", "hat.png"),
    "Mask": os.path.join(BASE_DIR, "images", "emask.png"),
    "Dog": os.path.join(BASE_DIR, "images", "dog.png"),
    "Cat": os.path.join(BASE_DIR, "images", "cats.png"),
    "Moustache": os.path.join(BASE_DIR, "images", "moustache.png")
}

# Style Metadata for Gallery
STYLE_META = {
    "None":       {"label": "Natural Beauty",     "color": "#9ca3af", "base": 80},
    "Sunglasses": {"label": "Fashion Forward",    "color": "#00d4ff", "base": 91},
    "Hat":        {"label": "Street Style",       "color": "#ff6b35", "base": 87},
    "Mask":       {"label": "Urban Cool",         "color": "#a855f7", "base": 84},
    "Dog":        {"label": "Playful Vibes",      "color": "#fbbf24", "base": 79},
    "Cat":        {"label": "Mysteriously Chic",  "color": "#f472b6", "base": 85},
    "Moustache":  {"label": "Classic Charm",      "color": "#34d399", "base": 89},
}

# Beauty Settings
LIPSTICK_COLORS = {
    "None": None,
    "Classic Red": (0, 0, 180),       # BGR format
    "Pink Gloss": (147, 105, 255),
    "Vampy Plum": (50, 0, 80)
}

EYE_COLORS = {
    "None": None,
    "Sapphire Blue": (255, 100, 0),
    "Emerald Green": (0, 200, 0),
    "Amethyst Purple": (200, 0, 150)
}

# Color Filters (full-frame)
COLOR_FILTERS = ["None", "Warm", "Cool", "Vintage"]
