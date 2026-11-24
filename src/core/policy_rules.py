RETURN_WINDOW_DAYS  = {
                        "Fashion":        30,
                        "Home & Kitchen": 30,
                        "Books":          30,
                        "Sports":         30,
                        "Electronics":    10,
                      }
NON_RETURNABLE      = ["Grocery", "Personal Care", "Gift Cards"]

REFUND_RULES        = {
                        "UPI":              ("the same UPI account",        "5-7 business days"),
                        "Card":             ("the same card",               "5-7 business days"),
                        "Net Banking":      ("the same bank account",       "5-7 business days"),
                        "Cash on Delivery": ("your bank account or UPI ID", "7 business days"),
                        "ShopEase Wallet":  ("ShopEase Wallet",             "24 hours"),
                      }

FREE_DELIVERY_FROM  = 499
DELIVERY_FEE        = 49
STANDARD_DELIVERY   = "3-5 business days"
DAMAGE_REPORT_HOURS = 48
RETURN_REASONS      = ["changed_mind", "damaged", "defective", "wrong_item"]

PAGE_DELIVERY       = 2
PAGE_RETURNS        = 3
PAGE_REFUNDS        = 4
PAGE_CANCELLATION   = 5
PAGE_DAMAGED        = 6
PAGE_PRIVACY        = 8


def policy_reference(*pages):
    return "ShopEase Store Policy, Page " + ", ".join(str(p) for p in pages)
