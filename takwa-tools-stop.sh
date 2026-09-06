#!/usr/bin/env bash
# Stop the editing tools. Finds the server by the port it holds rather than by
# matching "start.py" against process names -- that pattern also matches the
# shell running this script, which kills the wrong thing.
PORT=8099
pid=$(ss -ltnpH "sport = :$PORT" 2>/dev/null | grep -oP 'pid=\K[0-9]+' | head -1)
if [ -n "$pid" ]; then kill "$pid" && echo "Stopped."; else echo "Not running."; fi
sleep 2
