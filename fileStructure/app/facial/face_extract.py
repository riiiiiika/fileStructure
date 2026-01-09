#動画から切り出したフレーム群を受け取って、顔画像を抽出し保存、Tensor化して返す
#Tensor = AIが理解できる「数のかたまり」
from app.facial.preprocess import preprocess_face
import cv2
import os
import mediapipe as mp

mp_face_detection = mp.solutions.face_detection
# 顔検出器の初期化
face_detector = mp_face_detection.FaceDetection(
    model_selection=0,#近距離向け
    min_detection_confidence=0.6#信頼度閾値(60%以上でこれは顔！！)
)

SAVE_DIR = "app/facial/tmp/faces"#保存先


def extract_faces_from_frames(frames):
    # 保存先ディレクトリ作成
    os.makedirs(SAVE_DIR, exist_ok=True)

    faces = []
    for frame in frames:
        time_sec = frame["time_sec"]
        img = frame["image"]

        h, w, _ = img.shape
        #bgrをrgbに変換
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        #顔検出を実行（なければcontinueで次へ）
        results = face_detector.process(img_rgb)
        if not results.detections:
            continue
        #検出された顔ごとに処理
        for i, det in enumerate(results.detections):
            # 顔のバウンディングボックスを取得
            bbox = det.location_data.relative_bounding_box
            # 画像のどこを切り取るか計算
            x1 = max(0, int(bbox.xmin * w))
            y1 = max(0, int(bbox.ymin * h))
            x2 = min(w, int((bbox.xmin + bbox.width) * w))
            y2 = min(h, int((bbox.ymin + bbox.height) * h))

            #画像から顔部分を切り出す（上で計算した座標を使う）
            face_img = img[y1:y2, x1:x2]
            if face_img.size == 0:
                continue

            # 保存（face_〇〇秒.jpg)
            filename = f"face_{time_sec:03d}s_{i}.jpg"
            path = os.path.join(SAVE_DIR, filename)
            cv2.imwrite(path, face_img)

            # tensor をここで作る
            #OpenCVの画像をTensorに変換する関数を使う
            face_tensor = preprocess_face(face_img)
            #リストに追加(時間(何秒の所か）、パス、Tensorを格納)
            faces.append({
                "time_sec": time_sec,
                "path": path,
                "tensor": face_tensor
            })

    return faces
