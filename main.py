import tkinter as tk
import config
from core.face_tracker import FaceTracker
from core.beauty_engine import BeautyEngine
from core.overlay_engine import OverlayEngine
from voice.voice_controller import VoiceController
from ui.app_window import StyleStudioApp

def main():
    root = tk.Tk()
    
    # Initialize Core Components
    face_tracker = FaceTracker()
    beauty_engine = BeautyEngine()
    overlay_engine = OverlayEngine()
    voice_controller = VoiceController(callback=None)
    
    # Initialize UI
    app = StyleStudioApp(
        root=root,
        config=config,
        face_tracker=face_tracker,
        beauty_engine=beauty_engine,
        overlay_engine=overlay_engine,
        voice_controller=voice_controller
    )
    
    root.mainloop()

if __name__ == "__main__":
    main()
