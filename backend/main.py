from fastapi import FastAPI

app = FastAPI(title="Calorie Tracking API", version="1.0")

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Calorie Tracker API is running successfully!"}