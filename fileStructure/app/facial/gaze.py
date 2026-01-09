# app/facial/gaze.py
# ===============================
# 目線（顔の向き）分析
# ===============================

import cv2
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5
)

# ランドマークID
NOSE_TIP = 1
LEFT_EYE = 33
RIGHT_EYE = 263


def is_facing_forward(image, threshold=0.15):
    """
    image: OpenCV画像（BGR）
    return: True（正面） / False（非正面）
    """
    h, w, _ = image.shape
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    result = face_mesh.process(img_rgb)
    if not result.multi_face_landmarks:
        return False

    lm = result.multi_face_landmarks[0].landmark

    nose_x = lm[NOSE_TIP].x * w
    left_x = lm[LEFT_EYE].x * w
    right_x = lm[RIGHT_EYE].x * w

    face_center_x = (left_x + right_x) / 2
    face_width = abs(right_x - left_x)
    if face_width == 0:
        return False

    offset_ratio = abs(nose_x - face_center_x) / face_width
    return offset_ratio < threshold


def calc_gaze_rate(frames):
    """
    frames: extract_frames_every_n_sec_via_pipe の出力
    return: 正面率（%）
    """
    total = 0
    forward = 0

    for frame in frames:
        img = frame["image"]
        total += 1
        if is_facing_forward(img):
            forward += 1

    if total == 0:
        return None 

    return round(forward / total * 100, 1)

def gaze_rate_to_score(gaze_rate: float) -> int:
    """
    正面率(%) → 5段階スコア(1〜5)
    閾値は好みで調整OK（卒研の仕様として明文化しやすい）
    """
    if gaze_rate >= 90.0:
        return 5
    elif gaze_rate >= 75.0:
        return 4
    elif gaze_rate >= 60.0:
        return 3
    elif gaze_rate >= 40.0:
        return 2
    else:
        return 1

