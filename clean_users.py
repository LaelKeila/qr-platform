import json

# Chemin vers le fichier JSON
DATA_FILE = 'users.json'

# Charger les utilisateurs existants
with open(DATA_FILE, 'r') as f:
    users = json.load(f)

# Supprimer le champ 'email' de chaque utilisateur (s'il existe)
for user in users:
    user.pop('email', None)

# Réécrire le fichier sans le champ 'email'
with open(DATA_FILE, 'w') as f:
    json.dump(users, f, indent=4)

print("Tous les champs 'email' ont été supprimés du fichier users.json.")
