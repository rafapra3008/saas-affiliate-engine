#!/usr/bin/env bash
set -euo pipefail

# Vai nella cartella dello script (root del progetto)
cd "$(dirname "$0")"

# Attiva la venv
source .venv/bin/activate

# Esegui il motore
python -m src.engine.main
