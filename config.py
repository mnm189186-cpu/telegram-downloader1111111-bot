import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
BASE_DIR = Path(__file__).parent.resolve()
DOWNLOADS_DIR = BASE_DIR / "downloads"
DOWNLOADS_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE_BYTES = int(os.getenv("MAX_FILE_SIZE_BYTES", 150 * 1024 * 1024))
ADMINS = [int(x) for x in os.getenv("ADMINS", "").split(",") if x.strip().isdigit()]
DEFAULT_LANG = os.getenv("DEFAULT_LANG", "ar")
YTDLP_BINARY = os.getenv("YTDLP_BINARY", "yt-dlp")
FFMPEG_BINARY = os.getenv("FFMPEG_BINARY", "ffmpeg")
