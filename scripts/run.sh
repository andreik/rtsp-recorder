#!/bin/sh

set -eu

IMAGE_TAG="${IMAGE_TAG:-$(./scripts/image-tag.sh)}"
IMAGE_NAME="${IMAGE_NAME:-rtsp-recorder}"
IMAGE_REGISTRY="${IMAGE_REGISTRY:-}"

if [ -n "${IMAGE_REGISTRY}" ]; then
  IMAGE_REF="${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
else
  IMAGE_REF="${IMAGE_NAME}:${IMAGE_TAG}"
fi

docker run -d \
  --name rtsp-recorder \
  --memory=512m \
  --restart unless-stopped \
  --env-file "./.env" \
  -v "$(pwd)/recordings:/recordings" \
  "${IMAGE_REF}"
