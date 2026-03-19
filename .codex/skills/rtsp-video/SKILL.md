---
name: rtsp-video
description: Use this skill for this RTSP recorder project's stream and recording behavior: ffmpeg flags, RTSP disconnect handling, segmentation, timestamp quirks, MKV output choices, retention behavior, recording layout, and troubleshooting unstable camera streams.
---

# Rtsp Video

Use this skill when the issue is about recording behavior, stream stability, or ffmpeg choices.

## Use When

- Adjusting ffmpeg flags or stream transport behavior
- Troubleshooting unstable RTSP sources, reconnect behavior, or timestamp issues
- Changing segment duration, output layout, or container format
- Reviewing retention behavior relative to dated recording folders
- Deciding whether logic belongs in Python or should stay in ffmpeg invocation
- Explaining tradeoffs around `tcp`, `copy`, `segment`, `mkv`, and timestamp salvage flags

## Recorder Mental Model

- `record.py` is a thin controller around `ffmpeg`
- The recorder writes into `OUT_DIR/CAM_NAME/MM-DD-YYYY/`
- Segments are written as timestamped `.mkv` files
- Date rollover and retention cleanup are handled in Python
- Stream copying is preferred over re-encoding for low CPU usage

## Workflow

1. Inspect `record.py` and confirm how the ffmpeg command is assembled.
2. Check whether the requested change belongs in ffmpeg arguments, date-directory logic, or retention cleanup.
3. Preserve low-CPU behavior unless the user explicitly wants transcoding or CV processing.
4. Keep output layout and retention semantics predictable for NAS storage.
5. Add or update tests when Python-side behavior changes.

## Repo Guardrails

- Prefer directory-level retention because the output is already date-partitioned.
- Be careful with timestamp and segmentation changes because they affect filename layout and recoverability.
- Do not introduce re-encoding casually; call out CPU and storage tradeoffs when proposing it.
- Keep stream-handling logic resilient to dirty or unreliable camera sources.

## Avoid

- Do not treat this as a generic media-transcoding project.
- Do not suggest heavy CV or OpenCV changes when the problem is actually ffmpeg or RTSP behavior.
- Do not optimize away defensive flags without explaining stream reliability consequences.
