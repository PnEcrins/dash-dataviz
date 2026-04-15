# Module Base - Layout Framework Générique

Layout framework réutilisable pour des pages avec architecture 3-colonnes + header.

## Structure

```
src/modules/base/
├── __init__.py
├── layout.py           # create_base_layout(...)
└── README.md
```

## Utilisation

### Import

```python
from src.modules.base import create_base_layout
```

### Signature

```python
create_base_layout(
    title: str,                          # Titre du header
    left_panel: Component | list,        # Conteneur gauche
    center_panel: Component | list,      # Conteneur central
    right_panel: Component | list,       # Conteneur droit
    stores: list = None,                 # dcc.Store(...)
    modals: list = None,                 # dbc.Modal(...)
    intervals: list = None,              # dcc.Interval(...)
    app_id: str = "app"                  # ID du conteneur root
) -> html.Div
```

### Exemple minimal

```python
from dash import html, dcc
import dash_bootstrap_components as dbc
from src.modules.base import create_base_layout

def get_module_layout():
    return create_base_layout(
        title="🗺️ Ma Carte",
        left_panel=html.Div("Filtres"),
        center_panel=html.Div("Carte"),
        right_panel=html.Div("Détails"),
    )
```

### Exemple complet (avec stores, modals, intervals)

```python
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from src.modules.base import create_base_layout

def get_module_layout():
    return create_base_layout(
        title="🌿 Flore Prioritaire",

        # Colonne gauche
        left_panel=dbc.Tabs([
            dbc.Tab(label="Géo", tab_id="geo", children=html.Div(...)),
            dbc.Tab(label="Espèce", tab_id="species", children=html.Div(...)),
        ], id="tabs"),

        # Colonne centrale
        center_panel=dcc.Graph(id="map"),

        # Colonne droite
        right_panel=html.Div(id="right-details", children=None),

        # Stores
        stores=[
            dcc.Store(id="data-store"),
            dcc.Store(id="selection-store"),
        ],

        # Modals
        modals=[
            dbc.Modal([
                dbc.ModalBody(html.Div(id="modal-content"))
            ], id="modal"),
        ],

        # Intervals (callbacks optionnels)
        intervals=[
            dcc.Interval(id="init-interval", interval=100, max_intervals=1),
        ],
    )

# Callbacks normaux avec @callback
@callback(
    Output("right-details", "children"),
    Input("map", "clickData"),
)
def update_right_panel(click_data):
    # ...
    pass
```

## Architecture

### Desktop (≥768px)

```
┌─────────────────────────────────────┐
│         #header (56px)              │
├───────┬─────────────────┬───────────┤
│       │                 │           │
│ col1  │     col2        │  col3     │
│(md=3) │    (md=6)       │ (md=3)    │
│       │    #map-col     │ #right-   │
│       │                 │ panel     │
│       │                 │           │
└───────┴─────────────────┴───────────┘
```

### Mobile (<768px)

```
┌─────────────────┐
│   #header       │
├─────────────────┤
│   col1 (w=12)   │
├─────────────────┤
│   col2 (w=12)   │
│   #map-col      │
├─────────────────┤
│   col3 (w=12)   │
│   #right-panel  │
└─────────────────┘
(page scroll)
```

## CSS Required

Le CSS des classes de base doit être dans `assets/style.css`:

```css
#app { display: flex; flex-direction: column; height: 100vh; }
#header { flex: 0 0 var(--header-h); ... }
#body { flex: 1 1 0; min-height: 0; }
.main-row { height: 100%; display: flex; }
.col-panel { height: 100%; display: flex; flex-direction: column; }
.panel-body { flex: 1 1 0; min-height: 0; overflow-y: auto; }
#map-col { flex: 1 1 0; min-height: 0; }
#right-panel { flex: 1 1 0; min-height: 0; overflow-y: auto; }

@media (max-width: 767px) {
    #app { height: auto; min-height: 100dvh; }
    #body { flex: none; overflow: visible; }
    .main-row { height: auto; flex-direction: column; }
    .col-panel { height: auto; overflow: visible; }
    .panel-body { flex: none; height: auto; overflow-y: visible; }
    #map-col { flex: none; height: 55vw; min-height: 260px; max-height: 380px; }
    #right-panel { flex: none; height: auto; overflow-y: visible; }
}
```

## Notes

- **IDs globaux**: `header`, `body`, `map-col`, `right-panel` (statiques)
- **Classes CSS**: `col-panel`, `panel-body`, `main-row` (réutilisables)
- **Responsive**: Utilise Bootstrap `col-12 col-md-3/6` + CSS media queries
- **Flex layout**: Min-height: 0 crucial sur flex children pour overflow scrolling
- **Mobile scroll**: Sur mobile, tout passe en `flex: none; height: auto;`

## Refactoring des modules existants

Pour refactoriser un module existant (ex: flore) pour utiliser ce layout:

**Before:**

```python
# 50+ lignes de dtml.Div(), dbc.Row(), dbc.Col()
def get_flore_layout():
    return html.Div([...], id="flore-app")
```

**After:**

```python
from src.modules.base import create_base_layout

def get_flore_layout():
    return create_base_layout(
        title="🌿 Flore Prioritaire",
        left_panel=create_left_tabs(),
        center_panel=_create_map(),
        right_panel=None,  # Rempli par callback
        stores=[...],
        modals=[...],
        intervals=[...],
    )
```
