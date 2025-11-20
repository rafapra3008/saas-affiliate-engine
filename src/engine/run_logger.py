import json
import time
from pathlib import Path
from typing import Dict, Any, List


def start_run() -> float:
    return time.time()


def end_run(
    start_ts: float,
    num_tools: int,
    languages: List[str],
    extra: Dict[str, Any] | None = None,
    out_dir: str = "logs",
) -> Path:
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    end_ts = time.time()
    duration_sec = end_ts - start_ts

    payload: Dict[str, Any] = {
        "start_ts": start_ts,
        "end_ts": end_ts,
        "duration_sec": duration_sec,
        "num_tools": num_tools,
        "languages": languages,
    }
    if extra:
        payload.update(extra)

    ts_str = time.strftime("%Y%m%d-%H%M%S", time.gmtime(start_ts))
    file_path = out_path / f"run-{ts_str}.json"
    file_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"[LOG] Run log salvato in: {file_path}")
    return file_path
