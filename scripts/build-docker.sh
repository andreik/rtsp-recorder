#!/bin/sh

set -eu

IMAGE_TAG="${IMAGE_TAG:-$(./scripts/image-tag.sh)}"
IMAGE_NAME="${IMAGE_NAME:-rtsp-recorder}"
IMAGE_REGISTRY="${IMAGE_REGISTRY:-}"
VCS_REF="${VCS_REF:-$(git rev-parse --short HEAD 2>/dev/null || printf '%s' unknown)}"

if [ -n "${IMAGE_REGISTRY}" ]; then
  IMAGE_REF="${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
  LATEST_REF="${IMAGE_REGISTRY}/${IMAGE_NAME}:latest"
else
  IMAGE_REF="${IMAGE_NAME}:${IMAGE_TAG}"
  LATEST_REF="${IMAGE_NAME}:latest"
fi

docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --build-arg "VERSION=${IMAGE_TAG}" \
  --build-arg "VCS_REF=${VCS_REF}" \
  -t "${IMAGE_REF}" \
  -t "${LATEST_REF}" \
  .
