import os
import re
import json
import base64
from pathlib import Path
from pydantic import BaseModel, Field
from groq import Groq
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

class MacroNutrients(BaseModel):
    protein_g: float = Field(..., description="Zülal (qram)")
    carbs_g: float = Field(..., description="Karbohidrat (qram)")
    fat_g: float = Field(..., description="Yağ (qram)")

class MicroNutrients(BaseModel):
    fiber_g: float = Field(..., description="Lif / Sellüloza (qram)")
    sugar_g: float = Field(..., description="Şəkər (qram)")
    sodium_mg: float = Field(..., description="Natrium / Duz (mq)")
    key_vitamins: list[str] = Field(..., description="Əsas vitamin və minerallar")

class FoodScanResult(BaseModel):
    food_name: str = Field(..., description="Yeməyin adı")
    estimated_weight_g: float = Field(..., description="Təxmini porsiya çəkisi (qram)")
    calories: float = Field(..., description="Ümumi kalori (kkal)")
    macros: MacroNutrients
    micros: MicroNutrients
    confidence_note: str = Field(..., description="Təxminin dəqiqliyi barədə qısa qeyd")

def extract_json(text: str) -> dict:
    text = text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    return json.loads(text)

def analyze_food_image(image_bytes: bytes, mime_type: str) -> dict:
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise ValueError(f"GROQ_API_KEY tapılmadı. Yoxlanılan yol: {ENV_PATH}")

    client = Groq(api_key=groq_key)

    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{base64_image}"

    prompt = (
        "Bu şəkildəki yeməyi analiz et və cavabı YALNIZ aşağıdakı JSON strukturunda, "
        "Azərbaycan dilində qaytar (heç bir izah və ya əlavə mətn yazma):\n"
        "{\n"
        '  "food_name": "Yeməyin adı",\n'
        '  "estimated_weight_g": 250.0,\n'
        '  "calories": 300.0,\n'
        '  "macros": {\n'
        '    "protein_g": 20.0,\n'
        '    "carbs_g": 30.0,\n'
        '    "fat_g": 10.0\n'
        "  },\n"
        '  "micros": {\n'
        '    "fiber_g": 3.5,\n'
        '    "sugar_g": 4.0,\n'
        '    "sodium_mg": 450.0,\n'
        '    "key_vitamins": ["Vitamin C", "Dəmir", "Kalium"]\n'
        "  },\n"
        '  "confidence_note": "Təxminin dəqiqliyi barədə qısa qeyd"\n'
        "}"
    )

    available_ids = [m.id for m in client.models.list().data]
    vision_candidates = [
        m for m in available_ids
        if any(k in m.lower() for k in ["scout", "maverick", "vision", "llava", "pixtral", "qwen"])
    ]
    if not vision_candidates:
        vision_candidates = ["meta-llama/llama-4-scout-17b-16e-instruct"]

    errors = []
    for model_name in vision_candidates:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": data_url}},
                        ],
                    }
                ],
                temperature=0.2,
            )
            raw_text = response.choices[0].message.content
            parsed = extract_json(raw_text)
            validated = FoodScanResult.model_validate(parsed)
            return validated.model_dump()
        except Exception as e:
            errors.append(f"{model_name}: {str(e)}")
            continue

    raise RuntimeError(f"Groq AI analizi alınmadı. Aktiv modellər: {available_ids} | Xətalar: {' ; '.join(errors)}")