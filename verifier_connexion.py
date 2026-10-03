import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

adresse = os.environ.get("DATABASE_URL")

if not adresse:
    print("DATABASE_URL est absente du fichier .env.")
else:
    with psycopg.connect(adresse, connect_timeout=10) as connexion:
        with connexion.cursor() as curseur:
            curseur.execute("SELECT 1")
            print("Connexion réussie :", curseur.fetchone())