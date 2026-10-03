import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

adresse = os.environ.get("DATABASE_URL")

if not adresse:
    raise RuntimeError("DATABASE_URL est absente.")

with psycopg.connect(adresse, connect_timeout=10) as connexion:
    with connexion.cursor() as curseur:
        curseur.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                nom TEXT NOT NULL,
                prix INTEGER NOT NULL CHECK (prix > 0)
            )
        """)

print("La table services est prête.")