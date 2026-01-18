# RTSP Recorder

A lightweight, Dockerized **RTSP video recorder** designed for unstable RTSP sources
(e.g. Wi-Fi cameras, doorbells).

The recorder runs continuously, splits video into **fixed-length segments**, and stores
them **by date**. It is optimized for **low CPU usage** by copying the original stream
(`-c copy`) without re-encoding.

This project is intended to run inside **Docker**, including on **Synology NAS**.

---

## Features

- Continuous RTSP recording
- Fixed-length video segments (default: **60 seconds**)
- Date-based directory layout (`MM-DD-YYYY`)
- **MKV** container for crash-safe recording
- Copies **video and audio** (no re-encoding)
- Tolerates imperfect RTSP timestamps
- Automatic restart on RTSP disconnect
- Fully configurable via environment variables

---

## Output Layout

```
/recordings/
  d225_front/
    01-18-2026/
      d225_front_20260118_103401.mkv
      d225_front_20260118_103501.mkv
      d225_front_20260118_103601.mkv
```

---

## Configuration

All configuration is done via environment variables (or a `.env` file).

### Environment Variables

| Variable | Required | Default | Description |
|--------|---------|---------|------------|
| `RTSP_URL` | ✅ | — | Full RTSP URL (including credentials) |
| `CAM_NAME` | ❌ | `camera` | Logical camera name |
| `OUT_DIR` | ❌ | `/recordings` | Base output directory |
| `SEGMENT_SECONDS` | ❌ | `60` | Segment length in seconds |
| `FFMPEG_LOGLEVEL` | ❌ | `warning` | ffmpeg log verbosity |

---

## Docker Usage

### Build the image

```bash
docker build -t rtsp-recorder .
```

---

### Run locally

```bash
docker run --rm -it   --env-file .env   -v $(pwd)/recordings:/recordings   rtsp-recorder
```

---

### Run on Synology NAS

```bash
docker run -d   --name rtsp-recorder   --restart unless-stopped   --env-file /volume1/docker/rtsp-recorder/.env   -v /volume1/video/rtsp:/recordings   rtsp-recorder
```

---

## License

MIT
