# API Services & Météo

API Flask permettant de gérer des services et de récupérer la météo actuelle d’une ville.

## Fonctionnalités

- Gestion de services avec SQLite ;
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
CLE_API=votre-cle-api
```

Ne jamais publier ce fichier sur GitHub.

## Lancer l’API

```bash
python3 app.py
```

L’API est alors disponible sur :

```text
http://127.0.0.1:5000
```

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

## Technologies

- Python
- Flask
- SQLite
- Requests
- Python-dotenv
- Git
- Open-Meteo API