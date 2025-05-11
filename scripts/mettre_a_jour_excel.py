import os
import pandas as pd

# Utilisez un chemin relatif pour accéder au fichier liste_inscrits.xlsx
excel_path = os.path.join(os.getcwd(), 'scripts', 'liste_inscrits.xlsx')

# Vérifiez si le fichier existe
if os.path.exists(excel_path):
    # Lire le fichier Excel en spécifiant le moteur 'openpyxl'
    df = pd.read_excel(excel_path, engine='openpyxl')
    print("Le fichier a été chargé avec succès.")
else:
    print(f"Le fichier {excel_path} n'existe pas.")
