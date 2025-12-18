from __future__ import annotations

import csv
from csv import DictReader
from pathlib import Path

def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    
    with path.open("r",encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise ValueError("CSV has no data rows")
    return rows