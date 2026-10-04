# API Services & Météo

API Flask permettant de gérer des services et de récupérer la météo actuelle d’une ville.

## Fonctionnalités

- Gestion de services avec PostgreSQL hébergé sur Neon ;
- API REST : `GET`, `POST`, `PUT`, `PATCH`, `DELETE` ;
- Validation des données et réponses d’erreur ;
- Protection des modifications par clé API ;
- Intégration avec l’API Open-Meteo ;
- Recherche météo par ville et code pays.

## Installation

Créer et activer un environnement Python :

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Installer les dépendances :

```bash
python3 -m pip install -r requirements.txt
```

Créer un fichier `.env` :

```text
CLE_API=votre-cle-api-locale
DATABASE_URL=adresse-de-connexion-neon-production
TEST_DATABASE_URL=adresse-de-connexion-neon-tests
```

- `CLE_API` : clé attendue par l’API locale pour autoriser les requêtes protégées.
- `DATABASE_URL` : adresse de connexion à la base PostgreSQL utilisée par l’application.
- `TEST_DATABASE_URL` : adresse de connexion à une branche Neon distincte, réservée aux tests automatisés.

Remplacez les valeurs d’exemple dans votre fichier `.env` par vos propres valeurs. Les adresses de connexion Neon contiennent un mot de passe : ne publiez jamais le fichier `.env` sur GitHub.

Sur Render, configurez `CLE_API` et `DATABASE_URL` dans la rubrique Environment du service. Le fichier `.env` local n’est pas transmis à Render.

## Préparer la base PostgreSQL

Après avoir configuré `DATABASE_URL` dans votre fichier `.env`, exécutez :

```bash
python init_postgres.py
```

Cette commande crée la table `services` dans la base indiquée par `DATABASE_URL` si elle n’existe pas encore. Si elle existe déjà, sa structure et ses données restent inchangées.

## Lancer l’API

```bash
python3 app.py
```

L’API est alors disponible sur :

```text
http://127.0.0.1:5000
```

## Lancer les tests

Configurez `TEST_DATABASE_URL` dans votre fichier `.env` avec l’adresse d’une branche Neon réservée aux tests, distincte de celle utilisée par l’application.

Avec l’environnement virtuel activé, exécutez :

```bash
python -m pytest -q --tb=short
```

Avant chaque test, la table `services` de la base de test est vidée, son compteur d’identifiants est réinitialisé et un service fictif est ajouté.

N’utilisez jamais la base de l’application pour ces tests : ils créent, modifient ou suppriment des données. Une vérification bloque leur exécution si les adresses configurées désignent le même hôte Neon, avec ou sans pooler.

## Routes publiques

| Méthode | URL | Description |
|---|---|---|
| `GET` | `/` | Vérifie que l’API fonctionne |
| `GET` | `/api/bonjour` | Retourne un message de bienvenue |
| `GET` | `/api/services` | Retourne tous les services |
| `GET` | `/api/services/2` | Retourne le service n°2 |
| `GET` | `/api/services?prix_max=500` | Filtre les services par prix maximum |
| `GET` | `/api/meteo/Bali?pays=ID` | Retourne la météo de Bali, Indonésie |

## Routes protégées

Ces routes nécessitent le header :

```text
X-API-Key: votre-cle-api
```

| Méthode | URL | Description |
|---|---|---|
| `POST` | `/api/services` | Crée un service |
| `PUT` | `/api/services/2` | Modifie entièrement un service |
| `PATCH` | `/api/services/2` | Modifie partiellement un service |
| `DELETE` | `/api/services/2` | Supprime un service |

## Exemple : créer un service

```bash
curl -i -X POST http://127.0.0.1:5000/api/services \
  -H "Content-Type: application/json" \
  -H "X-API-Key: votre-cle-api" \
  -d '{"nom":"Audit API","prix":300}'
```

Réponse attendue :

```json
{
  "message": "Service ajouté avec succès.",
  "service": {
    "id": 1,
    "nom": "Audit API",
    "prix": 300
  }
}
```

## Codes HTTP utilisés

| Code | Signification |
|---|---|
| `200` | Requête réussie |
| `201` | Service créé avec succès |
| `400` | Données manquantes ou invalides |
| `401` | Clé API absente ou invalide |
| `404` | Ressource introuvable |
| `502` | Service externe indisponible |

## Déploiement sur Render

Créez un Web Service relié au dépôt GitHub, avec les réglages suivants :

- Runtime : Python 3
- Build Command : `pip install -r requirements.txt`
- Start Command : `gunicorn app:app --bind 0.0.0.0:$PORT`

Dans Environment, ajoutez deux variables distinctes :

- `DATABASE_URL` : adresse de connexion à la base Neon de l’application.
- `CLE_API` : clé secrète utilisée pour protéger les routes de l’API en ligne.

La clé de l’API en ligne peut être différente de celle utilisée en local. Pour appeler une route protégée, envoyez la clé correspondant à l’environnement visé.

La table `services` doit avoir été créée dans cette base avec `init_postgres.py` avant d’utiliser les routes de gestion des services.

Ne configurez pas `TEST_DATABASE_URL` sur ce service : elle est réservée aux tests.

## Technologies

- Python
- Flask
- PostgreSQL hébergé sur Neon
- Psycopg
- Requests
- Python-dotenv
- Git
- Open-Meteo API
- Gunicorn
- Pytest
- Render