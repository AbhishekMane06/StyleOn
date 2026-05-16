import cv2
import numpy as np

class BeautyEngine:
    def __init__(self):
        # Lip contour indices from FaceMesh
        self.LIPS_INDICES = [
            61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 78,
            191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 291, 409, 270, 269, 267, 0, 37, 39, 40, 185, 61
        ]
        self.LEFT_EYE_INDICES = [
            33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246
        ]
        self.RIGHT_EYE_INDICES = [
            362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398
        ]
        self.FACE_OVAL_INDICES = [
            10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148,
            176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109
        ]
        # Cheekbone contour points for contouring shadow
        self.LEFT_CHEEKBONE  = [234, 227, 116, 123, 147, 187, 207, 206, 205, 36, 101, 119]
        self.RIGHT_CHEEKBONE = [454, 447, 345, 352, 376, 411, 427, 426, 425, 266, 330, 348]

    # ── Lipstick ─────────────────────────────────────────────────────────────
    def apply_lipstick(self, frame, face, color, alpha=0.4):
        """Applies a color tint to the lips using alpha blending."""
        if not color:
            return frame

        landmarks = face["landmarks"]
        lip_pts   = np.array([landmarks[i] for i in self.LIPS_INDICES], dtype=np.int32)

        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [lip_pts], 255)
        mask = cv2.GaussianBlur(mask, (7, 7), 0)

        colored = np.zeros_like(frame)
        colored[:] = color

        w = (mask / 255.0) * alpha
        w = np.expand_dims(w, axis=-1)
        return ((1 - w) * frame + w * colored).astype(np.uint8)

    # ── Skin Smoothing ────────────────────────────────────────────────────────
    def apply_skin_smoothing(self, frame, face, intensity=0.5):
        """Bilateral filter on the face oval, keeping eyes & lips sharp."""
        if intensity <= 0:
            return frame

        landmarks = face["landmarks"]
        face_pts  = np.array([landmarks[i] for i in self.FACE_OVAL_INDICES], dtype=np.int32)
        lip_pts   = np.array([landmarks[i] for i in self.LIPS_INDICES],       dtype=np.int32)
        l_eye_pts = np.array([landmarks[i] for i in self.LEFT_EYE_INDICES],   dtype=np.int32)
        r_eye_pts = np.array([landmarks[i] for i in self.RIGHT_EYE_INDICES],  dtype=np.int32)

        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [face_pts], 255)
        cv2.fillPoly(mask, [lip_pts],   0)
        cv2.fillPoly(mask, [l_eye_pts], 0)
        cv2.fillPoly(mask, [r_eye_pts], 0)
        mask = cv2.GaussianBlur(mask, (15, 15), 0)

        smoothed = cv2.bilateralFilter(frame, 15, 75, 75)

        w = (mask / 255.0) * intensity
        w = np.expand_dims(w, axis=-1)
        return ((1 - w) * frame + w * smoothed).astype(np.uint8)

    # ── Contouring ────────────────────────────────────────────────────────────
    def apply_contouring(self, frame, face, intensity=0.45):
        """Darkens cheekbone hollows to sculpt the face."""
        landmarks  = face["landmarks"]
        l_pts = np.array([landmarks[i] for i in self.LEFT_CHEEKBONE],  dtype=np.int32)
        r_pts = np.array([landmarks[i] for i in self.RIGHT_CHEEKBONE], dtype=np.int32)

        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [l_pts], 255)
        cv2.fillPoly(mask, [r_pts], 255)
        mask = cv2.GaussianBlur(mask, (61, 61), 0)

        # Contour shadow = pure black blend
        shadow = np.zeros_like(frame)

        w = (mask / 255.0) * intensity
        w = np.expand_dims(w, axis=-1)
        return ((1 - w) * frame + w * shadow).astype(np.uint8)

    # ── Full-Frame Color Filters ───────────────────────────────────────────────
    def apply_warm_filter(self, frame):
        """Boosts reds/yellows — golden hour look."""
        result = frame.astype(np.float32)
        result[:, :, 2] = np.clip(result[:, :, 2] * 1.15, 0, 255)  # R up
        result[:, :, 1] = np.clip(result[:, :, 1] * 1.05, 0, 255)  # G up slightly
        result[:, :, 0] = np.clip(result[:, :, 0] * 0.88, 0, 255)  # B down
        return result.astype(np.uint8)

    def apply_cool_filter(self, frame):
        """Boosts blues — crisp, cinematic look."""
        result = frame.astype(np.float32)
        result[:, :, 0] = np.clip(result[:, :, 0] * 1.18, 0, 255)  # B up
        result[:, :, 2] = np.clip(result[:, :, 2] * 0.88, 0, 255)  # R down
        return result.astype(np.uint8)

    def apply_vintage_filter(self, frame):
        """Sepia + faded look — classic retro feel."""
        # Convert to float
        f = frame.astype(np.float32)
        b, g, r = f[:,:,0], f[:,:,1], f[:,:,2]

        # Sepia matrix
        out_r = np.clip(r * 0.393 + g * 0.769 + b * 0.189, 0, 255)
        out_g = np.clip(r * 0.349 + g * 0.686 + b * 0.168, 0, 255)
        out_b = np.clip(r * 0.272 + g * 0.534 + b * 0.131, 0, 255)

        sepia = np.stack([out_b, out_g, out_r], axis=-1)

        # Fade: blend with a washed-out beige to reduce contrast
        fade_color = np.full_like(sepia, (210, 200, 185), dtype=np.float32)
        result = 0.75 * sepia + 0.25 * fade_color
        return result.astype(np.uint8)
