from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

API_BASE = "http://46.250.239.109:6001/api/uids"
SESSION_COOKIE = ".eJyrVoovSC3KTcxLzStRsiopKk3VUSrKz0lVslIqLU4tUtIBU_GZKUpWRgZGEF5eYi5IPs-gLDE-I7VCqRYAP14XTw.abBAzg.i60OzIoY69rE45w_-d1EMUtAiWA"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return "OK", 200

@app.route('/claim_free_access', methods=['POST'])
def claim_free_access():
    uid = request.form.get('uid')
    if not uid:
        return jsonify({"success": False, "message": "UID IS REQUIRED!"})

    headers = {
        "Content-Type": "application/json",
        "Cookie": f"session={SESSION_COOKIE}",
        "User-Agent": "Mozilla/5.0"
    }

    payload = {
        "uid": uid,
        "duration_hours": 24,
        "cost": 0.0
    }

    try:
        resp = requests.post(API_BASE, json=payload, headers=headers, timeout=10)
        if resp.status_code in [200, 201]:
            return jsonify({"success": True, "message": f"SUCCESS! UID {uid} ACTIVATED FOR 24H."})
        elif resp.status_code == 401:
            return jsonify({"success": False, "message": "SESSION EXPIRED! UPDATE COOKIE."})
        else:
            return jsonify({"success": False, "message": f"SERVER ERROR: {resp.status_code}"})
    except Exception:
        return jsonify({"success": False, "message": "CONNECTION FAILED."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5051))
    app.run(host='0.0.0.0', port=port)