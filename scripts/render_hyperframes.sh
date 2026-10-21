#!/usr/bin/env bash
# Check and render a HyperFrames project.
# Usage: scripts/render_hyperframes.sh <hyperframes-project-dir> [output.mp4]
set -euo pipefail

PROJECT="${1:?usage: render_hyperframes.sh <project-dir> [output.mp4]}"
OUTPUT="${2:-out.mp4}"
VERSION="${HYPERFRAMES_VERSION:-0.8.181}"

cd "$PROJECT"
npx --yes "hyperframes@$VERSION" check
npx --yes "hyperframes@$VERSION" render --fps 30 --quality high --workers 4 -o "$OUTPUT"
ffprobe -v error -show_entries format=duration,size \
  -show_entries stream=codec_type,codec_name,width,height,r_frame_rate \
  -of default=nw=1 "$OUTPUT"
