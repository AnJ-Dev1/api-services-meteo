import sqlite3

import pytest

from app import CLE_API, app


@pytest.fixture
def client(tmp_path):
    base_test = tmp_path / "services_test.db"

    connexion = sqlite3.connect(base_test)
    curseur = connexion.cursor()

    curseur.execute("""
        CREATE TABLE services (
            id INTEGER PRIMARY KEY,
            nom TEXT NOT NULL,
            prix INTEGER NOT NULL
        )
    """)

    curseur.execute(
        "INSERT INTO services (nom, prix) VALUES (?, ?)",
        ("Service de test", 100)
    )

    connexion.commit()
    connexion.close()

    ancienne_base = app.config["DATABASE"]
    app.config["DATABASE"] = str(base_test)

    try:
        with app.test_client() as client:
            yield client
    finally:
        app.config["DATABASE"] = ancienne_base


def test_liste_services(client):
    reponse = client.get("/api/services")

    assert reponse.status_code == 200
    assert reponse.get_json()[0]["nom"] == "Service de test"


def test_creation_sans_cle_api_refusee(client):
    reponse = client.post(
        "/api/services",
        json={"nom": "Service interdit", "prix": 100}
    )

    assert reponse.status_code == 401


def test_service_inexistant(client):
    reponse = client.get("/api/services/999")

    assert reponse.status_code == 404


def test_creation_prix_negatif_refusee(client):
    reponse = client.post(
        "/api/services",
        headers={"X-API-Key": CLE_API},
        json={"nom": "Test invalide", "prix": -10}
    )

    assert reponse.status_code == 400


def test_creation_service_autorisee(client):
    reponse = client.post(
        "/api/services",
        headers={"X-API-Key": CLE_API},
        json={"nom": "Nouveau service", "prix": 250}
    )

    assert reponse.status_code == 201
    assert reponse.get_json()["service"]["nom"] == "Nouveau service"