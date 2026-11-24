import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR       = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

DATA_DIR       = BASE_DIR / "data"
POLICY_PDF     = DATA_DIR / "ShopEase_Store_Policy.pdf"
CUSTOMERS_FILE = DATA_DIR / "customers.json"
PRODUCTS_FILE  = DATA_DIR / "products.json"
FRONTEND_DIR   = BASE_DIR / "frontend"
DB_FILE        = Path(tempfile.gettempdir()) / "shopassist_sessions.db"

MODEL          = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
STORE_NAME     = "ShopEase"
POLICY_NAME    = "ShopEase Store Policy"


def openai_key():
    return os.getenv("OPENAI_API_KEY", "").strip()


def has_api_key():
    return openai_key().startswith("sk-")
