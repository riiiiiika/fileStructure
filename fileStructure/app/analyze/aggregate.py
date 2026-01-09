def aggregate_scores(scores: dict) -> dict:
    """
    各分析スコア（1〜5）を集約して
    平均・grade・total_score を算出する
    """

    used_items = {k: v for k, v in scores.items() if v is not None}
    missing_metrics = [k for k, v in scores.items() if v is None]
    values = list(used_items.values())

    if not values:
        raise ValueError("No valid scores to aggregate")

    avg = sum(values) / len(values)

    if avg >= 4.5:
        grade = "S"
    elif avg >= 4.0:
        grade = "A"
    elif avg >= 3.5:
        grade = "B+"
    elif avg >= 3.0:
        grade = "B"
    elif avg >= 2.5:
        grade = "B-"
    else:
        grade = "C"

    total_score = round((avg - 1) / 4 * 100)

    return {
        "avg_score": round(avg, 2),
        "total_score": total_score,
        "grade": grade,
        "missing_metrics": missing_metrics,
    }
