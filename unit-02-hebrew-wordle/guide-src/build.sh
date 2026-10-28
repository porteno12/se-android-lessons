#!/bin/sh
# Rebuild index.html from guide-src (run after any change to the stages or the text).
# The code cards come from stages/: each stage is a verified, compiling snapshot of the project.
# To check every stage still compiles:  python3 guide-src/stages.py verify
# To copy the last stage into app/:     python3 guide-src/stages.py sync
set -e
cd "$(dirname "$0")/.."
TMP=$(mktemp)
python3 guide-src/stages.py render guide-src/sections.html "$TMP"
python3 ~/.claude/skills/se-lessons-apps/scripts/fill_shell.py guide-src/config.json guide-src/toc.html "$TMP" index.html app
rm -f "$TMP"
