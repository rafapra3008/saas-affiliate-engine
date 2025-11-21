#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# Se non ci sono cambiamenti, esci
if git diff --quiet && git diff --cached --quiet; then
  echo "[GIT] Nessun cambiamento da committare."
  exit 0
fi

TS=$(date -Iseconds)
MSG="chore: auto commit ${TS}"

echo "[GIT] Trovati cambiamenti, eseguo commit: ${MSG}"

git add .
git commit -m "${MSG}"
git push
