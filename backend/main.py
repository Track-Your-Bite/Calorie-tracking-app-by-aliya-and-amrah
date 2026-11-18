from fastapi import FastAPI
from calculator import UserMetrics, calculate_tdee

app = FastAPI(title="Calorie Tracking API", version="1.0")

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Calorie Tracker API is running successfully!"}

@app.post("/calculate-calories")
def get_calorie_targets(metrics: UserMetrics):
    return calculate_tdee(metrics)