from app import app
from app import app, CLE_API


def test_liste_services():
    client = app.test_client()

    reponse = client.get("/api/services")

    assert reponse.status_code == 200

    donnees = reponse.get_json()
    assert isinstance(donnees, list)

def test_creation_sans_cle_api_refusee():
     client = app.test_client()

     reponse = client.post(
        "/api/services",
        json={
            "nom": "Service interdit",
            "prix": 100
        }
    )

     assert reponse.status_code == 401
     assert reponse.get_json()["erreur"] == "Clé API invalide ou absente."

def test_service_inexistant():
    client = app.test_client()

    reponse = client.get("/api/services/999")

    assert reponse.status_code == 404

def test_creation_prix_negatif_refusee():
    client = app.test_client()

    reponse = client.post(
        "/api/services",
        headers={"X-API-Key": CLE_API},
        json={
            "nom": "Test invalide",
            "prix": -10
        }
    )

    assert reponse.status_code == 400