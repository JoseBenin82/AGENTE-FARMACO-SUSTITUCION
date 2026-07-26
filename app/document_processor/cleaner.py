import re

def clean_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[^\S\n]{2,}", " ", text)
    text = re.sub(r"[•●▪→⇒]", "-", text)
    text = re.sub(r"[ \u00a0]", " ", text)
    text = re.sub(r"[\uf0b7\uf0a7\u2022\u2023]", "-", text)
    text = re.sub(r"[_]{3,}", "", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    lines = text.split("\n")
    seen = set()
    clean_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            clean_lines.append("")
            continue
        normalized = stripped.lower().strip()
        if normalized in seen and len(stripped) < 80:
            continue
        seen.add(normalized)
        clean_lines.append(stripped)
    while clean_lines and clean_lines[0] == "":
        clean_lines.pop(0)
    while clean_lines and clean_lines[-1] == "":
        clean_lines.pop()
    text = "\n".join(clean_lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
