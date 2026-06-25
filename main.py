from fastapi import FastAPI, Header, HTTPException
import sqlite3
import uuid
import os
import numpy as np
import joblib
from datetime import datetime

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "saas.db")
model = joblib.load(os.path.join(BASE_DIR, "model.pkl"))

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS shops (
    shop_id TEXT,
    api_key TEXT
)
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id TEXT,
    shop_id TEXT,
    timestamp TEXT,
    prediction REAL
)
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usage (
    shop_id TEXT,
    requests INTEGER
)
""")
conn.commit()
def get_shop(api_key: str):
    cursor.execute(
        "SELECT shop_id FROM shops WHERE api_key=?",
        (api_key.strip(),)
    )
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    return result[0]
@app.get("/")
def root():
    return {"status": "running"}
@app.post("/register_shop")
def register_shop():
    shop_id = str(uuid.uuid4())
    api_key = str(uuid.uuid4())

    cursor.execute("INSERT INTO shops VALUES (?, ?)", (shop_id, api_key))
    conn.commit()

    return {"shop_id": shop_id, "api_key": api_key}
@app.post("/predict")
def predict(data: dict, x_api_key: str = Header(..., alias="x-api-key")):

    shop_id = get_shop(x_api_key)

    cursor.execute(
        "SELECT requests FROM usage WHERE shop_id=?",
        (shop_id,)
    )
    result = cursor.fetchone()

    if not result:
        cursor.execute("INSERT INTO usage VALUES (?, ?)", (shop_id, 0))
        conn.commit()
        requests = 0
    else:
        requests = result[0]

    if requests >= 100:
        raise HTTPException(status_code=429, detail="API limit reached")

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

    cursor.execute(
        "INSERT INTO logs VALUES (?, ?, ?, ?)",
        (str(uuid.uuid4()), shop_id, datetime.utcnow().isoformat(), float(prediction))
    )

    cursor.execute("""
        UPDATE usage
        SET requests = requests + 1
        WHERE shop_id = ?
    """, (shop_id,))

    conn.commit()

    return {
        "shop": shop_id,
        "prediction": float(prediction)
    }
@app.get("/dashboard")
def dashboard():
    cursor.execute("SELECT COUNT(*) FROM shops")
    shop_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM logs")
    request_count = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(prediction) FROM logs")
    avg_prediction = cursor.fetchone()[0]

    return {
        "total_shops": shop_count,
        "total_requests": request_count,
        "avg_prediction": avg_prediction
    }
@app.get("/top_shop")
def top_shop():
    cursor.execute("""
        SELECT shop_id, COUNT(*) as requests
        FROM logs
        GROUP BY shop_id
        ORDER BY requests DESC
        LIMIT 1
    """)
    result = cursor.fetchone()

    if not result:
        return {"message": "no data yet"}

    return {
        "top_shop": result[0],
        "requests": result[1]
    }