#!/bin/sh

set -eu

IMAGE_TAG="${IMAGE_TAG:-$(./scripts/image-tag.sh)}"

docker run -d \
  --name rtsp-recorder \
  --memory=512m \
  --restart unless-stopped \
  --env-file "./.env" \
  -v "$(pwd)/recordings:/recordings" \
  "rtsp-recorder:${IMAGE_TAG}"
