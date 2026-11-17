#!/bin/sh
# A Claude Code status line that shows nothing: it saves the session's model
# for the pied-piper theme, which casts each agent by its model and before the
# session's first message finds it nowhere else as exactly. One file per
# session, written only when the model changes. Claude Code runs it on every
# redraw, so it stays in the shell. Turn it on with, in settings.json:
#   "statusLine": { "type": "command", "command": "~/.config/herdr-app/mods/pied-piper/claude-model.sh" }
in=$(cat)
sid=${in#*\"session_id\":\"}
[ "$sid" = "$in" ] && exit 0
sid=${sid%%\"*}
case $sid in "" | */* | .*) exit 0 ;; esac
model=${in#*\"model\":\{}
[ "$model" = "$in" ] && exit 0
model=${model%%\}*}
id=${model#*\"id\":\"}
[ "$id" = "$model" ] && exit 0
id=${id%%\"*}
[ -n "$id" ] || exit 0
dir="$HOME/.local/state/herdr-pied-piper/claude-models"
old=
[ -f "$dir/$sid" ] && IFS= read -r old < "$dir/$sid"
[ "$old" = "$id" ] && exit 0
mkdir -p "$dir" && printf '%s\n' "$id" > "$dir/$sid.$$" && mv -f "$dir/$sid.$$" "$dir/$sid"
exit 0
