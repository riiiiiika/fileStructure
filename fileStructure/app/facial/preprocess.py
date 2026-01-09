# app/facial/preprocess.py
import cv2
import torch
import numpy as np
from torchvision import transforms


# RAF-DB 用 前処理パイプライン
_transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),  # [0,255] → [0,1] & (C,H,W)
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],  # ImageNet
        std=[0.229, 0.224, 0.225]
    )
])


def preprocess_face(face_bgr: np.ndarray) -> torch.Tensor:
    """
    face_bgr:
        OpenCV形式の顔画像 (BGR, HxWx3)

    return:
        torch.Tensor (3, 224, 224)
    """

    # BGR → RGB
    face_rgb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)

    # 前処理 + Tensor化
    tensor = _transform(face_rgb)

    return tensor
