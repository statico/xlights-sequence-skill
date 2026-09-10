#!/bin/sh
# usage: scripts/render.sh <song>  -> renders xlights/sequences/<song>.xsq headless, one render at a time (mkdir lock). Exit 0 only means the file parsed.
cd "$(dirname "$0")/.."; mkdir -p tmp; while ! mkdir tmp/render.lock 2>/dev/null; do sleep 5; done; trap 'rmdir tmp/render.lock' EXIT
XL=${XLIGHTS:-/Applications/xLights.app/Contents/MacOS/xLights}   # linux: xlights on PATH
"$XL" -r "$PWD/xlights/sequences/$1.xsq" >/dev/null 2>&1; echo "render exit $?"; ls -la "xlights/sequences/$1.fseq"
