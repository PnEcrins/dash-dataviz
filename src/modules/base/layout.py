"""Layout exemple - template prêt à copier-coller pour nouveaux modules.

Architecture:
- Responsive 3-colonnes: 25%-50%-25% desktop, empilées mobile
- Header fixe avec hauteur var(--header-h) = 56px
- Flex layout avec scroll intelligent
- Mobile-first: scroll page complète sur petit écran
"""
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc


def get_example_layout():
    """
    Template layout générique - 3 colonnes responsive.
    
    À adapter:
    1. Remplacer "example" partout par le nom du module
    2. Adapter les stores, tabs, contenu des panneaux
    3. Ajouter les callbacks nécessaires
    
    Exemple:
    --------
    def get_mon_module_layout():
        return get_example_layout(
            title="🗺️ Mon Module",
            left_panel=create_left_tabs(),
            center_panel=create_map(),
            right_panel=None,
        )
    """
    
    return html.Div(
        [
            # === STORES ===
            dcc.Store(id="example-data-store", data=None),
            dcc.Store(id="example-selected-item-store", data=None),
            
            # === INTERVALS ===
            dcc.Interval(
                id="example-init-interval",
                interval=100,  # 100ms
                max_intervals=1,  # Tourne une seule fois au montage
            ),

            # === HEADER (ID: header, hauteur fixe 56px) ===
            html.Div(
                [html.H1("📊 Module Exemple")],
                id="header",
            ),

            # === BODY PRINCIPAL (ID: body) ===
            html.Div(
                [
                    dbc.Row(
                        [
                            # Colonne gauche: tabs, filtres, liste
                            # Sur desktop: md=3 (25%)
                            # Sur mobile: width=12 (100%), empilée
                            dbc.Col(
                                [
                                    dbc.Tabs(
                                        id="example-tabs",
                                        active_tab="tab-1",
                                        children=[
                                            dbc.Tab(
                                                label="🔑 Onglet 1",
                                                tab_id="tab-1",
                                                children=html.Div([
                                                    html.P(
                                                        "Contenu du premier onglet",
                                                        className="text-muted info-block",
                                                    ),
                                                ], className="panel-body"),
                                            ),
                                            dbc.Tab(
                                                label="⚙️ Onglet 2",
                                                tab_id="tab-2",
                                                children=html.Div([
                                                    html.P(
                                                        "Contenu du deuxième onglet",
                                                        className="text-muted info-block",
                                                    ),
                                                ], className="panel-body"),
                                            ),
                                        ],
                                    ),
                                ],
                                width=12,
                                md=3,
                                className="col-panel",
                            ),
                            
                            # Colonne centrale: carte/graph principal
                            # Sur desktop: md=6 (50%)
                            # Sur mobile: width=12 (100%), hauteur responsive
                            dbc.Col(
                                [
                                    html.Div(
                                        "Votre carte ou visualisation principale",
                                        style={"padding": "1rem", "textAlign": "center", "color": "#999"},
                                    )
                                ],
                                id="map-col",
                                width=12,
                                md=6,
                            ),
                            
                            # Colonne droite: détails, infos
                            # Sur desktop: md= 3 (25%)
                            # Sur mobile: width=12 (100%), empilée
                            dbc.Col(
                                [
                                    html.Div(
                                        id="example-right-panel",
                                        children=[
                                            html.P(
                                                "Sélectionnez un élément pour voir les détails",
                                                className="text-muted info-block",
                                            ),
                                        ],
                                        className="panel-body",
                                    ),
                                ],
                                width=12,
                                md=3,
                                className="col-panel",
                            ),
                        ],
                        className="g-0 main-row",
                    )
                ],
                id="body",
            ),

            # === MODALS ===
            dbc.Modal(
                [dbc.ModalBody(html.Div(id="example-modal-content"))],
                id="example-modal",
                is_open=False,
            ),
        ],
        id="app",
    )


# === CALLBACKS EXEMPLE ===
@callback(
    Output("example-data-store", "data"),
    Input("example-init-interval", "n_intervals"),
)
def example_load_data(n_intervals):
    """Charge les données au montage du module."""
    # TODO: Remplacer par votre logique de chargement
    return {"status": "loaded"}

