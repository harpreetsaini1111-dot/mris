import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# =========================
# BASIC ROUTES
# =========================

@app.route("/")
def home():
    # Main RIS page
    return render_template("index.html")


@app.route("/health")
def health():
    # For Cloud Run health checks
    return "OK", 200


# =========================
# RIS API ROUTES
# =========================

@app.route("/save-report", methods=["POST"])
def save_report():
    """
    Expects JSON:
    {
        "patient": {...},
        "report": "<html or text>"
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    # TEMP: just echo back
    # Later we plug Google Drive / DB here
    return jsonify({
        "status": "saved",
        "patient": data.get("patient", {}),
        "length": len(data.get("report", ""))
    })


@app.route("/load-template", methods=["GET"])
def load_template():
    """
    Later: fetch template from DB / Drive
    """
    return jsonify({
        "template": "MRI BRAIN (PLAIN)\n\nFindings:\nNormal study."
    })


# =========================
# CLOUD RUN ENTRY POINT
# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
