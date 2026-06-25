import numpy as np
from sklearn.linear_model import LinearRegression
import joblib

X = np.array([
    [10, 1, 2, 50, 0, 2.0, 5.0],
    [12, 2, 3, 60, 1, 2.5, 6.0],
    [18, 3, 2, 70, 1, 3.0, 7.0],
    [20, 4, 4, 80, 0, 3.5, 8.0],
])

y = np.array([15, 18, 22, 28])

model = LinearRegression()
model.fit(X, y)

joblib.dump(model, "model.pkl")

print("Model trained and saved")