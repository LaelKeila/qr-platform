import json

# Vide la liste des utilisateurs
with open('users.json', 'w') as f:
    json.dump([], f, indent=4)

print("✅ Le fichier users.json a été réinitialisé.")
