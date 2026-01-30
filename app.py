from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import jwt
import os
import datetime
from dotenv import load_dotenv
from invoice_utils import create_invoice

# ================= LOAD ENV =================
load_dotenv()

app = Flask(__name__)
CORS(app)

JWT_SECRET = os.getenv("JWT_SECRET")

if not JWT_SECRET:
    raise ValueError("JWT_SECRET missing in .env")

# ================= HOME =================
@app.route("/")
def home():
    return "SAAC Secure Backend Running"

# ================= GENERATE INVOICE =================
@app.route("/generate-invoice", methods=["POST"])
def generate_invoice():
    try:
        data = request.json

        if not data or "items" not in data:
            return jsonify({"error": "Invalid Order Data"}), 400

        order_id, pdf_path, total = create_invoice(data)

        token_payload = {
        "file": pdf_path,
        "order": order_id,
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=30)
    }

        token = jwt.encode(token_payload, JWT_SECRET, algorithm="HS256")

        return jsonify({
            "orderId": order_id,
            "total": total,
            "token": token
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ================= DOWNLOAD =================
@app.route("/download/<token>")
def download(token):
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        file_path = decoded["file"]

        if not os.path.exists(file_path):
            return jsonify({"error": "File Not Found"}), 404

        return send_file(file_path, as_attachment=True)

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Link Expired"}), 403

    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid Link"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ================= RUN =================
if __name__ == "__main__":
    app.run()

