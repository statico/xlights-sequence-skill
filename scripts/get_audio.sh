#!/bin/sh
# usage: scripts/get_audio.sh "<artist> <title>" <song>   -> music/<song>.mp3 (yt-dlp, first YouTube search hit) and a clean
# re-encode at xlights/music/<song>.mp3 (no cover art, no metadata, plain name; the raw download made xLights say "Media File Missing or Corrupted").
# If the user already has a file, skip the download: scripts/get_audio.sh - <song> re-encodes music/<song>.* only.
set -e; cd "$(dirname "$0")/.."; q="$1"; song="$2"; mkdir -p music xlights/music
[ "$q" = "-" ] || yt-dlp -x --audio-format mp3 --audio-quality 0 -o "music/$song.%(ext)s" "ytsearch1:$q official audio"
src=$(ls music/"$song".* | head -1)
ffmpeg -v error -y -i "$src" -vn -map_metadata -1 -c:a libmp3lame -b:a 192k "xlights/music/$song.mp3"
ffprobe -v error -show_entries format=duration -of csv=p=0 "xlights/music/$song.mp3" | awk '{printf "xlights/music/'"$song"'.mp3  %d ms\n",$1*1000}'
