from src.knowledge.policy import find_pages


def search_policy(question: str) -> str:
    """Search the ShopEase Store Policy PDF and return the most relevant pages as [Page N] text blocks."""
    pages = find_pages(question)
    if not pages:
        return "No matching page in the ShopEase Store Policy."
    return "\n\n".join("[Page " + str(p["page"]) + "]\n" + p["text"] for p in pages)
