import json
from datetime import date, timedelta
from functools import lru_cache

from src.core.config import CUSTOMERS_FILE, PRODUCTS_FILE


@lru_cache
def customers():
    return json.loads(CUSTOMERS_FILE.read_text(encoding="utf-8"))


@lru_cache
def products():
    return json.loads(PRODUCTS_FILE.read_text(encoding="utf-8"))


def customer(customer_id):
    return customers().get(customer_id or "")


def find_order(customer_id, order_id):
    person = customer(customer_id)
    if person is None:
        return None
    wanted = (order_id or "").strip().upper()
    return next((o for o in person["orders"] if o["order_id"] == wanted), None)


def order_view(order):
    today = date.today()
    view  = {
                "order_id":     order["order_id"],
                "product":      order["product"],
                "category":     order["category"],
                "price":        order["price"],
                "delivery_fee": order["delivery_fee"],
                "payment":      order["payment"],
                "status":       order["status"],
                "ordered_on":   (today - timedelta(days=order["ordered_days_ago"])).isoformat(),
            }
    if "delivered_days_ago" in order:
        view["delivered_on"] = (today - timedelta(days=order["delivered_days_ago"])).isoformat()
    if "arrives_in_days" in order:
        view["expected_delivery"] = (today + timedelta(days=order["arrives_in_days"])).isoformat()
    return view
