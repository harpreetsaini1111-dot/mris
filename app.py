import os
import json
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# -------------------------------------------------
# BASE PATHS (CLOUD RUN SAFE)
# -------------------------------------------------
BASE_DIR = os.getcwd()

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "static")
)

REPORTS_DIR = os.path.join(BASE_DIR, "reports")
TEMPLATES_DATA_DIR = os.path.join(BASE_DIR, "data", "templates")
UI_DIR = os.path.join(BASE_DIR, "templates")  # UI HTML lives here

os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DATA_DIR, exist_ok=True)

# -------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

# -------------------------------------------------
# SERVE UI (RAW HTML – NO JINJA)
# -------------------------------------------------
@app.route("/")
def home():
    return send_from_directory(UI_DIR, "index.html")

# -------------------------------------------------
# LIST TEMPLATES BY MODALITY
# -------------------------------------------------
@app.route("/api/templates")
def list_templates():
    modality = request.args.get("modality", "").strip()
    path = os.path.join(TEMPLATES_DATA_DIR, modality)

    templates = []
    if os.path.isdir(path):
        for f in os.listdir(path):
            if f.endswith(".html"):
                templates.append({
                    "id": f,
                    "name": f.replace(".html", "")
                })

    return jsonify(templates)

# -------------------------------------------------
# LOAD SINGLE TEMPLATE
# -------------------------------------------------
@app.route("/api/template/<template_id>")
def load_template(template_id):
    for root, _, files in os.walk(TEMPLATES_DATA_DIR):
        if template_id in files:
            with open(os.path.join(root, template_id), encoding="utf-8") as f:
                return jsonify({"content": f.read()})
    return jsonify({"content": ""})

# -------------------------------------------------
# SAVE TYPED REPORT
# (NAME + MODALITY + DATE)
# -------------------------------------------------
@app.route("/api/save-report", methods=["POST"])
def save_report():
    data = request.get_json(force=True)

    patient = data.get("patient", "").strip()
    modality = data.get("modality", "").strip()
    date = data.get("date", "").strip()

    if not patient or not modality or not date:
        return jsonify({"error": "Patient, Modality and Date required"}), 400

    filename = f"{patient.replace(' ', '_')}__{modality}__{date}.json"
    filepath = os.path.join(REPORTS_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return jsonify({"status": "saved"})

# -------------------------------------------------
# FETCH SAVED REPORTS
# -------------------------------------------------
@app.route("/api/search")
def search_reports():
    name = request.args.get("name", "").lower()
    modality = request.args.get("modality", "").lower()
    date = request.args.get("date", "")

    results = []

    for f in os.listdir(REPORTS_DIR):
        if not f.endswith(".json"):
            continue

        fname = f.lower()

        if name and name.replace(" ", "_") not in fname:
            continue
        if modality and f"__{modality}__" not in fname:
            continue
        if date and not fname.endswith(f"{date}.json"):
            continue

        with open(os.path.join(REPORTS_DIR, f), encoding="utf-8") as jf:
            results.append(json.load(jf))

    return jsonify(results)

# -------------------------------------------------
# UPLOAD WORD REPORT (METADATA ONLY)
# -------------------------------------------------
@app.route("/api/upload-report", methods=["POST"])
def upload_report():
    file = request.files.get("file")
    patient = request.form.get("patient", "").strip()
    modality = request.form.get("modality", "").strip()
    date = request.form.get("date", "").strip()

    if not file or not patient or not modality or not date:
        return jsonify({"error": "File, Patient, Modality and Date required"}), 400

    data = {
        "patient": patient,
        "modality": modality,
        "date": date,
        "report": f"<b>Uploaded file:</b> {secure_filename(file.filename)}"
    }

    filename = f"{patient.replace(' ', '_')}__{modality}__{date}.json"
    filepath = os.path.join(REPORTS_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return jsonify({"status": "uploaded"})

# -------------------------------------------------
# WORD EXPORT (SAFE STUB)
# -------------------------------------------------
@app.route("/api/export-word", methods=["POST"])
def export_word():
    return ("Word export will be added next", 501)

# -------------------------------------------------
# LOCAL RUN (IGNORED BY CLOUD RUN)
# -------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)



