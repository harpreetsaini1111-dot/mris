import os
import json
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
import io

# -------------------------
# BASIC APP SETUP
# -------------------------
app = Flask(__name__)

BASE_DIR = "data"
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# -------------------------
# HOME
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")

# -------------------------
# TEMPLATE LIST (CT/MRI/USG/XRAY)
# -------------------------
@app.route("/api/templates")
def list_templates():
    modality = request.args.get("modality", "")
    path = os.path.join(TEMPLATES_DIR, modality)

    templates = []
    if os.path.isdir(path):
        for f in os.listdir(path):
            if f.endswith(".html"):
                templates.append({
                    "id": f,
                    "name": f.replace(".html", "")
                })
    return jsonify(templates)

# -------------------------
# LOAD SINGLE TEMPLATE
# -------------------------
@app.route("/api/template/<tid>")
def load_template(tid):
    for root, _, files in os.walk(TEMPLATES_DIR):
        if tid in files:
            with open(os.path.join(root, tid), encoding="utf-8") as f:
                return jsonify({"content": f.read()})
    return jsonify({"content": ""})

# -------------------------
# SAVE TYPED REPORT
# (indexed by NAME + MODALITY + DATE)
# -------------------------
@app.route("/api/save-report", methods=["POST"])
def save_report():
    data = request.get_json(force=True)

    patient = data.get("patient", "").strip()
    modality = data.get("modality", "").strip()
    date = data.get("date", "").strip()

    if not patient or not modality or not date:
        return jsonify({"error": "Patient, Modality and Date required"}), 400

    fname = f"{patient.replace(' ', '_')}__{modality}__{date}.json"
    path = os.path.join(REPORTS_DIR, fname)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return jsonify({"status": "saved"})

# -------------------------
# FETCH REPORTS
# -------------------------
@app.route("/api/search")
def search_reports():
    name = request.args.get("name", "").lower()
    modality = request.args.get("modality", "")
    date = request.args.get("date", "")

    results = []

    for f in os.listdir(REPORTS_DIR):
        if not f.endswith(".json"):
            continue

        fname = f.lower()
        if name and name.replace(" ", "_") not in fname:
            continue
        if modality and f"__{modality.lower()}__" not in fname:
            continue
        if date and not fname.endswith(f"{date}.json"):
            continue

        with open(os.path.join(REPORTS_DIR, f), encoding="utf-8") as jf:
            results.append(json.load(jf))

    return jsonify(results)

# -------------------------
# UPLOAD REPORT (DOCX)
# -------------------------
@app.route("/api/upload-report", methods=["POST"])
def upload_report():
    file = request.files.get("file")
    patient = request.form.get("patient", "").strip()
    modality = request.form.get("modality", "").strip()
    date = request.form.get("date", "").strip()

    if not file or not patient or not modality or not date:
        return jsonify({"error": "File, Patient, Modality, Date required"}), 400

    data = {
        "patient": patient,
        "modality": modality,
        "date": date,
        "report": f"<b>Uploaded file:</b> {secure_filename(file.filename)}"
    }

    fname = f"{patient.replace(' ', '_')}__{modality}__{date}.json"
    path = os.path.join(REPORTS_DIR, fname)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return jsonify({"status": "uploaded"})

# -------------------------
# EXPORT WORD (STUB FOR NOW)
# -------------------------
@app.route("/api/export-word", methods=["POST"])
def export_word():
    # Stub to prevent 500 errors
    # We will add full Word formatting later
    return ("Word export coming next", 501)

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

