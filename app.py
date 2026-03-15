from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import timedelta
import requests
import os
import threading
import time

app = Flask(__name__)
app.secret_key = "tanvir_exe_premium_key"
app.permanent_session_lifetime = timedelta(hours=24)

PASTEBIN_URL = "https://pastebin.com/raw/WWxKha6K"
API_BASE = "http://46.250.239.109:6001/api/uids"
SESSION_COOKIE = ".eJyrVoovSC3KTcxLzStRsiopKk3VUSrKz0lVslIqLU4tUtIBU_GZKUpWRgZGEF5eYi5IPs-gLDE-I7VCqRYAP14XTw.abcQwg.nkv-EUH_H5EDn4OnLIbapaliEkQ"
DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL_HERE"

DURATION_MAP = {
    "DELETE": 0.01, "24H": 24, "3D": 72, "7D": 168, "15D": 360, "1M": 720, "6M": 4320
}

def keep_alive():
    while True:
        try:
            requests.get("https://uid-add-system.onrender.com", timeout=5)
        except:
            pass
        time.sleep(300)

def send_discord_log(username, uid, duration, action):
    if not DISCORD_WEBHOOK_URL.startswith("http"):
        return
    color = 0x00fff2 if action == "add" else 0x7000ff
    title = "🚀 NEW UID ACTIVATED" if action == "add" else "🔄 UID SYSTEM UPDATED"
    payload = {
        "embeds": [{
            "title": title,
            "color": color,
            "fields": [
                {"name": "👤 Admin", "value": f"`{username}`", "inline": True},
                {"name": "🆔 UID", "value": f"`{uid}`", "inline": True},
                {"name": "⏳ Expiry", "value": f"`{duration}`", "inline": True},
                {"name": "🛠️ Status", "value": f"`{action.upper()}ED`", "inline": True}
            ],
            "footer": {"text": "Developed by TANVIR | v2.0"}
        }]
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
    except:
        pass

def get_remote_users():
    try:
        response = requests.get(PASTEBIN_URL, timeout=5)
        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            user_db = {}
            for line in lines:
                if ':' in line:
                    u, p = line.split(':')
                    user_db[u.strip()] = p.strip()
            return user_db
    except:
        return {}
    return {}

@app.route('/')
def home():
    if 'logged_in' in session:
        return render_template('index.html')
    return render_template('login.html')

@app.route('/', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    allowed_users = get_remote_users()
    if username in allowed_users and allowed_users[username] == password:
        session.permanent = True
        session['logged_in'] = True
        session['user'] = username
        session['pass'] = password
        return redirect(url_for('home'))
    return render_template('login.html', error="Invalid Credentials")

@app.route('/api/user_info')
def user_info():
    if 'logged_in' in session:
        return jsonify({"username": session.get('user'), "password": session.get('pass')})
    return jsonify({"error": "Unauthorized"}), 401

@app.route('/api/manage', methods=['POST'])
def manage_uid():
    if 'logged_in' not in session:
        return jsonify({"success": False, "message": "UNAUTHORIZED ACCESS"})
    data = request.json
    uid, duration_key, action = data.get('uid'), data.get('duration'), data.get('type')
    hours = DURATION_MAP.get(duration_key, 24)
    headers = {"Content-Type": "application/json", "Cookie": f"session={SESSION_COOKIE}"}
    payload = {"uid": uid, "duration_hours": hours, "cost": 0.0}
    try:
        if action == 'add':
            resp = requests.post(API_BASE, json=payload, headers=headers, timeout=10)
        else:
            resp = requests.put(f"{API_BASE}/{uid}", json=payload, headers=headers, timeout=10)
        if resp.status_code in [200, 201]:
            send_discord_log(session.get('user'), uid, duration_key, action)
            return jsonify({"success": True, "message": f"UID {uid} SUCCESS!"})
        return jsonify({"success": False, "message": "API REJECTED"})
    except:
        return jsonify({"success": False, "message": "CONNECTION ERROR"})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    threading.Thread(target=keep_alive, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
