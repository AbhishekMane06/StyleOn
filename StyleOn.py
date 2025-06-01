import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
import threading
import speech_recognition as sr
import mediapipe as mp

# Import face detection module from MediaPipe
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

accessories = {
    "Sunglasses": "images/specs.png",
    "Hat": "images/hat.png",
    "Mask": "images/emask.png",
    "Dog": "images/dog.png",
    "Cat": "images/cats.png",
    "Moustache": "images/moustache.png"
}

selected_accessory = "Sunglasses"

def load_accessory(name):
    img = cv2.imread(accessories[name], cv2.IMREAD_UNCHANGED)
    return img

current_accessory = load_accessory(selected_accessory)

def detect_face(image):
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_detection.process(rgb_image)
    
    if results.detections:
        for detection in results.detections:
            bboxC = detection.location_data.relative_bounding_box
            h, w, _ = image.shape
            x, y, w, h = int(bboxC.xmin * w), int(bboxC.ymin * h), int(bboxC.width * w), int(bboxC.height * h)
            left_eye = (x + int(0.3 * w), y + int(0.35 * h))
            right_eye = (x + int(0.7 * w), y + int(0.35 * h))
            nose = (x + int(0.5 * w), y + int(0.55 * h))
            return (x, y, w, h), left_eye, right_eye, nose
    return None

def overlay_accessory(img, accessory, face, left, right, nose):
    x, y, w, h = face
    aspect_ratio = accessory.shape[1] / accessory.shape[0]

    # Calculate the center point between both eyes
    eyes_center = ((left[0] + right[0]) // 2, (left[1] + right[1]) // 2)
 
    # Positioning based on accessory type
    if selected_accessory == "Sunglasses":
        width = int(1 * w) 
        height = int(width / aspect_ratio)  

        pos_x = eyes_center[0] - int(0.5 * width)  
        pos_y = eyes_center[1] - int(0.5 * height)  

    elif selected_accessory == "Hat":
        width = int(1.5 * w)
        height = int(width / aspect_ratio)

        pos_x, pos_y = x - int(0.25 * w), y - int(0.9 * height)

    elif selected_accessory == "Mask":
        width = int(1 * w) 
        height = int(width / aspect_ratio)  

        pos_x = eyes_center[0] - int(0.5 * width)  
        pos_y = eyes_center[1] - int(0.6 * height) 
        
    elif selected_accessory == "Dog":
        width = int(1.2 * w)  
        height = int(width / aspect_ratio)  

        pos_x = eyes_center[0] - int(0.5 * width)  
        pos_y = eyes_center[1] - int(0.5 * height) 

    elif selected_accessory == "Cat":
        width = int(0.6 * w)  
        height = int(width / aspect_ratio)  

        pos_x = eyes_center[0] - int(0.5 * width)  
        pos_y = eyes_center[1] - int(0.5 * height) 

    elif selected_accessory == "Moustache":
        width = int(0.6 * w)  
        height = int(width / aspect_ratio)
    
        pos_x = nose[0] - int(0.5 * width) 
        pos_y = nose[1] - int(0.3 * height)  


    resized_accessory = cv2.resize(accessory, (width, height), interpolation=cv2.INTER_AREA)
    overlay_image(img, resized_accessory, pos_x, pos_y)

def overlay_image(background, overlay, x, y):
    for i in range(overlay.shape[0]):
        for j in range(overlay.shape[1]):
            if 0 <= y + i < background.shape[0] and 0 <= x + j < background.shape[1]:
                if overlay[i, j, 3] > 0:
                    background[y + i, x + j] = overlay[i, j, :3]

def change_accessory(name):
    global selected_accessory, current_accessory
    selected_accessory = name
    current_accessory = load_accessory(name)
    accessory_label.config(text=f"🕶 Accessory: {name}", fg="cyan")

    
def capture_frame():
    ret, frame = cap.read()
    if ret:
        frame = cv2.flip(frame, 1)  
        landmarks = detect_face(frame)

        if landmarks:
            face, left_eye, right_eye, nose = landmarks
            overlay_accessory(frame, current_accessory, face, left_eye, right_eye, nose)

        cv2.imwrite("captured_frame.jpg", frame)
        accessory_label.config(text="📸 Photo Captured!", fg="blue")
        print("Image saved as 'captured_frame.jpg'")

def video_loop():
    ret, frame = cap.read()
    if ret:
        frame = cv2.flip(frame, 1)
        landmarks = detect_face(frame)
        if landmarks:
            face, left_eye, right_eye, nose = landmarks
            overlay_accessory(frame, current_accessory, face, left_eye, right_eye, nose)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)
    video_label.after(10, video_loop)

def recognize_speech():
    accessory_label.config(text="🎤 Listening...", fg="yellow")
    root.update_idletasks()

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 100  # Lower energy threshold for better detection
    recognizer.dynamic_energy_threshold = True  # Auto-adjust for noise

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Reduce background noise
        try:
            print("Listening...")
            audio = recognizer.listen(source, timeout=15, phrase_time_limit=8)
            command = recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")

            if "hat" in command:
                change_accessory("Hat")
            elif "sunglasses" in command:
                change_accessory("Sunglasses")
            elif "apply" in command:
                change_accessory("Mask")
            elif "dog" in command:
                change_accessory("Dog")
            elif "cat" in command:
                change_accessory("Cat")
            elif "moustache" in command:
                change_accessory("Moustache")
            elif "snap" in command or "take a picture" in command:
                capture_frame()
        
        except sr.UnknownValueError:
            accessory_label.config(text="❌ Could not understand. Try again!", fg="red")
        except sr.RequestError:
            accessory_label.config(text="🌐 Speech service unavailable!", fg="red")

    root.update_idletasks()

            
def start_speech_recognition():
    threading.Thread(target=recognize_speech, daemon=True).start()

# GUI setup
root = tk.Tk()
root.title("Virtual Style-On")
root.geometry("900x750")
root.configure(bg="#222")

video_label = tk.Label(root, bg="#222")
video_label.pack(pady=10)
accessory_label = tk.Label(root, text="🕶 Accessory: Sunglasses", fg="cyan", font=("Arial", 14, "bold"), bg="#222")
accessory_label.pack(pady=10)

def create_button(text, command):
    return tk.Button(root, text=text, command=command, font=("Arial", 12, "bold"), fg="white", bg="#333", activebackground="lime", activeforeground="black", bd=2, relief="ridge", padx=15, pady=5, cursor="hand2")

create_button("🎤 Voice Command", start_speech_recognition).pack(pady=10)
create_button("📸 Capture", capture_frame).pack(pady=10)

cap = cv2.VideoCapture(0)
video_loop()

root.mainloop()
cap.release()
cv2.destroyAllWindows()
