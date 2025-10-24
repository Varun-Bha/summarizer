import os
import traceback
from flask import Blueprint, render_template, request, jsonify
from .services.yt import download_audio
from .services.asr import transcribe_audio
from .services.summarize import summarize_transcript

bp = Blueprint("routes", __name__)

@bp.get("/")
def index():
    return render_template("index.html")

@bp.post("/api/process")
def process():
    try:
        data = request.get_json(force=True)
        yt_url = data.get("yt_url", "").strip()
        target_lang = data.get("target_lang")  # optional
        length = data.get("length", "medium")  # short|medium|detailed
        style = data.get("style", "bullets")   # bullets|narrative
        translate = bool(data.get("translate", False))

        if not yt_url:
            return jsonify({"error": "yt_url is required"}), 400

        file_path, video_info = download_audio(yt_url)

        asr_result = transcribe_audio(file_path, language=target_lang, translate=translate)
        transcript = asr_result["text"]
        segments = asr_result["segments"]

        summary = summarize_transcript(
            transcript=transcript,
            length=length,
            style=style,
        )

        # cleanup
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass

        return jsonify({
            "summary": summary,
            "transcript": transcript,
            "segments": segments,
            "video": video_info
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500