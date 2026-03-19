---
name: python-cv
description: Use this skill for Python computer-vision work related to this recorder project: future frame processing, OpenCV integration, inference pipelines, video analysis code structure, performance tradeoffs, and tests for Python-side video processing.
---

# Python Cv

Use this skill when the work moves beyond pure recording and into Python-based video analysis.

## Use When

- Adding frame extraction, OpenCV, or image-processing logic
- Designing a Python video-analysis pipeline on top of recorded segments or live frames
- Integrating detection, tracking, or inference into the recorder workflow
- Organizing Python code for future CV modules, helpers, or tests
- Evaluating CPU, memory, and latency tradeoffs for analysis work

## Scope Boundary

- This skill is for Python-side analysis and CV architecture.
- If the issue is mainly about RTSP capture, ffmpeg flags, segmentation, or retention, use `rtsp-video` instead.
- If the issue is mainly about Docker, release, registry, or Synology deployment, use `devops` instead.

## Guidance

1. Keep recording and analysis responsibilities separate unless the user explicitly wants them combined.
2. Prefer small, testable Python modules over embedding CV behavior directly into operational scripts.
3. Be explicit about tradeoffs: CPU load, frame rate, latency, storage, and failure handling.
4. For new CV paths, propose where they fit: inline with capture, post-processing segments, or as a separate worker.
5. Add tests around Python-side behavior when introducing parsing, frame logic, or decision code.

## Future-Oriented Patterns

- Separate capture from analysis whenever possible.
- Treat recorded segments as a stable handoff boundary.
- Keep dependencies intentional; do not add OpenCV or ML libraries unless the new functionality clearly needs them.
- Prefer clear module boundaries for ingestion, decoding, processing, and output.

## Avoid

- Do not blur ffmpeg/RTSP issues into Python-CV work.
- Do not add CV dependencies before the repo actually needs them.
- Do not increase recorder complexity when a sidecar analysis process would be cleaner.
