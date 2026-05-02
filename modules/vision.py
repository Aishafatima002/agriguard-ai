import os
import base64
import json
import io
import requests
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

HF_API_TOKEN = os.environ.get("HF_API_TOKEN")

from config import USE_REAL_VISION_MODEL, VISION_MODEL_ID


def image_to_base64(image_file) -> str:
    image_file.seek(0)
    return base64.b64encode(image_file.read()).decode("utf-8")


def classify_disease(image_file) -> dict:
    if not USE_REAL_VISION_MODEL:
        return _mock_vision_response()
    return _call_huggingface(image_file)


def _call_huggingface(image_file) -> dict:
    api_url = f"https://router.huggingface.co/hf-inference/models/{VISION_MODEL_ID}"
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "image/jpeg"
    }

    # Convert image to correct size and format
    image_file.seek(0)
    img = Image.open(image_file)
    img = img.convert("RGB")
    img = img.resize((224, 224))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    raw_bytes = buf.read()

    try:
        response = requests.post(
            api_url,
            headers=headers,
            data=raw_bytes,
            timeout=60
        )
        response.raise_for_status()
        results = response.json()

        print("HuggingFace raw response:", results)

        top = results[0] if isinstance(results, list) and results else {}
        return {
            "disease_name": top.get("label", "Unknown"),
            "confidence":   round(top.get("score", 0.0), 2),
            "crop_type":    _extract_crop(top.get("label", "")),
            "severity":     _infer_severity(top.get("score", 0.0))
        }
    except Exception as e:
        return {
            "disease_name": f"Error: {e}",
            "confidence":   0.0,
            "crop_type":    "Unknown",
            "severity":     "Unknown"
        }


def _extract_crop(label: str) -> str:
    crops = ["Tomato", "Wheat", "Rice", "Maize", "Cotton",
             "Potato", "Chili", "Apple", "Corn", "Grape",
             "Peach", "Pepper", "Strawberry", "Squash"]
    for crop in crops:
        if crop.lower() in label.lower():
            return crop
    return "Unknown Crop"


def _infer_severity(confidence: float) -> str:
    if confidence >= 0.85: return "High"
    if confidence >= 0.60: return "Medium"
    return "Low"


def _mock_vision_response() -> dict:
    with open("mock/mock_data.json") as f:
        return json.load(f)["vision"]