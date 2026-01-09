# app/facial/feedback.py
# ===============================
# 表情分析の結果からフィードバック文を生成
# ===============================

def generate_feedback(summary: dict) -> str:
    """
    summary例:
    {
        "happiness": 40.0,
        "neutral": 60.0,
        "tension": 0.0
    }
    """

    happiness = summary.get("happiness(笑顔)", 0.0)
    neutral   = summary.get("neutral(落ち着き)", 0.0)
    tension   = summary.get("tension(緊張)", 0.0)

    messages = []

    # 全体評価
    if tension == 0:
        messages.append("全体的に落ち着いた印象でした。")
    elif tension < 20:
        messages.append("やや緊張は見られましたが、大きな問題はありません。")
    else:
        messages.append("全体的に緊張が強く見られました。")

    # 笑顔について
    if happiness >= 40:
        messages.append("笑顔が多く、前向きな印象を与えています。")
    elif happiness > 0:
        messages.append("笑顔は見られましたが、やや控えめでした。")

    # 無表情について
    if neutral >= 60:
        messages.append("落ち着いて話せていますが硬く見える場面もありました。")

    return " ".join(messages)
