import tiktoken
import re
from app.config import CHUNK_SIZE, CHUNK_OVERLAP

_ENCODER = tiktoken.get_encoding("cl100k_base")

def _count_tokens(text: str) -> int:
    return len(_ENCODER.encode(text))

def chunk_text(
    text: str,
    metadata: dict,
    chunk_size: int = None,
    chunk_overlap: int = None,
) -> list[dict]:
    if chunk_size is None:
        chunk_size = CHUNK_SIZE
    if chunk_overlap is None:
        chunk_overlap = CHUNK_OVERLAP

    sections = _split_by_structure(text)
    chunks = []
    global_chunk_idx = 0
    for section_title, section_text in sections:
        section_chunks = _split_by_tokens(
            section_text, chunk_size, chunk_overlap
        )
        for chunk_text_content in section_chunks:
            chunk_meta = metadata.copy()
            if section_title:
                chunk_meta["seccion"] = section_title
            chunk_meta["chunk_id"] = f"{metadata.get('archivo', 'unknown')}_chunk_{global_chunk_idx}"
            chunk_meta["orden"] = global_chunk_idx
            global_chunk_idx += 1
            chunks.append({
                "texto": chunk_text_content.strip(),
                "metadata": chunk_meta,
            })
    return chunks

def _split_by_structure(text: str) -> list[tuple[str, str]]:
    section_pattern = re.compile(
        r"(^|\n)(#{1,3}\s+.+?)(?=\n|$)", re.MULTILINE
    )
    heading_pattern = re.compile(
        r"(^|\n)((?:##?\s+[A-ZÁÉÍÓÚÑ].*?|(?:\d+\.\s*[A-ZÁÉÍÓÚÑ].*?)))(?=\n|$)",
        re.MULTILINE,
    )
    lines = text.split("\n")
    sections = []
    current_title = ""
    current_lines = []
    for line in lines:
        stripped = line.strip()
        if heading_pattern.match(line) or section_pattern.match(line):
            if current_lines:
                body = "\n".join(current_lines).strip()
                if body:
                    sections.append((current_title, body))
            current_title = stripped
            current_lines = []
        else:
            current_lines.append(line)
    if current_lines:
        body = "\n".join(current_lines).strip()
        if body:
            sections.append((current_title, body))
    if not sections and text.strip():
        sections.append(("", text.strip()))
    return sections

def _split_by_tokens(text: str, chunk_size: int, overlap: int) -> list[str]:
    tokens = _ENCODER.encode(text)
    if len(tokens) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = _ENCODER.decode(chunk_tokens)
        chunks.append(chunk_text)
        if end >= len(tokens):
            break
        start = end - overlap
    if len(chunks) > 1 and len(_ENCODER.encode(chunks[-1])) < chunk_size // 4:
        merged = _ENCODER.encode(chunks[-2] + " " + chunks[-1])
        if len(merged) <= chunk_size + overlap:
            chunks[-2] = _ENCODER.decode(merged)
            chunks.pop()
    return chunks
