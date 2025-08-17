import csv
from datetime import datetime
from pathlib import Path
from typing import List

from config import *


def new_csv_file(file_name: str, header: List[str]):
    out_dir = Path(__file__).resolve().parent.parent / "results" / file_name
    out_dir.parent.mkdir(parents=True, exist_ok=True)

    with open(out_dir, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)


def write_csv(file_name: str, rows: List[List[str]]):
    out_dir = Path(__file__).resolve().parent.parent / "results" / file_name
    out_dir.parent.mkdir(parents=True, exist_ok=True)

    with open(out_dir, "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
