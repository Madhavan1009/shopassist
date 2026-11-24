import re

from src.core.policy_rules import FREE_DELIVERY_FROM, DELIVERY_FEE, NON_RETURNABLE, PAGE_DELIVERY, PAGE_RETURNS, RETURN_WINDOW_DAYS, STANDARD_DELIVERY, policy_reference
from src.tools.store_data import products


def _view(product):
    category = product["category"]
    return {
            "product_id":    product["product_id"],
            "name":          product["name"],
            "category":      category,
            "price":         product["price"],
            "in_stock":      product["stock"] > 0,
            "units_left":    product["stock"],
            "rating":        product["rating"],
            "delivery":      STANDARD_DELIVERY + (", free delivery" if product["price"] >= FREE_DELIVERY_FROM else ", delivery fee ₹" + str(DELIVERY_FEE)),
            "return_window": "Non-returnable" if category in NON_RETURNABLE else str(RETURN_WINDOW_DAYS[category]) + " days",
           }


def search_products(query: str, max_price: int = 0) -> dict:
    """Search the ShopEase catalogue by product name or category. Use max_price to keep only products at or below that price (0 = no limit)."""
    words   = [w for w in re.findall(r"[a-z0-9]+", query.lower()) if len(w) > 2]
    matches = []
    for product in products():
        text = (product["name"] + " " + product["category"]).lower()
        if words and not any(w in text for w in words):
            continue
        if max_price and product["price"] > max_price:
            continue
        matches.append(_view(product))
    return {"query": query, "max_price": max_price or None, "results": matches, "policy_reference": policy_reference(PAGE_DELIVERY, PAGE_RETURNS)}


def check_stock(product_name: str) -> dict:
    """Check if one product is in stock, with its price, delivery time and return window."""
    words = [w for w in re.findall(r"[a-z0-9]+", product_name.lower()) if len(w) > 2]
    best  = max(products(), key=lambda p: sum(w in p["name"].lower() for w in words))
    if not words or not any(w in best["name"].lower() for w in words):
        return {"found": False, "message": "No product matches '" + product_name + "'."}
    return {"found": True, **_view(best), "policy_reference": policy_reference(PAGE_DELIVERY, PAGE_RETURNS)}


PRODUCT_TOOLS = [search_products, check_stock]
