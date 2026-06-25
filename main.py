from fastapi import FastAPI, Header, HTTPException
import sqlite3
import uuid

app = FastAPI()

# DB
conn = sqlite3.connect("saas.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS shops (
    shop_id TEXT,
    api_key TEXT
)
""")
conn.commit()

# Auth
def get_shop(api_key: str):
    cursor.execute("SELECT shop_id FROM shops WHERE api_key=?", (api_key,))
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    return result[0]

# Root
@app.get("/")
def root():
    return {"status": "Phase 4 running"}

# Shop erstellen
@app.post("/register_shop")
def register_shop():
    shop_id = str(uuid.uuid4())
    api_key = str(uuid.uuid4())

    cursor.execute("INSERT INTO shops VALUES (?, ?)", (shop_id, api_key))
    conn.commit()

    return {
        "shop_id": shop_id,
        "api_key": api_key
    }

# Predict
@app.post("/predict")
def predict(data: dict, x_api_key: str = Header(...)):

    shop_id = get_shop(x_api_key)

    score = (
        data["warehouse_load"] * 0.05 +
        data["sku_complexity"] * 1.8 +
        data["pick_time"] * 2.0 +
        data["shipping_time"] * 1.1 +
        (-2 if data["express"] == 1 else 0)
    )

    return {
        "shop": shop_id,
        "p10": round(score * 0.9, 2),
        "p50": round(score, 2),
        "p90": round(score * 1.2, 2)
    }