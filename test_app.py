import os
import psycopg

from unittest.mock import Mock, patch

from psycopg.conninfo import conninfo_to_dict

import requests

import pytest

from app import CLE_API, app

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

def verifier_base_test():
    if not TEST_DATABASE_URL:
        raise RuntimeError("TEST_DATABASE_URL est absente.")

    adresse_application = app.config["DATABASE_URL"]

    if not adresse_application:
        raise RuntimeError("DATABASE_URL est absente.")

    configuration_test = conninfo_to_dict(TEST_DATABASE_URL)
    configuration_application = conninfo_to_dict(adresse_application)

    hote_test = configuration_test.get("host", "").replace("-pooler", "")
    hote_application = configuration_application.get("host", "").replace("-pooler", "")

    if not hote_test or hote_test == hote_application:
        raise RuntimeError("Les tests doivent utiliser une branche Neon distincte.")


@pytest.fixture
def client(monkeypatch):
    verifier_base_test()

    with psycopg.connect(TEST_DATABASE_URL, connect_timeout=10) as connexion:
        with connexion.cursor() as curseur:
            curseur.execute("""
                CREATE TABLE IF NOT EXISTS services (
                    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    nom TEXT NOT NULL,
                    prix INTEGER NOT NULL CHECK (prix > 0)
                )
            """)

            curseur.execute("TRUNCATE TABLE services RESTART IDENTITY")

            curseur.execute(
                "INSERT INTO services (nom, prix) VALUES (%s, %s)",
                ("Service de test", 100)
            )

    monkeypatch.setitem(
        app.config,
        "DATABASE_URL",
        TEST_DATABASE_URL
    )

    with app.test_client() as client:
        yield client


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


def test_suppression_service_autorisee(client):
    reponse = client.delete(
        "/api/services/1",
        headers={"X-API-Key": CLE_API}
    )

    assert reponse.status_code == 200

    verification = client.get("/api/services/1")
    assert verification.status_code == 404

def test_meteo_bali(client):
    fausse_reponse_geocodage = Mock()
    fausse_reponse_geocodage.json.return_value = {
        "results": [
            {
                "name": "Bali",
                "country": "Indonésie",
                "latitude": -8.4095,
                "longitude": 115.1889
            }
        ]
    }

    fausse_reponse_meteo = Mock()
    fausse_reponse_meteo.json.return_value = {
        "current": {
            "temperature_2m": 28.5,
            "wind_speed_10m": 12.0
        }
    }

    with patch(
        "app.requests.get",
        side_effect=[
            fausse_reponse_geocodage,
            fausse_reponse_meteo
        ]
    ):
        reponse = client.get("/api/meteo/Bali?pays=ID")

    assert reponse.status_code == 200
    assert reponse.get_json() == {
        "ville": "Bali",
        "pays": "Indonésie",
        "temperature": 28.5,
        "vent_km_h": 12.0
    }

def test_creation_refusee_si_cle_serveur_absente(client):
    with patch("app.CLE_API", None):
        reponse = client.post(
            "/api/services",
            json={"nom": "Service interdit", "prix": 100}
        )

    assert reponse.status_code == 401

def test_meteo_indisponible(client):
     with patch(
        "app.requests.get",
        side_effect=requests.RequestException("Open-Meteo indisponible")
    ):
        reponse = client.get("/api/meteo/Bali?pays=ID")

     assert reponse.status_code == 502
     assert reponse.get_json()["erreur"] == "Impossible de rechercher cette ville."