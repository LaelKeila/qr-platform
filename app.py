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

        # Génération du code secret (exemple : une lettre + un chiffre)
        secret_code = f"{chr(65 + (len(name) % 26))}{len(surname) % 10}"

        data = {
            'id': user_id,
            'name': name,
            'surname': surname,
            'phone': phone,
            'presence': presence,
            'secret_code': secret_code,
            'timestamp': datetime.now().isoformat()
        }

        with open(DATA_FILE, 'r') as f:
            users = json.load(f)
        users.append(data)
        with open(DATA_FILE, 'w') as f:
            json.dump(users, f, indent=4)

        if presence == 'oui' or presence == 'hesitation':  # Génère un QR code uniquement si la présence est confirmée
            verify_url = f"{request.host_url}verify/{user_id}".rstrip('/')
            qr = qrcode.make(verify_url)
            qr_path = os.path.join(QR_FOLDER, f"{user_id}.png")
            qr.save(qr_path)

            message = "Merci pour ton inscription ! N'oublie pas d'amener ce QR code le jour de l'événement."
            return render_template('confirm.html', name=name, secret_code=secret_code, qr_code='/static/qrcodes/' + f"{user_id}.png", message=message)
        else:
            message = "Merci pour ton inscription. Aucun QR code n'a été généré puisque tu ne seras pas présent(e)."
            return render_template('confirm.html', name=name, secret_code=secret_code, message=message)

    return render_template('index.html', remaining_spots=remaining_spots)

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    user = None
    error = None

    if request.method == 'POST':
        # Récupère l'ID ou le code secret entré
        user_id = request.form.get('user_id')

        # Charge les utilisateurs inscrits
        with open(DATA_FILE, 'r') as f:
            users = json.load(f)

        # Cherche l'utilisateur par ID ou code secret
        user = next((u for u in users if u['id'] == user_id or u['secret_code'] == user_id), None)
        
        if not user:
            error = "Code invalide ou non trouvé."

    # Retourne la page de vérification avec les résultats ou l'erreur
    return render_template('verify.html', user=user, error=error)

@app.route('/admin/remaining')
def admin_remaining():
    return jsonify({"places_restantes": get_remaining_spots()})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
