import os
import time
import subprocess
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Load .env if present (works in Docker too)
load_dotenv()

CAM_NAME = os.getenv("CAM_NAME", "d225_front")
RTSP_URL = os.getenv("RTSP_URL")
OUT_DIR = os.getenv("OUT_DIR", "/recordings")
SEGMENT_SECONDS = int(os.getenv("SEGMENT_SECONDS", "60"))
LOGLEVEL = os.getenv("FFMPEG_LOGLEVEL", "warning")

if not RTSP_URL:
    raise RuntimeError("RTSP_URL is not set (check .env)")

def date_dir_name() -> str:
    # MM-DD-YYYY
    return datetime.now().strftime("%m-%d-%Y")

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def build_output_pattern() -> str:
    base = Path(OUT_DIR) / CAM_NAME / date_dir_name()
    ensure_dir(base)
    # d225_front_YYYYmmdd_HHMMSS.mkv
    return str(base / f"{CAM_NAME}_%Y%m%d_%H%M%S.mkv")

def ffmpeg_cmd() -> list[str]:
    out_pattern = build_output_pattern()
    return [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", LOGLEVEL,

        # RTSP stability + timestamp salvage for "dirty" sources
        "-rtsp_transport", "tcp",
        "-fflags", "+genpts+igndts+discardcorrupt",
        "-use_wallclock_as_timestamps", "1",

        "-i", RTSP_URL,

        # Copy both video+audio (audio is a must for you)
        "-c", "copy",

        # Segmenting
        "-f", "segment",
        "-segment_time", str(SEGMENT_SECONDS),
        "-reset_timestamps", "1",
        "-segment_format", "mkv",
        "-strftime", "1",

        out_pattern,
    ]

def run_forever():
    print(f"[{CAM_NAME}] starting")
    print(f"[{CAM_NAME}] OUT_DIR={OUT_DIR} SEGMENT_SECONDS={SEGMENT_SECONDS}")

    while True:
        cmd = ffmpeg_cmd()
        print(f"[{CAM_NAME}] launching ffmpeg")
        print(" ".join(cmd))

        p = None
        try:
            p = subprocess.Popen(cmd)
            rc = p.wait()
            print(f"[{CAM_NAME}] ffmpeg exited rc={rc}; restarting in 3s")
            time.sleep(3)
        except KeyboardInterrupt:
            print(f"[{CAM_NAME}] stopping")
            if p and p.poll() is None:
                p.terminate()
            break
        except Exception as e:
            print(f"[{CAM_NAME}] error: {e}; restarting in 5s")
            try:
                if p and p.poll() is None:
                    p.terminate()
            except Exception:
                pass
            time.sleep(5)

if __name__ == "__main__":
    Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
    run_forever()
