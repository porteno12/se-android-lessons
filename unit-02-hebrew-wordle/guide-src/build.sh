#!/bin/sh
# Rebuild index.html from guide-src (run after any change to the app or the text)
cd "$(dirname "$0")/.." && python3 ~/.claude/skills/se-lessons-apps/scripts/fill_shell.py guide-src/config.json guide-src/toc.html guide-src/sections.html index.html app
