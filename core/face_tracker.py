import cv2
import mediapipe as mp
import numpy as np

class FaceTracker:
    def __init__(self, max_faces=1):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=max_faces,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
    def process(self, frame):
        """
        Processes the frame and returns a list of faces.
        Each face is a dictionary containing landmark points and bounding box data.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        ih, iw = frame.shape[:2]
        faces = []
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Convert normalized landmarks to pixel coordinates
                landmarks = []
                for lm in face_landmarks.landmark:
                    x, y = int(lm.x * iw), int(lm.y * ih)
                    landmarks.append((x, y))
                
                # Get bounding box around the face
                xs = [pt[0] for pt in landmarks]
                ys = [pt[1] for pt in landmarks]
                bbox = (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
                
                # Calculate face tilt angle using eyes
                # Left eye center (index 468 in refined, or 33 for outer), let's use 33 and 263
                left_eye = landmarks[33]
                right_eye = landmarks[263]
                
                dy = right_eye[1] - left_eye[1]
                dx = right_eye[0] - left_eye[0]
                angle = np.degrees(np.arctan2(dy, dx))
                
                faces.append({
                    "landmarks": landmarks,
                    "bbox": bbox,
                    "angle": angle,
                    "left_eye": left_eye,
                    "right_eye": right_eye,
                    "nose_tip": landmarks[1],
                    "chin": landmarks[152]
                })
                
        return faces

    def close(self):
        self.face_mesh.close()
