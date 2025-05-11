import os

# Chemin du dossier où les QR codes sont stockés
qr_code_directory = 'static/qrcodes/'

# Supprimer tous les fichiers du dossier
for filename in os.listdir(qr_code_directory):
    file_path = os.path.join(qr_code_directory, filename)
    if os.path.isfile(file_path):
        os.remove(file_path)
