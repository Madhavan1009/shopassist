from datetime import date, timedelta

from agno.run.base import RunContext

from src.core.policy_rules import (
    DAMAGE_REPORT_HOURS,
    NON_RETURNABLE,
    PAGE_CANCELLATION,
    PAGE_DAMAGED,
    PAGE_PRIVACY,
    PAGE_REFUNDS,
    PAGE_RETURNS,
    REFUND_RULES,
    RETURN_REASONS,
    RETURN_WINDOW_DAYS,
    policy_reference,
)
from src.tools.store_data import customer, find_order, order_view


def _not_your_order(order_id):
    return {
            "found":            False,
            "order_id":         order_id,
            "message":          "This order is not on the signed-in account. For privacy, only the customer's own orders can be shown.",
            "policy_reference": policy_reference(PAGE_PRIVACY),
           }


def _return_check(order):
    status = order["status"]
    if status == "Processing":
        return {"eligible": False, "reason": "Not dispatched yet. It can be cancelled free of charge instead of returned.", "policy_reference": policy_reference(PAGE_CANCELLATION)}
    if status != "Delivered":
        return {"eligible": False, "reason": "Not delivered yet. Refuse it at the doorstep or return it after delivery.", "policy_reference": policy_reference(PAGE_CANCELLATION)}
    if order["category"] in NON_RETURNABLE:
        return {"eligible": False, "reason": order["category"] + " items are non-returnable.", "policy_reference": policy_reference(PAGE_RETURNS)}
    window    = RETURN_WINDOW_DAYS[order["category"]]
    days_used = order["delivered_days_ago"]
    last_day  = (date.today() + timedelta(days=window - days_used)).isoformat()
    if days_used > window:
        reason = "The " + str(window) + "-day return window for " + order["category"] + " ended " + str(days_used - window) + " day(s) ago."
        if order["category"] == "Electronics":
            reason += " A warranty claim through the brand service centre is still possible."
            return {"eligible": False, "reason": reason, "return_window_days": window, "policy_reference": policy_reference(PAGE_RETURNS, PAGE_DAMAGED)}
        return {"eligible": False, "reason": reason, "return_window_days": window, "policy_reference": policy_reference(PAGE_RETURNS)}
    return {
            "eligible":           True,
            "return_window_days": window,
            "days_left":          window - days_used,
            "last_return_date":   last_day,
            "conditions":         "Unused, original packaging, all tags and accessories. Free pickup within 2 business days.",
            "policy_reference":   policy_reference(PAGE_RETURNS),
           }


def get_my_orders(run_context: RunContext) -> dict:
    """List every order of the signed-in customer with its status and dates."""
    person = customer(run_context.user_id)
    if person is None:
        return {"found": False, "message": "No signed-in customer."}
    return {"customer": person["name"], "orders": [order_view(o) for o in person["orders"]]}


def get_order_details(run_context: RunContext, order_id: str) -> dict:
    """Get one order of the signed-in customer by its order ID, for example SE-1001."""
    order = find_order(run_context.user_id, order_id)
    if order is None:
        return _not_your_order(order_id)
    return {"found": True, **order_view(order)}


def check_return_eligibility(run_context: RunContext, order_id: str) -> dict:
    """Check whether an order of the signed-in customer can be returned, using the store's return rules."""
    order = find_order(run_context.user_id, order_id)
    if order is None:
        return _not_your_order(order_id)
    return {"found": True, "order_id": order["order_id"], "product": order["product"], "category": order["category"], **_return_check(order)}


def estimate_refund(run_context: RunContext, order_id: str, reason: str) -> dict:
    """Work out the refund amount, where it goes and how long it takes. reason must be one of: changed_mind, damaged, defective, wrong_item."""
    if reason not in RETURN_REASONS:
        return {"valid": False, "message": "reason must be one of: " + ", ".join(RETURN_REASONS)}
    order = find_order(run_context.user_id, order_id)
    if order is None:
        return _not_your_order(order_id)
    if order["status"] != "Delivered":
        return {"valid": False, "order_id": order["order_id"], **_return_check(order)}
    destination, timeline = REFUND_RULES[order["payment"]]
    hours_since           = order["delivered_days_ago"] * 24
    if reason != "changed_mind" and hours_since <= DAMAGE_REPORT_HOURS:
        return {
                "valid":                 True,
                "order_id":              order["order_id"],
                "refund_amount":         order["price"] + order["delivery_fee"],
                "includes_delivery_fee": True,
                "refund_to":             destination,
                "refund_time":           timeline + " after the quality check",
                "other_option":          "A replacement instead of a refund, if the item is in stock.",
                "policy_reference":      policy_reference(PAGE_REFUNDS, PAGE_DAMAGED),
               }
    check = _return_check(order)
    if not check["eligible"]:
        return {"valid": False, "order_id": order["order_id"], **check}
    return {
            "valid":                 True,
            "order_id":              order["order_id"],
            "refund_amount":         order["price"],
            "includes_delivery_fee": False,
            "refund_to":             destination,
            "refund_time":           timeline + " after the quality check",
            "policy_reference":      policy_reference(PAGE_REFUNDS),
           }


ORDER_TOOLS = [get_my_orders, get_order_details, check_return_eligibility, estimate_refund]
