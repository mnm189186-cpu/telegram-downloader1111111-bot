import asyncio
import uuid
from pathlib import Path
from typing import Optional, List, Tuple, Dict

from config import DOWNLOADS_DIR, YTDLP_BINARY, FFMPEG_BINARY, MAX_FILE_SIZE_BYTES

async def run_cmd(cmd: List[str], cwd: Optional[Path] = None, timeout: int = 3600) -> Tuple[int, str, str]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(cwd) if cwd else None,
    )
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        return -1, "", f"Timeout after {timeout}s"
    return proc.returncode, out.decode(errors="ignore"), err.decode(errors="ignore")

async def ytdlp_info(url_or_query: str) -> Dict:
    cmd = [YTDLP_BINARY, "--no-warnings", "--no-playlist", "--dump-single-json", url_or_query]
    code, out, err = await run_cmd(cmd)
    if code != 0:
        raise RuntimeError(f"yt-dlp info failed: {err or out}")
    import json
    return json.loads(out)

class DownloadResult:
    def __init__(self, filepath: Path, meta: Dict):
        self.filepath = filepath
        self.meta = meta

async def download_media(url: str, format_selector: Optional[str] = None, output_basename: Optional[str] = None, extract_audio: bool = False) -> DownloadResult:
    uid = uuid.uuid4().hex
    workdir = DOWNLOADS_DIR / uid
    workdir.mkdir(parents=True, exist_ok=True)
    out_template = (output_basename or "%(title).200s-%(id)s") + ".%(ext)s"
    out_path = str(workdir / out_template)
    cmd = [
        YTDLP_BINARY,
        "-o", out_path,
        "--no-warnings",
        "--restrict-filenames",
        "--merge-output-format", "mp4",
    ]
    if format_selector:
        cmd += ["-f", format_selector]
    if extract_audio:
        cmd += ["-x", "--audio-format", "mp3", "--audio-quality", "0"]
    code, out, err = await run_cmd(cmd + [url], cwd=workdir, timeout=3600)
    if code != 0:
        raise RuntimeError(f"yt-dlp download failed: {err or out}")
    files = list(workdir.glob("*"))
    if not files:
        raise RuntimeError("No output file after yt-dlp")
    files_sorted = sorted(files, key=lambda p: p.stat().st_size, reverse=True)
    target = files_sorted[0]
    if target.stat().st_size > MAX_FILE_SIZE_BYTES:
        return DownloadResult(filepath=target, meta={"warning": "file_too_large"})
    try:
        meta = await ytdlp_info(url)
    except Exception:
        meta = {}
    return DownloadResult(filepath=target, meta=meta)
