# app.py
from flask import Flask, render_template, request, send_from_directory, jsonify
import qrcode
import uuid
import os
import json
from datetime import datetime

app = Flask(__name__)

# Dossier pour les QR codes
QR_FOLDER = 'static/qrcodes'
os.makedirs(QR_FOLDER, exist_ok=True)

# Fichier utilisateurs
DATA_FILE = 'users.json'
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

# Nombre max d'inscriptions
MAX_PLACES = 1500

def get_remaining_spots():
    with open(DATA_FILE, 'r') as f:
        users = json.load(f)
    confirmed_users = [u for u in users if u['presence'] in ('oui', 'hesitation')]
    return MAX_PLACES - len(confirmed_users)

@app.route('/', methods=['GET', 'POST'])
def index():
    remaining_spots = get_remaining_spots()

    if request.method == 'POST':
        if remaining_spots <= 0:
            return render_template('index.html', remaining_spots=0, error="Désolé, il n'y a plus de places disponibles.")

        name = request.form['name']
        surname = request.form['surname']
        phone = request.form['phone']
        presence = request.form['presence']
        user_id = str(uuid.uuid4())

        verify_url = f"{request.host_url}verify/{user_id}".rstrip('/')

        data = {
            'id': user_id,
            'name': name,
            'surname': surname,
            'phone': phone,
            'presence': presence,
            'qr_code_data': verify_url,
            'timestamp': datetime.now().isoformat()
        }

        with open(DATA_FILE, 'r') as f:
            users = json.load(f)
        users.append(data)
        with open(DATA_FILE, 'w') as f:
            json.dump(users, f, indent=4)

        if presence in ('oui', 'hesitation'):
            qr = qrcode.make(verify_url)
            qr_path = os.path.join(QR_FOLDER, f"{user_id}.png")
            qr.save(qr_path)

            message = "Merci pour ton inscription ! N'oublie pas d'amener ce QR code le jour de l'événement."
            return render_template('confirm.html', name=name, qr_code='/static/qrcodes/' + f"{user_id}.png", message=message, verify_url=verify_url)
        else:
            message = "Merci pour ton inscription. Aucun QR code n'a été généré puisque tu ne seras pas présent(e)."
            return render_template('confirm.html', name=name, message=message)

    return render_template('index.html', remaining_spots=remaining_spots)

@app.route('/verify/<user_id>')
def verify_qr(user_id):
    with open(DATA_FILE, 'r') as f:
        users = json.load(f)
    user = next((u for u in users if u['id'] == user_id), None)
    return render_template('verify_result.html', user=user, user_id=user_id)

@app.route('/verify', methods=['GET', 'POST'])
def verify_form():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        with open(DATA_FILE, 'r') as f:
            users = json.load(f)
        user = next((u for u in users if u['id'] == user_id), None)
        return render_template('verify_result.html', user=user, user_id=user_id)
    return render_template('verify.html')

@app.route('/admin/remaining')
def admin_remaining():
    return jsonify({"places_restantes": get_remaining_spots()})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
