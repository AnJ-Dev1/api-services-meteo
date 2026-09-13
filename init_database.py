import sqlite3

connexion = sqlite3.connect("services.db")
curseur = connexion.cursor()

curseur.execute("""
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL,
    prix INTEGER NOT NULL
)
""")

curseur.execute(
    "INSERT INTO services (nom, prix) VALUES (?, ?)",
    ("Création de site web", 500)
)

curseur.execute(
    "INSERT INTO services (nom, prix) VALUES (?, ?)",
    ("Création d'API", 800)
)

connexion.commit()
connexion.close()

print("Base de données créée.")