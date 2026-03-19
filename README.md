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
- Optional retention cleanup for old recordings
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
| `RETENTION_DAYS` | ✅ | `0` (disabled) | Delete dated recording folders older than this many days |
| `CLEANUP_INTERVAL_SECONDS` | ❌ | `3600` | How often retention cleanup runs |

---

## Docker Usage

### Build the image

The build script tags the image from `git describe --tags --always`.
If no git tags exist yet, it falls back to the current commit SHA.
It also writes OCI image labels for the version tag and git commit SHA.

```bash
scripts/build-docker.sh
```

---

### Run locally

The run script uses the same git-derived image tag as the build script.
You can override it with `IMAGE_TAG=v0.3 ./scripts/run.sh` if needed.

```bash
scripts/run.sh
```

### Create a release tag

```bash
git tag v0.3
git push --tags
```

---

### Run on Synology NAS

```bash
docker run -d   --name rtsp-recorder   --restart unless-stopped   --env-file /volume1/docker/rtsp-recorder/.env   -v /volume1/video/rtsp:/recordings   rtsp-recorder:your-version-here
```

---

## License

MIT
