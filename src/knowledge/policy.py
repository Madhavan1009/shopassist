import math
import re
from functools import lru_cache

from pypdf import PdfReader

from src.core.config import POLICY_PDF

STOP_WORDS = {
                "a", "an", "the", "is", "are", "am", "i", "my", "me", "can", "do", "does", "how", "what",
                "when", "where", "which", "who", "why", "for", "of", "to", "in", "on", "and", "or", "if",
                "it", "you", "your", "we", "our", "with", "be", "will", "get", "about", "any", "this", "up",
             }


def _words(text):
    return [w for w in re.findall(r"[a-z0-9₹,]+", text.lower().replace(",", "")) if w not in STOP_WORDS and len(w) > 1]


@lru_cache
def load_pages():
    reader = PdfReader(str(POLICY_PDF))
    pages  = []
    for number, page in enumerate(reader.pages, start=1):
        lines = [line.replace("\x7f", "-").strip() for line in (page.extract_text() or "").splitlines()]
        lines = [line for line in lines if line and "Sample document for PROITBRIDGE" not in line and not re.fullmatch(r"Page \d+", line)]
        pages.append({"page": number, "text": "\n".join(lines), "words": _words("\n".join(lines))})
    return pages


def find_pages(question, top_k=2):
    pages  = load_pages()
    query  = set(_words(question))
    weight = {w: math.log(1 + len(pages) / (1 + sum(w in p["words"] for p in pages))) for w in query}
    scored = []
    for page in pages:
        score = sum(page["words"].count(w) * weight[w] for w in query)
        if score:
            scored.append((score, page))
    scored.sort(key=lambda item: (-item[0], item[1]["page"]))
    return [{"page": page["page"], "text": page["text"]} for _, page in scored[:top_k]]
