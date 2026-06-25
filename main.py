from fastapi import FastAPI, Header, HTTPException
import sqlite3
import uuid
import joblib
import numpy as np
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
model = joblib.load(MODEL_PATH)

app = FastAPI()

# DB (SAUBER)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "saas.db")

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS shops (
    shop_id TEXT,
    api_key TEXT
)
""")
conn.commit()

# AUTH
def get_shop(api_key: str):
    print("INCOMING:", repr(api_key))

    cursor.execute("SELECT * FROM shops")
    rows = cursor.fetchall()
    print("ALL ROWS:", rows)

    cursor.execute(
        "SELECT shop_id FROM shops WHERE api_key=?",
        (api_key.strip(),)
    )
    result = cursor.fetchone()

    print("MATCH:", result)

    if not result:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    return result[0]
# ROOT
@app.get("/")
def root():
    return {"status": "running"}

# REGISTER
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

# PREDICT
@app.post("/predict")
def predict(data: dict, x_api_key: str = Header(..., alias="x-api-key")):

    shop_id = get_shop(x_api_key)

    features = np.array([[
        data["order_hour"],
        data["weekday"],
        data["sku_complexity"],
        data["warehouse_load"],
        data["express"],
        data["pick_time"],
        data["shipping_time"]
    ]])

    prediction = model.predict(features)[0]

    return {
        "shop": shop_id,
        "predicted_delivery_time": float(prediction)
    }