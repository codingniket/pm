#!/usr/bin/env sh
set -e

pids=$(lsof -ti tcp:8000 || true)
if [ -z "$pids" ]; then
  echo "No process found on port 8000."
  exit 0
fi

echo "$pids" | xargs kill -9
