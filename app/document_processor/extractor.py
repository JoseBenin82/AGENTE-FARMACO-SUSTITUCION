from pathlib import Path

from .pdf_extractor import extract_text_from_pdf
from .word_extractor import extract_text_from_word
from .excel_extractor import extract_text_from_excel
from .ppt_extractor import extract_text_from_pptx
from .markdown_extractor import extract_text_from_markdown
from .csv_extractor import extract_text_from_csv
from .json_extractor import extract_text_from_json
from .html_extractor import extract_text_from_html

EXTRACTORS = {
    ".pdf": extract_text_from_pdf,
    ".docx": extract_text_from_word,
    ".xlsx": extract_text_from_excel,
    ".pptx": extract_text_from_pptx,
    ".md": extract_text_from_markdown,
    ".csv": extract_text_from_csv,
    ".json": extract_text_from_json,
    ".html": extract_text_from_html,
    ".htm": extract_text_from_html,
}

def extract_text(filepath: str) -> tuple[str, str]:
    path = Path(filepath)
    ext = path.suffix.lower()
    if ext not in EXTRACTORS:
        raise ValueError(f"Formato no soportado: {ext}")
    text = EXTRACTORS[ext](filepath)
    return text, ext
