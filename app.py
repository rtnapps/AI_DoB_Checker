from flask import Flask, request, jsonify
import requests
import cv2
import numpy as np
import easyocr
from PIL import Image
import os

# Flask app
app = Flask(__name__)

# Roboflow API credentials
API_KEY = os.getenv("API_KEY")  # Set your API key as an environment variable
MODEL_ID = "driving_license-08fcm"
MODEL_VERSION = "4"

# Initialize EasyOCR reader
reader = easyocr.Reader(["en"])

def extract_dob_text(image_np):
    # Encode image
    _, image_encoded = cv2.imencode(".jpg", image_np)
    image_bytes = image_encoded.tobytes()

    # Send to Roboflow
    url = f"https://detect.roboflow.com/{MODEL_ID}/{MODEL_VERSION}?api_key={API_KEY}"
    response = requests.post(url, files={"file": image_bytes})

    if response.status_code != 200:
        return "Error: Roboflow API request failed"

    predictions = response.json()
    for pred in predictions.get("predictions", []):
        if pred["class"] == "Dateofbirth":
            x, y, w, h = int(pred["x"]), int(pred["y"]), int(pred["width"]), int(pred["height"])
            crop = image_np[y - h // 2 : y + h // 2, x - w // 2 : x + w // 2]
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

# if __name__ == "__main__":
#     app.run(debug=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)