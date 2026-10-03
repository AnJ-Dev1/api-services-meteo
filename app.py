import os
import requests
import psycopg
from psycopg.rows import dict_row
from functools import wraps
from flask import Flask, jsonify, request
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")

app = Flask(__name__)
app.config["DATABASE_URL"] = DATABASE_URL

CLE_API = os.environ.get("CLE_API")

def ouvrir_connexion():
    adresse = app.config["DATABASE_URL"]

    if not adresse:
        raise RuntimeError("DATABASE_URL est absente.")

    return psycopg.connect(
        adresse,
        row_factory=dict_row,
        connect_timeout=10
    )

def requiert_cle_api(f):
    @wraps(f)
    def fonction_protegee(*args, **kwargs):
        cle_recue = request.headers.get("X-API-Key")

        if not CLE_API or cle_recue != CLE_API:
            return jsonify(erreur="Clé API invalide ou absente."), 401

        return f(*args, **kwargs)

    return fonction_protegee


@app.route("/")
def accueil():
    return "Bonjour Angelo ! Mon API fonctionne."


@app.route("/api/bonjour")
def bonjour_api():
    return jsonify(
        message="Bonjour Angelo !",
        statut="API fonctionnelle"
    )


@app.route("/api/bonjour/<prenom>")
def bonjour_personnalise(prenom):
    return jsonify(
        message=f"Bonjour {prenom} !",
        statut="API personnalisée"
    )


@app.route("/api/services")
def liste_services():
    prix_max = request.args.get("prix_max", type=int)

    connexion = ouvrir_connexion()
    curseur = connexion.cursor()

    if prix_max is None:
        curseur.execute("SELECT id, nom, prix FROM services")
    else:
        curseur.execute(
            "SELECT id, nom, prix FROM services WHERE prix <= %s",
            (prix_max,)
        )

    services = [dict(service) for service in curseur.fetchall()]
    connexion.close()

    return jsonify(services)


@app.route("/api/services/<int:service_id>")
def detail_service(service_id):
    connexion = ouvrir_connexion()
    curseur = connexion.cursor()

    curseur.execute(
        "SELECT id, nom, prix FROM services WHERE id = %s",
        (service_id,)
    )

    service = curseur.fetchone()
    connexion.close()

    if service is None:
     return jsonify(erreur="Service introuvable."), 404

    return jsonify(dict(service))


@app.route("/api/services", methods=["POST"])
@requiert_cle_api
def creer_service():
    donnees = request.get_json(silent=True)

    if not donnees:
        return jsonify(erreur="Aucune donnée reçue."), 400

    nom = donnees.get("nom")
    prix = donnees.get("prix")

    if not nom or prix is None:
        return jsonify(erreur="Le nom et le prix sont obligatoires."), 400

    if not isinstance(prix, (int, float)) or isinstance(prix, bool) or prix <= 0:
        return jsonify(erreur="Le prix doit être un nombre positif."), 400

    connexion = ouvrir_connexion()
    curseur = connexion.cursor()

    curseur.execute(
        "INSERT INTO services (nom, prix) VALUES (%s, %s) RETURNING id",
        (nom, prix)
    )

    nouveau_service_id = curseur.fetchone()["id"]
    connexion.commit()
    connexion.close()

    return jsonify(
        message="Service ajouté avec succès.",
        service={
            "id": nouveau_service_id,
            "nom": nom,
            "prix": prix
        }
    ), 201

@app.route("/api/services/<int:service_id>", methods=["PUT"])
@requiert_cle_api
def modifier_service(service_id):
    donnees = request.get_json(silent=True)

    if not donnees:
        return jsonify(erreur="Aucune donnée reçue."), 400

    nom = donnees.get("nom")
    prix = donnees.get("prix")

    if not nom or prix is None:
        return jsonify(erreur="Le nom et le prix sont obligatoires."), 400

    if not isinstance(prix, (int, float)) or isinstance(prix, bool) or prix <= 0:
        return jsonify(erreur="Le prix doit être un nombre positif."), 400

    connexion = ouvrir_connexion()
    curseur = connexion.cursor()

    curseur.execute(
        "UPDATE services SET nom = %s, prix = %s WHERE id = %s",
        (nom, prix, service_id)
    )

    connexion.commit()
    modifie = curseur.rowcount
    connexion.close()

    if modifie == 0:
        return jsonify(erreur="Service introuvable."), 404

    return jsonify(message="Service modifié avec succès.")

@app.route("/api/services/<int:service_id>", methods=["PATCH"])
@requiert_cle_api
def modifier_partiellement_service(service_id):
    donnees = request.get_json(silent=True)

    if not donnees:
        return jsonify(erreur="Aucune donnée reçue."), 400

    if "nom" not in donnees and "prix" not in donnees:
        return jsonify(erreur="Indique au moins un champ : nom ou prix."), 400

    nom = donnees.get("nom")
    prix = donnees.get("prix")

    if nom is not None and not isinstance(nom, str):
        return jsonify(erreur="Le nom doit être du texte."), 400

    if prix is not None:
        if not isinstance(prix, (int, float)) or isinstance(prix, bool) or prix <= 0:
            return jsonify(erreur="Le prix doit être un nombre positif."), 400

    connexion = ouvrir_connexion()
    curseur = connexion.cursor()

    curseur.execute(
    "SELECT id, nom, prix FROM services WHERE id = %s",
    (service_id,)
    )
    

    service = curseur.fetchone()

    if service is None:
        connexion.close()
        return jsonify(erreur="Service introuvable."), 404

    nouveau_nom = nom if nom is not None else service["nom"]
    nouveau_prix = prix if prix is not None else service["prix"]

    curseur.execute(
        "UPDATE services SET nom = %s, prix = %s WHERE id = %s",
        (nouveau_nom, nouveau_prix, service_id)
    )

    connexion.commit()
    connexion.close()

    return jsonify(
        message="Service modifié partiellement avec succès.",
        service={
            "id": service_id,
            "nom": nouveau_nom,
            "prix": nouveau_prix
        }
    )


@app.route("/api/services/<int:service_id>", methods=["DELETE"])
@requiert_cle_api
def supprimer_service(service_id):
    
    connexion = ouvrir_connexion()
    curseur = connexion.cursor()

    curseur.execute(
        "DELETE FROM services WHERE id = %s",
        (service_id,)
    )

    connexion.commit()
    supprime = curseur.rowcount
    connexion.close()

    if supprime == 0:
        return jsonify(erreur="Service introuvable."), 404

    return jsonify(message="Service supprimé avec succès.")

@app.route("/api/meteo/<ville>")
def meteo_ville(ville):
    pays = request.args.get("pays")
    url_geocodage = "https://geocoding-api.open-meteo.com/v1/search"

    parametres_geocodage = {
        "name": ville,
        "count": 1,
        "language": "fr",
        "format": "json"
    }

    if pays:
        parametres_geocodage["countryCode"] = pays.upper()

    try:
        reponse_geocodage = requests.get(
            url_geocodage,
            params=parametres_geocodage,
            timeout=10
        )
        reponse_geocodage.raise_for_status()
    except requests.RequestException:
        return jsonify(erreur="Impossible de rechercher cette ville."), 502

    resultats = reponse_geocodage.json().get("results", [])

    if not resultats:
        return jsonify(erreur="Ville introuvable."), 404

    lieu = resultats[0]

    try:
        reponse_meteo = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lieu["latitude"],
                "longitude": lieu["longitude"],
                "current": "temperature_2m,wind_speed_10m"
            },
            timeout=10
        )
        reponse_meteo.raise_for_status()
    except requests.RequestException:
        return jsonify(erreur="Impossible de récupérer la météo."), 502

    meteo_actuelle = reponse_meteo.json()["current"]

    return jsonify(
        ville=lieu["name"],
        pays=lieu.get("country"),
        temperature=meteo_actuelle["temperature_2m"],
        vent_km_h=meteo_actuelle["wind_speed_10m"]
    )


if __name__ == "__main__":
    app.run(debug=True)