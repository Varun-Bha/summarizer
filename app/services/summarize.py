import os
from typing import List
import google.generativeai as genai

def chunk_text(text: str, max_chars: int = 8000) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            # try to split on sentence boundary
            dot = text.rfind(".", start, end)
            if dot > start + int(max_chars * 0.5):
                end = dot + 1
        chunks.append(text[start:end].strip())
        start = end
    return [c for c in chunks if c]

def summarize_transcript(transcript: str, length: str = "medium", style: str = "bullets") -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not set")

    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    max_tokens = int(os.getenv("SUMMARIZE_MAX_TOKENS", "2048"))
    temperature = 0.3

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    # For shorter transcripts, do single-shot
    if len(transcript) < 8000:
        prompt = (
            "Summarize the following transcript. Style: "
            f"{'bullets' if style=='bullets' else 'narrative'}, Length: {length}. "
            "Include Executive summary, Detailed summary, Key takeaways, and optional Action items.\n\n"
            f"{transcript}"
        )
        resp = model.generate_content(
            prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            },
        )
        return (resp.text or "").strip()

    # Map-reduce for longer inputs
    chunks = chunk_text(transcript, 8000)
    mapped = []
    for ch in chunks:
        prompt = (
            "You are a precise analyst. Summarize the following transcript chunk "
            "into crisp bullet points with only the essential facts and topics. "
            "Avoid hallucinations. If timestamps appear, keep them.\n\n"
            f"Transcript chunk:\n{ch}"
        )
        resp = model.generate_content(
            prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            },
        )
        mapped.append((resp.text or "").strip())

    joined = "\n\n".join(mapped)
    final_prompt = (
        "You are a helpful assistant. Merge the bullet-point summaries into a final result.\n"
        f"Output style: {'bullet points' if style=='bullets' else 'short narrative paragraphs'}.\n"
        f"Length: {length}.\n\n"
        "Include sections:\n"
        "- Executive summary\n"
        "- Detailed summary\n"
        "- Key takeaways\n"
        "- Optional action items if applicable\n\n"
        f"Chunk summaries:\n{joined}\n\nFinal summary:"
    )
    final_resp = model.generate_content(
        final_prompt,
        generation_config={
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        },
    )
    return (final_resp.text or "").strip()