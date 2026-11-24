import os

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.core.config import FRONTEND_DIR, MODEL, STORE_NAME, has_api_key
from src.runner.shop_runner import ask_shopassist, clear_memory
from src.tools.store_data import customers

app = FastAPI(title="ShopAssist")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class ChatRequest(BaseModel):
    customer_id: str
    message:     str


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/status")
def status():
    return {"status": "ok", "app": "ShopAssist", "store": STORE_NAME, "model": MODEL, "has_api_key": has_api_key(),
            "running_on": "Azure App Service" if os.getenv("WEBSITE_SITE_NAME") else "Local machine",
            "team": ["ShopAssist (team leader)", "Orders Desk", "Policy Desk", "Product Desk"]}


@app.get("/api/customers")
def customer_list():
    return [{"customer_id": cid, "name": c["name"], "city": c["city"],
             "orders": [{"order_id": o["order_id"], "product": o["product"], "status": o["status"]} for o in c["orders"]]}
            for cid, c in customers().items()]


@app.post("/api/chat")
def chat(body: ChatRequest):
    if body.customer_id not in customers():
        raise HTTPException(status_code=404, detail="Unknown customer.")
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Please type a message.")
    if not has_api_key():
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY is not set. Add it to .env (local) or to the App Service environment variables (Azure).")
    return ask_shopassist(body.customer_id, body.message.strip())


@app.delete("/api/memory/{customer_id}")
def forget(customer_id: str):
    if customer_id not in customers():
        raise HTTPException(status_code=404, detail="Unknown customer.")
    clear_memory(customer_id)
    return {"cleared": True}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
