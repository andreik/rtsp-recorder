import os
import time
import subprocess
import threading
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

def build_output_pattern(current_date: str = None) -> str:
    if current_date is None:
        current_date = date_dir_name()
    base = Path(OUT_DIR) / CAM_NAME / current_date
    ensure_dir(base)
    # d225_front_YYYYmmdd_HHMMSS.mkv
    return str(base / f"{CAM_NAME}_%Y%m%d_%H%M%S.mkv")

def ffmpeg_cmd(current_date: str = None) -> list[str]:
    out_pattern = build_output_pattern(current_date)
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

    current_date = date_dir_name()
    process_ref = {"p": None}  # Use dict to allow modification from nested function
    should_stop = threading.Event()
    date_changed = threading.Event()
    date_lock = threading.Lock()

    def check_date_change():
        """Background thread to check for date changes at midnight"""
        nonlocal current_date
        while not should_stop.is_set():
            time.sleep(60)  # Check every minute
            new_date = date_dir_name()
            with date_lock:
                if new_date != current_date:
                    print(f"[{CAM_NAME}] Date changed from {current_date} to {new_date}, restarting ffmpeg")
                    current_date = new_date
                    date_changed.set()
                    # Terminate ffmpeg so it restarts with new date
                    if process_ref["p"] and process_ref["p"].poll() is None:
                        process_ref["p"].terminate()

    date_checker = threading.Thread(target=check_date_change, daemon=True)
    date_checker.start()

    while True:
        # Check if date changed (in case we're restarting after a date change)
        with date_lock:
            new_date = date_dir_name()
            if new_date != current_date:
                current_date = new_date
                print(f"[{CAM_NAME}] Using new date directory: {current_date}")

        cmd = ffmpeg_cmd(current_date)
        print(f"[{CAM_NAME}] launching ffmpeg")
        print(" ".join(cmd))

        try:
            process_ref["p"] = subprocess.Popen(cmd)
            rc = process_ref["p"].wait()
            
            # Check if we stopped due to date change
            if date_changed.is_set():
                date_changed.clear()
                with date_lock:
                    print(f"[{CAM_NAME}] Restarting with new date directory: {current_date}")
                continue
            
            print(f"[{CAM_NAME}] ffmpeg exited rc={rc}; restarting in 3s")
            time.sleep(3)
        except KeyboardInterrupt:
            print(f"[{CAM_NAME}] stopping")
            should_stop.set()
            if process_ref["p"] and process_ref["p"].poll() is None:
                process_ref["p"].terminate()
            break
        except Exception as e:
            print(f"[{CAM_NAME}] error: {e}; restarting in 5s")
            try:
                if process_ref["p"] and process_ref["p"].poll() is None:
                    process_ref["p"].terminate()
            except Exception:
                pass
            time.sleep(5)

if __name__ == "__main__":
    Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
    run_forever()
