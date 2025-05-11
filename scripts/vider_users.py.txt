import json

# Ouvrir le fichier 'users.json' et le vider
with open('users.json', 'w') as f:
    json.dump([], f)  # Réinitialiser à une liste vide
