# Application Dash: Suivi des Aires d'Aigle 🦅

Visualisation interactive des données du protocole de suivi de reproduction des aires d'aigle.

## Installation

```bash
# Installer les dépendances
pip install -r requirements.txt
```

## Démarrage

```bash
# Lancer l'application
python3 app.py
```

L'application sera disponible à: **http://localhost:8050**

## Fonctionnalités

- 🗺️ **Carte Leaflet**: Affiche toutes les aires d'aigle avec leurs géométries
- 📋 **Liste des aires**: Affichage complet de toutes les aires (sans pagination)
- 📊 **Visites détaillées**: Cliquez sur une aire pour voir ses visites
- 📅 **Filtre par année**: Sélectionnez l'année pour filtrer les visites
- ⚡ **Chargement optimisé**: Lazy loading des visites au clic

## Architecture

```
src/
├── api/
│   └── client.py          # Appels API GeoNature
├── data/
│   └── models.py          # Modèles de données (Site, Visit)
└── components/
    ├── map.py             # Composant carte
    ├── list.py            # Composant liste Aires
    └── visits_panel.py    # Composant panneau visites
```

## Sources de données

- **API 31**: listes des aires d'aigle (GeoNature)
- **API 32**: listes des visites (GeoNature)

## Variables d'environnement

Créez un fichier `.env` à la racine du projet:

```
DEBUG=False
PORT=8050
HOST=127.0.0.1
```

## Appli flore :

callback à gérer pour afficher sur la carte :
flore_update_right_panel
