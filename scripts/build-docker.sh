#!/bin/sh

set -eu

IMAGE_TAG="${IMAGE_TAG:-$(./scripts/image-tag.sh)}"
VCS_REF="${VCS_REF:-$(git rev-parse --short HEAD 2>/dev/null || printf '%s' unknown)}"

docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --build-arg "VERSION=${IMAGE_TAG}" \
  --build-arg "VCS_REF=${VCS_REF}" \
  -t "rtsp-recorder:${IMAGE_TAG}" \
  -t "rtsp-recorder:latest" \
  .
