from pydantic import BaseModel, Field

class UserMetrics(BaseModel):
    weight_kg: float = Field(..., gt=0, description="Çəki kiloqramla")
    height_cm: float = Field(..., gt=0, description="Boy santimetrlə")
    age: int = Field(..., gt=0, description="Yaş")
    gender: str = Field(..., pattern="^(male|female)$", description="'male' və ya 'female'")
    activity_level: float = Field(..., ge=1.2, le=1.9, description="Aktivlik əmsalı (1.2 - 1.9 arası)")

def calculate_tdee(metrics: UserMetrics) -> dict:
    # Mifflin-St Jeor düsturu ilə BMR (Baza metabolizm) hesablama
    if metrics.gender.lower() == "male":
        bmr = (10 * metrics.weight_kg) + (6.25 * metrics.height_cm) - (5 * metrics.age) + 5
    else:
        bmr = (10 * metrics.weight_kg) + (6.25 * metrics.height_cm) - (5 * metrics.age) - 161

    # TDEE (Gündəlik ümumi kalori ehtiyacı)
    tdee = bmr * metrics.activity_level

    return {
        "bmr": round(bmr, 2),
        "maintenance_calories": round(tdee, 2),
        "weight_loss_calories": round(tdee - 500, 2),  # Arıqlamaq üçün
        "weight_gain_calories": round(tdee + 500, 2)   # Çəki almaq üçün
    }