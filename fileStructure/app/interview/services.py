#質問をシャッフルしてラウンドロビン方式で並び替える関数を作る
from collections import defaultdict
import random

def arrange_round_robin(question_dicts):
    # カテゴリごとに分類
    groups = defaultdict(list)
    for q in question_dicts:
        groups[q["category"]].append(q)

    # 各カテゴリ内をシャッフル
    for cat in groups:
        random.shuffle(groups[cat])

    # ラウンドロビン生成
    result = []
    categories = list(groups.keys())
    random.shuffle(categories)  # ラウンド順もランダムにする

    # 最大ラウンド数
    max_len = max(len(v) for v in groups.values())

    for r in range(max_len):
        # ラウンドごとにカテゴリ順に1個ずつ取り出す
        for cat in categories:
            if r < len(groups[cat]):
                result.append(groups[cat][r])

    return result

