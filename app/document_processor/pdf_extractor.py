import fitz

def extract_text_from_pdf(filepath: str) -> str:
    text_parts = []
    with fitz.open(filepath) as doc:
        for page_num, page in enumerate(doc, start=1):
            page_text = page.get_text()
            if page_text.strip():
                text_parts.append(f"[Página {page_num}]\n{page_text}")
    return "\n\n".join(text_parts)
