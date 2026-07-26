import markdown
from bs4 import BeautifulSoup

def extract_text_from_markdown(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()
    html = markdown.markdown(raw)
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n")
