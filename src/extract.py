import json
import requests
from pathlib import Path
from datetime import datetime, timezone

from config import OPENSKY_API_URL
from auth import token_manager

RAW_DATA_DIR = Path("data/raw")


def extract() -> dict:
    response = requests.get(OPENSKY_API_URL, headers=token_manager.headers())
    response.raise_for_status()
    data = response.json()

    states = data.get("states", []) or []
    print(f"[extract] {len(states)} Flugzeuge im Snapshot erfasst")
    print(f"[extract] Zeitstempel (Unix): {data.get('time')}")

    return data


def save_raw(data: dict) -> Path:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    file_path = RAW_DATA_DIR / f"opensky_{timestamp}.json"

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"[extract] Gespeichert unter {file_path}")
    return file_path


if __name__ == "__main__":
    data = extract()
    save_raw(data)