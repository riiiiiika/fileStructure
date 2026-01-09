#顔画像（Tensor）を受け取って、表情の名前と自信度を返す
import torch
import torch.nn.functional as F
from app.facial.emotion_labels import EMOTION_LABELS
from torchvision import models
import torch.nn as nn


# モデル読み込み（起動時1回）
MODEL_PATH = "app/facial/models/rafdb_resnet18.pth"
#GPU / CPU を決める
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = models.resnet18(weights=None)
model.fc = nn.Linear(model.fc.in_features, 7)

state_dict = torch.load(MODEL_PATH, map_location=device)
model.load_state_dict(state_dict)

model.eval()
model.to(device)


def predict_emotion(face_tensor: torch.Tensor):
    
    with torch.no_grad():
        #Tensor を GPU/CPU に送る(model と同じデバイスに置かないとエラー)
        face_tensor = face_tensor.to(device)
        #モデルに入力して予測
        if face_tensor.dim() == 3:
            face_tensor = face_tensor.unsqueeze(0)

        logits = model(face_tensor)
        #確立に変換（softmax(0-1に変換、合計が1））
        probs = F.softmax(logits, dim=1)
        #最も確率の高いクラスを取得(ex:0.88がhappyならhappyを返す)
        confidence, pred_idx = torch.max(probs, dim=1)
        #ラベル名に変換
        emotion = EMOTION_LABELS[pred_idx.item()]
        #最も高確率のもののラベル名と確率を返す
        return emotion, confidence.item()
