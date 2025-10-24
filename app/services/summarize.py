import os
from typing import List
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

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

    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0.3,
        max_output_tokens=max_tokens,
    )

    map_prompt = PromptTemplate.from_template(
        "You are a precise analyst. Summarize the following transcript chunk "
        "into crisp bullet points with only the essential facts and topics. "
        "Avoid hallucinations. If timestamps appear, keep them.\n\n"
        "Transcript chunk:\n{chunk}"
    )

    reduce_prompt = PromptTemplate.from_template(
        "You are a helpful assistant. Merge the bullet-point summaries into a final result.\n"
        f"Output style: {'bullet points' if style=='bullets' else 'short narrative paragraphs'}.\n"
        f"Length: {length}.\n\n"
        "Include sections:\n"
        "- Executive summary\n"
        "- Detailed summary\n"
        "- Key takeaways\n"
        "- Optional action items if applicable\n\n"
        "Chunk summaries:\n{bullets}\n\nFinal summary:"
    )

    # For shorter transcripts, do single-shot
    if len(transcript) < 8000:
        single_prompt = PromptTemplate.from_template(
            "Summarize the following transcript. Style: "
            f"{'bullets' if style=='bullets' else 'narrative'}, Length: {length}. "
            "Include Executive summary, Detailed summary, Key takeaways, and optional Action items.\n\n"
            "{text}"
        )
        resp = llm.invoke(single_prompt.format(text=transcript))
        return resp.content.strip()

    # Map-reduce for longer inputs
    chunks = chunk_text(transcript, 8000)
    mapped = []
    for ch in chunks:
        resp = llm.invoke(map_prompt.format(chunk=ch))
        mapped.append(resp.content.strip())

    joined = "\n\n".join(mapped)
    final_resp = llm.invoke(reduce_prompt.format(bullets=joined))
    return final_resp.content.strip()