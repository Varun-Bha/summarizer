import os
import re
from glob import glob
from yt_dlp import YoutubeDL

SAFE = re.compile(r'[^A-Za-z0-9._-]+')

def sanitize(name: str) -> str:
    return SAFE.sub("_", name)

def download_audio(url: str):
    os.makedirs("downloads", exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        # Use stable video ID to avoid mismatches between our computed path and yt-dlp's sanitization
        "outtmpl": os.path.join("downloads", "%(id)s.%(ext)s"),
        "noprogress": True,
        "quiet": True,
        "postprocessors": [
            { "key": "FFmpegExtractAudio", "preferredcodec": "m4a" }
        ],
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title") or "audio"
        filename = os.path.join("downloads", f"{info.get('id')}.m4a")
        if not os.path.exists(filename):
            base = os.path.join("downloads", f"{info.get('id')}")
            candidates = sorted(glob(base + ".*"))
            for c in candidates:
                if os.path.isfile(c) and not c.endswith(".part"):
                    filename = c
                    break
        return filename, {
            "title": title,
            "id": info.get("id"),
            "duration": info.get("duration"),
            "webpage_url": info.get("webpage_url") or url,
            "thumbnail": info.get("thumbnail"),
        }