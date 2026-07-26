from docx import Document

def extract_text_from_word(filepath: str) -> str:
    doc = Document(filepath)
    lines = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            style = para.style.name if para.style else ""
            if "Heading" in style or "Title" in style:
                lines.append(f"\n## {text}\n")
            else:
                lines.append(text)
    return "\n".join(lines)
