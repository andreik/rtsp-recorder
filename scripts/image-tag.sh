#!/bin/sh

set -eu

if raw_tag="$(git describe --tags --always 2>/dev/null)"; then
  :
elif raw_tag="$(git rev-parse --short HEAD 2>/dev/null)"; then
  :
else
  raw_tag="dev"
fi

printf '%s\n' "$raw_tag" | tr '/:@ ' '-'
