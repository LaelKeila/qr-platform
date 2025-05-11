import json
import pandas as pd
import os

# Chemin vers ton fichier JSON et Excel
json_path = 'user.json'  # Assure-toi que ce chemin est correct
excel_path = 'inscrits.xlsx'  # Le fichier Excel où les inscrits seront stockés

# Charger les données du fichier JSON
def load_json_data(json_path):
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Ajouter ou mettre à jour le fichier Excel
def update_excel_from_json(json_data, excel_path):
    # Vérifie si le fichier Excel existe déjà
    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path, engine='openpyxl')
    else:
        df = pd.DataFrame(columns=["Nom", "Prénom", "Email", "Téléphone"])

    # Convertir les données JSON en DataFrame pandas
    new_data = pd.DataFrame(json_data)

    # Ajouter les nouvelles données au DataFrame existant
    df = pd.concat([df, new_data], ignore_index=True)

    # Sauvegarder les données dans le fichier Excel
    df.to_excel(excel_path, index=False, engine='openpyxl')

# Charger les données du JSON
json_data = load_json_data(json_path)

# Si des données sont présentes, les insérer dans le fichier Excel
if json_data:
    update_excel_from_json(json_data, excel_path)
    print(f"Les données ont été mises à jour dans le fichier Excel: {excel_path}")
else:
    print("Aucune donnée trouvée dans le fichier JSON.")
