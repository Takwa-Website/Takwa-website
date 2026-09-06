#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Start the editing tools and open them in a browser.
#
# The point of this script is that nobody should need a terminal to edit the
# website. Double-click the desktop icon, the browser opens, you edit.
#
# It is safe to run twice. If the server is already up it just opens the
# browser at the page that is already being served, rather than starting a
# second copy and failing on "address already in use".
# ---------------------------------------------------------------------------
set -u

PORT=8099
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$HERE/.takwa-tools.log"
HOME_PAGE="http://localhost:$PORT/_photo-index.html"

note() { printf '%s\n' "$*"; }

# Is something already answering on the port? curl is the honest test: the port
# can be held by a dying process that no longer serves anything.
already_up() {
    curl -s -o /dev/null --max-time 2 "http://localhost:$PORT/_photo-index.html"
}

if already_up; then
    note "Tools are already running."
else
    command -v python3 >/dev/null || {
        note "python3 is not installed."; sleep 5; exit 1; }
    python3 -c 'import PIL' 2>/dev/null || {
        note "Pillow is missing. Install it with:  pip install Pillow"; sleep 8; exit 1; }

    note "Starting the Takwa editing tools..."
    cd "$HERE" || exit 1
    # setsid so the server outlives this script and the terminal that ran it
    setsid nohup python3 start.py > "$LOG" 2>&1 < /dev/null &

    for _ in $(seq 1 25); do
        sleep 0.4
        already_up && break
    done

    if ! already_up; then
        note "It did not start. The last few lines of the log:"
        tail -n 15 "$LOG"
        sleep 12
        exit 1
    fi
fi

note "Opening $HOME_PAGE"
xdg-open "$HOME_PAGE" >/dev/null 2>&1 &
sleep 1
