# app/analyze/service.py

import os
import json
import re
import traceback
from typing import Any, Dict, Union

from google import genai

from app import db
from app.models import GeminiAnalysis
from app.analyze.aggregate import aggregate_scores
from app.analyze.prompt import SYSTEM_INSTRUCTION, PROMPT_TEMPLATE, OUTPUT_SPEC


def finalize_analysis_scores(analysis: GeminiAnalysis) -> Dict[str, Any]:
    """
    GeminiAnalysis に入っている各スコア(1〜5)を集約して
    total_score / grade を確定してDB保存する。
    未取得の項目は None として除外され、missing_metrics に記録される。
    """
    scores = {
        "emotion": analysis.emotion_score,
        "gaze": analysis.gaze_score,
        "volume": analysis.volume_score,
        "speech_rate": analysis.speech_rate_score,
        "grammar": analysis.grammar_score,
    }

    result = aggregate_scores(scores)

    analysis.total_score = result["total_score"]
    analysis.grade = result["grade"]

    # DBに missing_metrics カラムがある場合のみ保存
    if hasattr(analysis, "missing_metrics"):
        analysis.missing_metrics = result.get("missing_metrics", [])

    db.session.commit()
    return result


def _extract_json(text: str) -> Dict[str, Any]:
    """
    Geminiの返答から最初の { ... } を抜き出してJSONとして読む
    （余計な文章が混ざっても耐える）
    """
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        raise ValueError(f"JSON object not found in response: {text[:200]}")
    return json.loads(m.group(0))


def _build_prompt(analysis: GeminiAnalysis) -> str:
    """
    全体フィードバック用に、STTだけでなく各分析結果も渡すプロンプトを作る。
    未計測項目は None → JSONでは null として渡される。
    """
    input_payload = {
        "stt_text": analysis.stt_text,

        # 5段階スコア（Noneは未計測）
        "scores_1to5": {
            "emotion": analysis.emotion_score,
            "gaze": analysis.gaze_score,
            "volume": analysis.volume_score,               # Noneなら未計測
            "speech_rate": analysis.speech_rate_score,     # Noneなら未計測
            "grammar": analysis.grammar_score,             # Geminiがこれから算出（既にあれば入ってもOK）
        },

        # 数値・内訳（あるものだけ）
        "details": {
            "emotion_summary": analysis.emotion_summary,
            "gaze_rate_percent": analysis.gaze_rate,
            "frames_extracted": analysis.frames_extracted,
            "interval_sec": analysis.interval_sec,
        },
    }

    return PROMPT_TEMPLATE.format(
        system_instruction=SYSTEM_INSTRUCTION.strip(),
        output_spec=OUTPUT_SPEC,
        input_json=json.dumps(input_payload, ensure_ascii=False),
    )


def run_gemini_and_save(video_id: int) -> Union[GeminiAnalysis, Dict[str, Any]]:
    """
    video_id に紐づく GeminiAnalysis を読み、
    Geminiで grammar_score + feedback を生成してDB保存して返す。

    失敗時は {"error": "...", "detail": "...", ...} を返す。
    """
    analysis = GeminiAnalysis.query.filter_by(video_id=int(video_id)).first()
    if not analysis:
        return {
            "error": "analysis_not_found",
            "detail": f"GeminiAnalysis not found for video_id={video_id}. Run /analyze/save first."
        }

    if not analysis.stt_text or not str(analysis.stt_text).strip():
        return {
            "error": "stt_text_empty",
            "detail": "stt_text is empty. Save STT text to GeminiAnalysis.stt_text first."
        }

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {
            "error": "api_key_missing",
            "detail": "GEMINI_API_KEY is missing in this server process environment."
        }

    try:
        client = genai.Client(api_key=api_key)

        prompt = _build_prompt(analysis)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"temperature": 0.2},
        )

        text = getattr(response, "text", None)
        if not text:
            return {
                "error": "gemini_no_text",
                "detail": f"Gemini response has no .text. response={response!r}"
            }

        payload = _extract_json(text)

        # 必須キー確認（無いときは原因が見えるように例外にする）
        required = ["grammar_score", "grammar_feedback", "overall_feedback", "advice_by_item"]
        missing = [k for k in required if k not in payload]
        if missing:
            raise ValueError(f"Missing keys: {missing}. payload={payload}")

        # --- grammar_score / feedback を保存 ---
        analysis.grammar_score = int(payload["grammar_score"])

        if hasattr(analysis, "grammar_feedback"):
            analysis.grammar_feedback = payload.get("grammar_feedback")

        if hasattr(analysis, "overall_feedback"):
            analysis.overall_feedback = payload.get("overall_feedback")

        # advice_by_item をDBに保存したいなら、JSONカラムを追加してここで保存
        # 例: analysis.advice_by_item = payload.get("advice_by_item")

        # ✅ grammar が入った後のスコアで総合点を再計算して保存（commitもここで行う）
        finalize_analysis_scores(analysis)

        return analysis

    except Exception as e:
        return {
            "error": "gemini_exception",
            "detail": str(e),
            "trace": traceback.format_exc(),
        }
