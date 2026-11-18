from fastapi import FastAPI, UploadFile, File, HTTPException
from calculator import UserMetrics, calculate_tdee
from ai_scanner import analyze_food_image

app = FastAPI(title="Calorie Tracking API", version="1.0")

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Calorie Tracker API is running successfully!"}

@app.post("/calculate-calories")
def get_calorie_targets(metrics: UserMetrics):
    return calculate_tdee(metrics)

@app.post("/scan-food")
async def scan_food(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Zəhmət olmasa yalnız şəkil faylı (JPG, PNG və s.) yükləyin.")

    try:
        image_bytes = await file.read()
        result = analyze_food_image(image_bytes=image_bytes, mime_type=file.content_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analizi zamanı xəta baş verdi: {str(e)}")