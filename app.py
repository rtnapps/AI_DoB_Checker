from flask import Flask, request, jsonify
import requests
import cv2
import numpy as np
import easyocr
from PIL import Image
import os
from ultralytics import YOLO

# Set up persistent storage path for Azure Web App
# /home is persistent in Azure App Service
# STORAGE_PATH = "/home/EasyOCR"
# os.makedirs(STORAGE_PATH, exist_ok=True)
# os.environ["EASYOCR_CACHE_DIR"] = STORAGE_PATH
# os.environ["EASYOCR_DOWNLOAD_DIR"] = STORAGE_PATH

# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# Load YOLO model locally
MODEL_PATH = "dob_model_v1.pt"  # Update to your actual path
yolo_model = YOLO(MODEL_PATH)

# Flask app
app = Flask(__name__)

# Roboflow API credentials
API_KEY = os.getenv("API_KEY")  # Set your API key as an environment variable
MODEL_ID = "driving_license-08fcm"
MODEL_VERSION = "4"

# Initialize EasyOCR reader

# Path to your downloaded model file
MODEL_PATH = "model"  # Update this path to where you downloaded the model

# Initialize EasyOCR reader with custom model storage directory
reader = easyocr.Reader(
    ["en"],
    model_storage_directory=MODEL_PATH,
    download_enabled=False  # Prevent automatic downloading
)

# reader = None

# def get_reader():
#     global reader
#     if reader is None:
#         print(f"Initializing EasyOCR with cache dir: {STORAGE_PATH}")
#         reader = easyocr.Reader(["en"], model_storage_directory=STORAGE_PATH)
#     return reader

# def extract_dob_text(image_np):
#     # Encode image
#     _, image_encoded = cv2.imencode(".jpg", image_np)
#     image_bytes = image_encoded.tobytes()
    
#     # Send to Roboflow
#     url = f"https://detect.roboflow.com/{MODEL_ID}/{MODEL_VERSION}?api_key={API_KEY}"
#     response = requests.post(url, files={"file": image_bytes})
#     if response.status_code != 200:
#         return response.status_code
#         # return "Error: Roboflow API request failed"
    
#     predictions = response.json()
#     for pred in predictions.get("predictions", []):
#         if pred["class"] == "Dateofbirth":
#             x, y, w, h = int(pred["x"]), int(pred["y"]), int(pred["width"]), int(pred["height"])
#             crop = image_np[y - h // 2 : y + h // 2, x - w // 2 : x + w // 2]
#             gray_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
#             result = get_reader().readtext(gray_crop, allowlist='0123456789/')
#             return " ".join([res[1] for res in result]) or "DOB not detected"
    
#     return "DOB not detected"

def extract_dob_text(image_np):
    results = yolo_model(image_np)
    boxes = results[0].boxes

    for box in boxes:
        cls = int(box.cls.item())  # class 0 = dob, 1 = photo
        if cls == 0:  # Only look for DOB
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            crop = image_np[y1:y2, x1:x2]
            gray_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            result = reader.readtext(gray_crop, allowlist='0123456789/')
            return " ".join([res[1] for res in result]) or "DOB not detected"

    return "DOB not detected"
  
@app.route("/extract-dob", methods=["POST"])
def extract_dob():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    file = request.files["image"]
    image = Image.open(file.stream).convert("RGB")
    image_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    dob_text = extract_dob_text(image_np)
    return jsonify({"dob": dob_text})

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "cache_dir": STORAGE_PATH})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
