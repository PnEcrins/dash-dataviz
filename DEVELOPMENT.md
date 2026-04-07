# NOTES DÉVELOPPEMENT - Dash Rapaces

## ✅ Fonctionnalités Implémentées

1. **Chargement des données**
   - API 31: Toutes les aires au démarrage (sans pagination)
   - API 32: Visites chargées lazy (au clic sur une aire)
   - Extraction automatique des années disponibles

2. **Interface utilisateur**
   - Carte Leaflet avec markers et GeoJSON rendering
   - Liste complète non-paginée des aires
   - Panneau détail des visites
   - Dropdown sélection année (défaut = année courante)

3. **Interactions**
   - Clic sur aire (liste ou carte/marker) → affiche visites
   - Changement année → actualise visites si aire sélectionnée
   - Synchronisation liste/carte/détail

4. **Styling**
   - Bootstrap classique (dbc.themes.BOOTSTRAP)
   - CSS personnalisé responsive
   - Scrollbars customisées

## 🔄 Points Techniques Importants

### Callbacks Cas-clés

- `load_sites()`: Déclenché au démarrage (url pathname changed)
- `select_site_from_list()`: Pattern-matching avec ALL (dynamique)
- `load_and_display_visits()`: Dépendance multi-input (site + année)
- Stores utilisés pour garder l'état entre callbacks

### Structure des données

- Site: dataclass avec méthode `get_geom_feature()` pour GeoJSON
- Visit: dataclass avec `get_year()` et `get_formatted_date()`
- Conversion API dict → dataclass → dict (sérialisation)

## 🚀 Comment Démarrer

### Rapide

```bash
./run.sh
```

### Manuel

```bash
pip install -r requirements.txt
python3 app.py
```

L'app démarre sur http://localhost:8050

## 🔮 Améliorations Possibles (Future)

1. **Performance**
   - Cache disque avec TTL (1 jour)
   - Virtualisation liste si >500 aires
   - Requêtes parallèles pour années + aires

2. **Fonctionnalités**
   - Export données (CSV/PDF)
   - Recherche/filtre aires par nom/code
   - Statistiques (nb visites/année)
   - Affichage trends temporelles
   - Multi-sélection aires comparaison

3. **UX/UI**
   - Dark mode
   - Meilleure gestion des erreurs API
   - Toast notifications
   - Responsive mobile
   - Animations transitions

4. **Code**
   - Tests unitaires (pytest)
   - Logging plus détaillé
   - Configuration via .env (DEBUG, API_TIMEOUT)
   - Documenting docstrings

5. **Données**
   - Ajouter filtres avancés (altitude, orientation)
   - Clustering markers sur carte si >100
   - Heatmap visites par période

## 📋 Fichiers Modifiés/Créés

```
dash_rapaces/
├── app.py                    # Layout principal + callbacks
├── config.py                 # Configuration
├── requirements.txt          # Dépendances (Dash >= 3.0.4!)
├── README.md                 # Documentation
├── run.sh                    # Script démarrage
├── .gitignore
├── assets/
│   └── style.css             # CSS personnalisé
└── src/
    ├── api/
    │   └── client.py         # Requêtes GeoNature
    ├── data/
    │   └── models.py         # Dataclasses Site/Visit
    └── components/
        ├── map.py            # Composant Leaflet
        ├── list.py           # Composant liste Aires
        └── visits_panel.py   # Composant panneau Visites
```

## ⚠️ Points d'Attention

1. **CORS**: Les APIs GeoNature doivent être accessibles (vérifier pare-feu)
2. **Timeout**: API_TIMEOUT = 30s (augmenter si données volumineuses)
3. **Versions Dash**: 2.x ne compatible pas avec dbc 2.0+, utiliser 3.0.4+
4. **Zone déploiement**: Map centrée sur Alpes (45°, 6.2°), adapter zoom/center si autre région

## 🧪 Test de Base

```bash
# Vérifier imports
python3 -c "from app import app; print('✓ OK')"

# Tester API
python3 -c "from src.api.client import fetch_all_sites; sites = fetch_all_sites(); print(f'{len(sites)} sites')"

# Démarrer serveur
python3 app.py
# Accéder http://localhost:8050
```
