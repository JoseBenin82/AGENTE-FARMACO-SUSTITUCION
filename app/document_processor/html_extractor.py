from bs4 import BeautifulSoup

def extract_text_from_html(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()
    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)
