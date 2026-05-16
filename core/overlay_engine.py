import cv2
import numpy as np

class OverlayEngine:
    def __init__(self):
        self.accessory_cache = {}

    def load_accessory(self, path):
        if not path:
            return None
        if path not in self.accessory_cache:
            self.accessory_cache[path] = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        return self.accessory_cache[path]

    def overlay_image_fast(self, bg, overlay, x, y):
        """Vectorized alpha blending"""
        oh, ow = overlay.shape[:2]
        x1, y1 = max(x, 0), max(y, 0)
        x2, y2 = min(x + ow, bg.shape[1]), min(y + oh, bg.shape[0])
        
        if x1 >= x2 or y1 >= y2:
            return
            
        ox1, oy1 = x1 - x, y1 - y
        ox2, oy2 = ox1 + (x2 - x1), oy1 + (y2 - y1)
        
        alpha = overlay[oy1:oy2, ox1:ox2, 3:4].astype(np.float32) / 255.0
        bg_sl = bg[y1:y2, x1:x2].astype(np.float32)
        ov_sl = overlay[oy1:oy2, ox1:ox2, :3].astype(np.float32)
        
        bg[y1:y2, x1:x2] = ((1 - alpha) * bg_sl + alpha * ov_sl).astype(np.uint8)

    def rotate_image(self, image, angle):
        """Rotates an image with alpha channel."""
        if angle == 0:
            return image
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Calculate new bounding box to prevent cropping
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        nW = int((h * sin) + (w * cos))
        nH = int((h * cos) + (w * sin))
        
        M[0, 2] += (nW / 2) - center[0]
        M[1, 2] += (nH / 2) - center[1]
        
        return cv2.warpAffine(image, M, (nW, nH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))

    def apply_accessory(self, frame, face, accessory_path, accessory_name):
        if not accessory_path or accessory_name == "None":
            return
            
        accessory = self.load_accessory(accessory_path)
        if accessory is None:
            return
            
        bbox = face["bbox"]
        angle = face["angle"]
        
        # Rotate the accessory
        rotated_acc = self.rotate_image(accessory, -angle)
        
        # Determine position and scale
        x, y, w, h = bbox
        ar = rotated_acc.shape[1] / rotated_acc.shape[0]
        
        left_eye = face["left_eye"]
        right_eye = face["right_eye"]
        cx = (left_eye[0] + right_eye[0]) // 2
        cy = (left_eye[1] + right_eye[1]) // 2
        
        def dims(scale):
            nw = int(scale * w)
            return max(1, nw), max(1, int(nw / ar))
            
        if accessory_name == "Sunglasses":
            nw, nh = dims(1.0)
            px = cx - nw // 2
            py = cy - nh // 2
        elif accessory_name == "Hat":
            nw, nh = dims(1.5)
            px = x - int(0.25 * w)
            py = y - int(0.9 * nh)
        elif accessory_name == "Mask":
            nw, nh = dims(1.0)
            px = cx - nw // 2
            py = cy - int(0.6 * nh)
        elif accessory_name == "Dog":
            nw, nh = dims(1.2)
            px = cx - nw // 2
            py = cy - nh // 2
        elif accessory_name == "Cat":
            nw, nh = dims(0.6)
            px = cx - nw // 2
            py = cy - nh // 2
        elif accessory_name == "Moustache":
            nw, nh = dims(0.6)
            nose = face["nose_tip"]
            px = nose[0] - nw // 2
            py = nose[1] - int(0.3 * nh)
        else:
            return
            
        resized = cv2.resize(rotated_acc, (nw, nh), interpolation=cv2.INTER_AREA)
        self.overlay_image_fast(frame, resized, px, py)
