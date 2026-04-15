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

## Layout de base

| Élément               | Desktop                         | Mobile                                          |
| --------------------- | ------------------------------- | ----------------------------------------------- |
| **hauteur html/body** | `100%`                          | `auto` (scroll page)                            |
| **#app**              | `height: 100vh` (figé)          | `height: auto; min-height: 100dvh`              |
| **#header**           | `flex: 0 0 56px` (fixe)         | `flex: 0 0 56px` (fixe)                         |
| **#body**             | `flex: 1 1 0` (prend reste)     | `flex: none` (sort du flex)                     |
| **.main-row**         | `height: 100%; display: flex`   | `height: auto; flex-direction: column`          |
| **.col-panel**        | `height: 100%` (fixe)           | `height: auto` (naturelle)                      |
| **.panel-body**       | `flex: 1 1 0; overflow-y: auto` | `flex: none; height: auto; overflow-y: visible` |
| **#map-col**          | `flex: 1 1 0` (responsive)      | `height: 55vw` (min: 260px, max: 380px)         |
| **#right-panel**      | `flex: 1 1 0; overflow-y: auto` | `flex: none; height: auto; overflow-y: visible` |

### Architecture

- **Desktop**: 3 colonnes côte à côte (3-6-3), hauteur fixe 100vh, scroll interne par panneau
- **Mobile**: Colonnes empilées verticalement, scroll page entière, carte proportionnelle

Voir `assets/style.css` pour les règles CSS complètes organisées par élément.

## Deploiement en prod

Le dossier `deploy` contient des exemples :

- configuration apache
- configuration systemd (à adapter)

  mkdir -p /var/log/dash-dataviz
  chown <user>:<user> /var/log/dash-dataviz
  systemctl daemon-reload
  systemctl enable dash-dataviz.service
  systemctl start dash-dataviz.service
