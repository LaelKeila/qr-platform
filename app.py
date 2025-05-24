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
    return """
    <html>
        <head>
            <title>Inscriptions fermées</title>
            <style>
                body {
                    margin: 0;
                    height: 100vh;
                    background-color: #FF8C00;  /* orange foncé */
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    font-family: Arial, sans-serif;
                    color: white;
                    text-align: center;
                    padding: 20px;
                }
                h2 {
                    font-size: 2.5em;
                    margin-bottom: 0.5em;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
                }
                p {
                    font-size: 1.2em;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
                }
            </style>
        </head>
        <body>
            <div>
                <h2>Désolé, aucune place disponible. 🙏</h2>
                <p>Merci pour votre enthousiasme et votre participation.<br>Que Dieu vous bénisse.</p>
            </div>
        </body>
    </html>
    """

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

@app.route('/liste-inscrits')
def liste_inscrits():
    with open(DATA_FILE, 'r') as f:
        users = json.load(f)
    return render_template('static/liste_inscrits.html', inscrits=users)

@app.route('/download-excel')
def download_excel():
    with open(DATA_FILE, 'r') as f:
        users = json.load(f)

    df = pd.DataFrame(users)
    excel_path = 'static/inscrits.xlsx'
    df.to_excel(excel_path, index=False)

    return send_file(excel_path, as_attachment=True)

@app.route('/static/inscrits.xlsx')
def serve_excel():
    return send_from_directory('static', 'inscrits.xlsx')

if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
