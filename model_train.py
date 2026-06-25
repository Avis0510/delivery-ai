import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor

np.random.seed(42)

X = []
y = []

for i in range(200):
    order_hour = np.random.randint(8, 22)
    weekday = np.random.randint(0, 6)
    sku_complexity = np.random.randint(1, 5)
    warehouse_load = np.random.randint(30, 100)
    express = np.random.randint(0, 2)
    pick_time = np.random.uniform(1, 5)
    shipping_time = np.random.uniform(5, 20)

    delivery_time = (
        10
        + warehouse_load * 0.1
        + sku_complexity * 1.5
        + express * (-3)
        + pick_time * 2
        + shipping_time * 0.5
        + np.random.normal(0, 2)
    )

    X.append([
        order_hour,
        weekday,
        sku_complexity,
        warehouse_load,
        express,
        pick_time,
        shipping_time
    ])

    y.append(delivery_time)

model = RandomForestRegressor(n_estimators=100)
model.fit(np.array(X), np.array(y))

joblib.dump(model, "model.pkl")

print("Better model trained")