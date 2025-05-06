from flask import Flask, render_template, request, send_from_directory, jsonify
import qrcode
import uuid
import os
import json

app = Flask(__name__)

# Dossiers pour stocker les QR codes
QR_FOLDER = 'static/qrcodes'
os.makedirs(QR_FOLDER, exist_ok=True)

# Fichier pour stocker les utilisateurs
DATA_FILE = 'users.json'
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

# Page de scan
@app.route('/scan')
def scan():
    return render_template('scan.html')

# Vérification d'un utilisateur via son QR code
@app.route('/verify/<user_id>')
def verify(user_id):
    with open(DATA_FILE, 'r') as f:
        users = json.load(f)
    for user in users:
        if user.get('qr_code_data', '').endswith(user_id):
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

        # Génère une URL dynamique (utile pour Render)
        verify_url = f"{request.host_url}verify/{user_id}".rstrip('/')

        data = {
            'id': user_id,
            'name': name,
            'phone': phone,
            'email': email,
            'presence': presence,
            'qr_code_data': verify_url
        }

        # Sauvegarde de l'utilisateur
        with open(DATA_FILE, 'r') as f:
            users = json.load(f)
        users.append(data)
        with open(DATA_FILE, 'w') as f:
            json.dump(users, f, indent=4)

        # Traitement basé sur la présence
        if presence == 'oui' or presence == 'hesitation':
            # Génération du QR code
            qr = qrcode.make(verify_url)
            qr_path = os.path.join(QR_FOLDER, f"{user_id}.png")
            qr.save(qr_path)

            # Message personnalisé en fonction de la présence
            if presence == 'oui':
                message = "Merci pour ton inscription ! N'oublie pas d'amener ce QR code le jour de l'événement, il sera vérifié à l'entrée."
            elif presence == 'hesitation':
                message = "Merci pour ton inscription ! Nous espérons te voir à l'événement. N'oublie pas d'amener ce QR code le jour de l'événement, il sera vérifié à l'entrée."
            
            return render_template('confirm.html', name=name, qr_code='/' + qr_path, qr_filename=f"{user_id}.png", verify_url=verify_url, message=message)

        else:  # Si la personne ne sera pas présente
            message = "Merci pour ton inscription, mais comme tu ne seras pas présent(e), aucun QR code n'a été généré."
            return render_template('confirm.html', name=name, message=message)

    return render_template('index.html')

# Route pour télécharger le QR code
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(QR_FOLDER, filename, as_attachment=True)

# Lancement de l'application (compatible Render)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
