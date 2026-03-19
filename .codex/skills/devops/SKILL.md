---
name: devops
description: Use this skill for this RTSP recorder project's operational work: release tagging, Docker build and push flows, registry-tagged images, Synology NAS deployment, container verification, and troubleshooting runtime issues around env vars, mounts, and image tags.
---

# Devops

Use this skill when work is primarily operational rather than recorder logic.

## Use When

- Releasing a new version with `make release VERSION=...`
- Building or pushing Docker images
- Working with `IMAGE_REGISTRY`, image tags, or OCI metadata
- Deploying or updating the container on Synology NAS
- Verifying whether the correct image or container is running
- Troubleshooting container startup, env-file usage, mounts, or restart behavior

## Repo Workflow

1. Confirm the current release tag with `./scripts/image-tag.sh` or `git describe --tags --always`.
2. For a release, use `make release VERSION=vX.Y`.
3. Build images with `./scripts/build-docker.sh`.
4. Build for a registry with `IMAGE_REGISTRY=<IP:PORT> ./scripts/build-docker.sh`.
5. Push registry-tagged images with `IMAGE_REGISTRY=<IP:PORT> ./scripts/push-docker.sh`.
6. Run locally with `./scripts/run.sh` or from a registry with `IMAGE_REGISTRY=<IP:PORT> ./scripts/run.sh`.

## Repo Conventions

- Keep Docker image naming aligned across build, push, and run commands.
- Prefer the repo scripts over hand-written Docker commands unless debugging something unusual.
- Treat `RETENTION_DAYS` as explicit config for deployments.
- Keep README operational examples in sync with script behavior.

## Checks

- Verify the working tree before tagging or release operations.
- Verify the image tag used for build matches the tag used for push and run.
- If checking runtime state, inspect both containers and images.
- On Synology deploys, verify mount paths and env-file paths exactly.

## Avoid

- Do not hardcode a personal registry address into the scripts.
- Do not document a placeholder flow that differs from actual repo scripts.
- Do not change release or deploy behavior without updating the README examples.
