from pathlib import Path
from datetime import datetime, timezone
import os
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
UPLOADS = ROOT / "uploads"
UPLOADS.mkdir(exist_ok=True)
MODEL_PATH = ROOT / os.getenv("MODEL_PATH", "models/best.pt")
ALLOWED = {".jpg", ".jpeg", ".png", ".webp"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024
sensor_state = {"ph": None, "tds": None, "turbidity": None, "temperature": None,
                "updated_at": None}

@app.get("/")
def home():
    return send_from_directory(FRONTEND, "index.html")

@app.get("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(FRONTEND, filename)

@app.get("/api/status")
def status():
    return jsonify({"ok": True, "model_ready": MODEL_PATH.exists(),
                    "sensor_data": sensor_state})

@app.get("/api/sensors")
def get_sensors():
    return jsonify(sensor_state)

@app.post("/api/sensors")
def receive_sensors():
    data = request.get_json(silent=True) or request.form.to_dict()
    for key in ("ph", "tds", "turbidity", "temperature"):
        if key in data:
            try:
                sensor_state[key] = float(data[key])
            except (TypeError, ValueError):
                return jsonify({"error": f"Invalid value for {key}"}), 400
    sensor_state["updated_at"] = datetime.now(timezone.utc).isoformat()
    return jsonify({"ok": True, "received": sensor_state})

@app.post("/api/detect")
def detect():
    if "image" not in request.files:
        return jsonify({"error": "ارفق صورة في الحقل image"}), 400
    file = request.files["image"]
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED:
        return jsonify({"error": "صيغة الصورة غير مدعومة"}), 400
    filename = secure_filename(file.filename) or "upload" + suffix
    saved = UPLOADS / filename
    file.save(saved)

    if not MODEL_PATH.exists():
        return jsonify({"error": "ملف النموذج غير موجود. ضع best.pt داخل models/",
                        "uploaded": filename, "model_ready": False}), 503
    try:
        from ultralytics import YOLO
        model = YOLO(str(MODEL_PATH))
        result = model.predict(str(saved), conf=0.25, verbose=False)[0]
        detections = []
        for box in result.boxes:
            class_id = int(box.cls[0])
            detections.append({"class": model.names[class_id],
                               "confidence": round(float(box.conf[0]), 4),
                               "xyxy": [round(float(v), 1) for v in box.xyxy[0].tolist()]})
        output_path = Path(result.save_dir) / saved.name
        return jsonify({"ok": True, "detections": detections,
                        "image_url": f"/uploads/{saved.name}",
                        "annotated_path": str(output_path)})
    except Exception as exc:
        return jsonify({"error": f"فشل التحليل: {exc}"}), 500

@app.get("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOADS, filename)

if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))
    app.run(host=host, port=port, debug=True)
