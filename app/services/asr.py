import os
from faster_whisper import WhisperModel

_WHISPER_SINGLETON = None

def _get_model():
    global _WHISPER_SINGLETON
    if _WHISPER_SINGLETON is None:
        model_name = os.getenv("WHISPER_MODEL", "base")
        # compute_type can be "int8" for minimal memory; change to "float16" if you have more resources
        _WHISPER_SINGLETON = WhisperModel(model_name, device="cpu", compute_type="int8")
    return _WHISPER_SINGLETON

def transcribe_audio(path: str, language: str | None = None, translate: bool = False):
    model = _get_model()
    segments, info = model.transcribe(
        path,
        language=language,
        task="translate" if translate else "transcribe",
        vad_filter=True,
    )
    segs = []
    full_text = []
    for s in segments:
        segs.append({
            "start": round(s.start, 2),
            "end": round(s.end, 2),
            "text": s.text.strip()
        })
        full_text.append(s.text.strip())
    return {
        "text": " ".join(full_text).strip(),
        "segments": segs,
        "language": info.language,
        "duration": info.duration,
    }