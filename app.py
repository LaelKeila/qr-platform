from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import qrcode
import uuid
import os
import json
from datetime import datetime
import pandas as pd  # 📦 Pour générer le fichier Excel

app = Flask(__name__)

# Dossier pour les QR codes
QR_FOLDER = 'static/qrcodes'
os.makedirs(QR_FOLDER, exist_ok=True)

# Fichier utilisateurs
DATA_FILE = 'users.json'
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('full.html')

@app.route('/admin/remaining')
def admin_remaining():
    with open(DATA_FILE, 'r') as f:
        users = json.load(f)
    return jsonify({"inscrits": len(users)})

@app.route('/scanner')
def scanner():
    return render_template('scanner.html')

@app.route('/verify/<user_id>', methods=['GET'])
def verify(user_id):
    with open(DATA_FILE, 'r') as f:
        users = json.load(f)
    
    user = next((u for u in users if u['id'] == user_id), None)
    
    if user:
        return jsonify({"verified": True, "user": user})
    else:
        return jsonify({"verified": False})

# 🔸 Route pour afficher la liste des inscrits dans une page HTML
@app.route('/liste-inscrits')
def liste_inscrits():
    with open(DATA_FILE, 'r') as f:
        users = json.load(f)
    return render_template('static/liste_inscrits.html', inscrits=users)

# 🔸 Route pour générer et télécharger le fichier Excel
@app.route('/download-excel')
def download_excel():
    with open(DATA_FILE, 'r') as f:
        users = json.load(f)

    df = pd.DataFrame(users)
    excel_path = 'static/inscrits.xlsx'  # Le fichier Excel sera stocké dans 'static'
    df.to_excel(excel_path, index=False)

    return send_file(excel_path, as_attachment=True)

# 🔸 Route pour servir le fichier Excel directement via une URL
@app.route('/static/inscrits.xlsx')
def serve_excel():
    return send_from_directory('static', 'inscrits.xlsx')

if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
