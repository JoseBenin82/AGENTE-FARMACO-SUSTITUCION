import csv
import io

def extract_text_from_csv(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        rows = [row for row in reader]
    if not rows:
        return ""
    header = rows[0]
    text_parts = [" | ".join(header)]
    for row in rows[1:]:
        text_parts.append(" | ".join(row))
    return "\n".join(text_parts)
