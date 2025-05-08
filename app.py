from flask import Flask, render_template, request, send_from_directory, jsonify
import qrcode
import uuid
import os
import json
import random
import string
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

def generate_simple_id(existing_ids):
    letters = string.ascii_uppercase
    digits = '0123456789'
    all_combinations = [l + d for l in letters for d in digits]
    available_ids = list(set(all_combinations) - set(existing_ids))

    if not available_ids:
        raise ValueError("Tous les IDs simples sont déjà utilisés.")

    return random.choice(available_ids)

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

        with open(DATA_FILE, 'r') as f:
            users = json.load(f)
        existing_ids = [u['id'] for u in users]
        user_id = generate_simple_id(existing_ids)

        data = {
            'id': user_id,
            'name': name,
            'surname': surname,
            'phone': phone,
            'presence': presence,
            'qr_code_data': user_id,
            'timestamp': datetime.now().isoformat()
        }

        users.append(data)
        with open(DATA_FILE, 'w') as f:
            json.dump(users, f, indent=4)

        if presence in ('oui', 'hesitation'):
            qr = qrcode.make(user_id)
            qr_path = os.path.join(QR_FOLDER, f"{user_id}.png")
            qr.save(qr_path)

            message = f"Merci pour ton inscription ! Ton code est : {user_id}. N'oublie pas d'amener ce QR code."
            return render_template('confirm.html', name=name, qr_code='/static/qrcodes/' + f"{user_id}.png", message=message, verify_url=user_id)
        else:
            message = "Merci pour ton inscription. Aucun QR code n'a été généré puisque tu ne seras pas présent(e)."
            return render_template('confirm.html', name=name, message=message)

    return render_template('index.html', remaining_spots=remaining_spots)

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        input_id = request.form['user_id'].strip().upper()
        with open(DATA_FILE, 'r') as f:
            users = json.load(f)
        user = next((u for u in users if u['id'] == input_id), None)
        if user:
            return render_template('verify_result.html', user=user)
        else:
            return render_template('verify_result.html', error="Aucun utilisateur trouvé avec cet identifiant.")
    return render_template('verify.html')

@app.route('/admin/remaining')
def admin_remaining():
    return jsonify({"places_restantes": get_remaining_spots()})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
