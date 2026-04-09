# Dash dataviz

Visualisation interactive des données issues de différentes sources (GeoNature, API etc.)

### Modules disponivles

- Visualisation des données aigle (en construction)
- Interface de visualisation et de recherche de taxons prioriatires non contactés depuis plus de 10 ans

## Installation

Créer le fichier de conf et remplissez le :

` cp config.py.sample config.py`

Installer les dépendances :

```bash
python3 -m venv venv
pip install -r requirements.txt
```

## Deploiement en prod

Le dossier `deploy` contient des exemples :

- configuration apache
- configuration systemd
