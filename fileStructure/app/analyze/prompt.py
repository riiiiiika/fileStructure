# app/analyze/prompt.py

SYSTEM_INSTRUCTION = (
    "あなたは面接の評価者です。返答は必ずJSONのみで返してください。"
    "余計な文章、コードブロック、前置きは禁止です。"
)

# Geminiに返してほしいJSONの仕様（固定）
OUTPUT_SPEC = """
# 出力JSON（固定・省略禁止・JSONのみ）
{
  "grammar_score": 1,
  "grammar_feedback": "文法/表現に関する短評（日本語1〜2文）",
  "overall_feedback": "全項目（表情/目線/声量/話速/文法/内容）を加味した総合フィードバック（日本語3〜6文）",
  "advice_by_item": {
    "emotion": "表情への改善提案（未計測なら未計測と書く）",
    "gaze": "目線への改善提案（未計測なら未計測と書く）",
    "volume": "声量への改善提案（未計測なら未計測と書く）",
    "speech_rate": "話速への改善提案（未計測なら未計測と書く）",
    "grammar": "文法/表現への改善提案"
  }
}
""".strip()

# 総合評価用のプロンプトテンプレ
PROMPT_TEMPLATE = """
{system_instruction}

あなたは面接の総合評価者です。
以下の入力データ（表情・目線・声量・話速・文法・STT本文）を **すべて加味** して、改善点を具体的に指摘してください。

重要:
- scores_1to5 の値が null の項目は「未計測」です。
- 未計測の項目は「未計測」と明記し、それ以外の項目で総合コメントしてください。

{output_spec}

# 入力データ(JSON)
{input_json}
""".strip()
