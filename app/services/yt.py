import os
import re
from yt_dlp import YoutubeDL

SAFE = re.compile(r'[^A-Za-z0-9._-]+')

def sanitize(name: str) -> str:
    return SAFE.sub("_", name)

def download_audio(url: str):
    os.makedirs("downloads", exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join("downloads", "%(title).200B.%(ext)s"),
        "noprogress": True,
        "quiet": True,
        "postprocessors": [
            { "key": "FFmpegExtractAudio", "preferredcodec": "m4a" }
        ],
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title") or "audio"
        ext = "m4a"
        filename = os.path.join("downloads", f"{sanitize(title)}.{ext}")
        return filename, {
            "title": title,
            "id": info.get("id"),
            "duration": info.get("duration"),
            "webpage_url": info.get("webpage_url") or url,
            "thumbnail": info.get("thumbnail"),
        }