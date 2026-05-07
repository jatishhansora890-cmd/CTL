from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

app = Flask(__name__, template_folder='../templates')

# --- FIREBASE INITIALIZATION ---
if not firebase_admin._apps:
    try:
        # Pulling the key from Vercel Environment Variables
        key_dict = json.loads(os.environ.get("FIREBASE_KEY"))
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Firebase initialization error: {e}")

db = firestore.client()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/log_production', methods=['POST'])
def log_production():
    try:
        data = request.json
        # Standardize the timestamp for better sorting later
        db.collection("production_logs").add(data)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Required for Vercel to recognize the app
def handler(request):
    return app(request)
