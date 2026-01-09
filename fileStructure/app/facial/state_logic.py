STATE_MAP = {
    "happy": "happiness",
    "neutral": "neutral",

    "anger": "tension",
    "disgust": "tension",
    "fear": "tension",
    "surprise": "tension",
    "sad": "tension",
}

def emotion_to_state(emotion, confidence, th=0.6):
    if confidence < th:
        return "neutral"
    return STATE_MAP.get(emotion, "neutral")
    
def emotion_summary_to_score(summary: dict) -> int:
    """
    表情分析の summary（happiness / neutral / tension）から
    5段階評価（1〜5）を返す
    """

    happiness = summary.get("happiness", 0.0)
    tension   = summary.get("tension", 0.0)

    if happiness >= 50 and tension == 0:
        return 5
    elif happiness >= 30 and tension <= 10:
        return 4
    elif tension <= 20:
        return 3
    elif tension <= 40:
        return 2
    else:
        return 1


def gaze_rate_to_score(rate):
    if rate >= 80:
        return 5
    elif rate >= 65:
        return 4
    elif rate >= 50:
        return 3
    elif rate >= 30:
        return 2
    else:
        return 1

