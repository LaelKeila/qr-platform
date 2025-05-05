from flask import Flask, render_template, request, jsonify
import qrcode
import uuid
import os
import json

app = Flask(__name__)

# Chemins de fichiers et dossiers
QR_FOLDER = 'static/qrcodes'
os.makedirs(QR_FOLDER, exist_ok=True)

DATA_FILE = 'users.json'
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

# Page de scan
@app.route('/scan')
def scan():
    return render_template('scan.html')

# Vérification d'un utilisateur via son ID
@app.route('/verify/<user_id>')
def verify(user_id):
    with open(DATA_FILE, 'r') as f:
        users = json.load(f)
    for user in users:
        if user['id'] == user_id:
            return jsonify({'found': True, 'name': user['name']})
    return jsonify({'found': False})

# Page d'inscription
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        presence = request.form['presence']
        user_id = str(uuid.uuid4())

        data = {
            'id': user_id,
            'name': name,
            'phone': phone,
            'email': email,
            'presence': presence
        }

        # Sauvegarde de l'utilisateur
        with open(DATA_FILE, 'r') as f:
            users = json.load(f)
        users.append(data)
        with open(DATA_FILE, 'w') as f:
            json.dump(users, f, indent=4)

        # URL de vérification à encoder dans le QR code
        verify_url = f"http://127.0.0.1:5000/verify/{user_id}"

        # Génération du QR code avec l'URL complète
        qr = qrcode.make(verify_url)
        qr_path = os.path.join(QR_FOLDER, f"{user_id}.png")
        qr.save(qr_path)

        return render_template('confirm.html', name=name, qr_code='/' + qr_path, verify_url=verify_url)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
