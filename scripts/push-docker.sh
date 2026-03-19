#!/bin/sh

set -eu

IMAGE_TAG="${IMAGE_TAG:-$(./scripts/image-tag.sh)}"
IMAGE_NAME="${IMAGE_NAME:-rtsp-recorder}"
IMAGE_REGISTRY="${IMAGE_REGISTRY:?IMAGE_REGISTRY is required, for example IMAGE_REGISTRY=<IP:PORT>}"

IMAGE_REF="${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
LATEST_REF="${IMAGE_REGISTRY}/${IMAGE_NAME}:latest"

docker push "${IMAGE_REF}"
docker push "${LATEST_REF}"
