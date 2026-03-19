#!/bin/sh

set -eu

IMAGE_TAG="${IMAGE_TAG:-$(./scripts/image-tag.sh)}"

docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t "rtsp-recorder:${IMAGE_TAG}" \
  -t "rtsp-recorder:latest" \
  .
