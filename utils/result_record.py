import csv
from pathlib import Path


def write_csv(file_name, header, rows):
    out_dir = Path(__file__).resolve().parent.parent / "results" / file_name
    out_dir.parent.mkdir(parents=True, exist_ok=True)
    with open(out_dir, "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
