"""Layout principal du module Aigle."""
import logging
from dash import html, dcc, callback, Input, Output, ALL, ctx
import dash_bootstrap_components as dbc

import config
from src.modules.aigle.api.client import fetch_all_sites, fetch_visits, fetch_all_years
from src.modules.aigle.data.models import Site, Visit
from src.modules.aigle.components.map import create_map_component
from src.modules.aigle.components.list import create_sites_list, create_empty_list
from src.components.maps import create_map

from src.modules.aigle.components.visits_panel import create_visits_panel, create_empty_visits_panel

logger = logging.getLogger(__name__)


def get_aigle_layout():
    """Retourne le layout du module Aigle."""
    return html.Div(
        [
            # Stores
            dcc.Store(id="aigle-sites-data-store", data=None),
            dcc.Store(id="aigle-visits-data-store", data=None),
            dcc.Store(id="aigle-years-list-store", data=None),
            dcc.Store(id="aigle-selected-site-store", data=None),
            
            # Interval pour charger les données une seule fois au montage
            dcc.Interval(
                id="aigle-init-interval",
                interval=100,  # 100ms
                max_intervals=1,  # Tourne une seule fois
            ),

            # Header
            html.Div(
                [
                    html.Div(
                        [
                            html.H1("🦅 Suivi des Aires d'Aigle", style={"margin": "0"}),
                            html.P("Visualisation interactive des données du protocole de reproduction", style={"margin": "0"}),
                        ],
                        style={"flex": "1"},
                    ),
                    html.Div(
                        [
                            html.Label("Année:", style={"marginRight": "10px", "fontWeight": "500"}),
                            dcc.Dropdown(
                                id="aigle-year-selector",
                                options=[],
                                value=config.CURRENT_YEAR,
                                style={"width": "150px"},
                                clearable=False,
                            ),
                        ],
                        style={"display": "flex", "alignItems": "center"},
                    ),
                ],
                className="header",
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "padding": "1rem",
                    "borderBottom": "1px solid #ddd",
                    "flexShrink": "0",
                },
            ),

            # Layout principal
            html.Div(
                [
                    html.Div(
                        id="aigle-sites-list-container",
                        children=create_empty_list(),
                        style={
                            "flex": "0 0 25%",
                            "minHeight": "0",
                            "borderRight": "1px solid #ddd",
                            "padding": "1rem",
                            "overflowY": "auto",
                        },
                    ),
                    html.Div(
                        id="aigle-map-container",
                        children=create_map(),
                        style={"flex": "1", "minHeight": "0"},
                    ),
                    html.Div(
                        id="aigle-visits-panel",
                        children=create_empty_visits_panel(),
                        style={
                            "flex": "0 0 25%",
                            "minHeight": "0",
                            "borderLeft": "1px solid #ddd",
                            "padding": "1rem",
                            "overflowY": "auto",
                        },
                    ),
                ],
                style={"display": "flex", "gap": "0", "flex": "1", "minHeight": "0"},
            ),
        ],
        style={"height": "100vh", "display": "flex", "flexDirection": "column", "margin": "0", "padding": "0"},
    )


# --- Callbacks pour charger les données au montage de la page Aigle ---
@callback(
    Output("aigle-sites-data-store", "data"),
    Input("aigle-init-interval", "n_intervals"),
)
def aigle_load_sites(n_intervals):
    """Charge les sites au montage de la page Aigle."""
    sites = fetch_all_sites()
    return [Site.from_api(site).to_dict() for site in sites]


@callback(
    Output("aigle-years-list-store", "data"),
    Input("aigle-init-interval", "n_intervals"),
)
def aigle_load_years(n_intervals):
    """Charge les années au montage de la page Aigle."""
    return fetch_all_years()


# Callbacks Aigle
@callback(
    Output("aigle-year-selector", "options"),
    Output("aigle-year-selector", "value"),
    Input("aigle-years-list-store", "data"),
)
def aigle_update_year_options(years):
    """Met à jour les options du sélecteur d'année."""
    if not years:
        years = [config.CURRENT_YEAR]

    options = [{"label": str(year), "value": year} for year in years]
    default_year = config.CURRENT_YEAR if config.CURRENT_YEAR in years else years[0]

    return options, default_year


@callback(
    Output("aigle-map-container", "children"),
    Output("aigle-sites-list-container", "children"),
    Input("aigle-sites-data-store", "data"),
    Input("aigle-selected-site-store", "data"),
)
def aigle_update_map_and_list(sites_data, selected_site_id):
    """Met à jour la carte et la liste des aires."""
    if not sites_data:
        return create_map(), create_empty_list()

    sites = [
        Site(
            id_base_site=site["id_base_site"],
            base_site_name=site["base_site_name"],
            base_site_code=site["base_site_code"],
            discover_year=site.get("discover_year"),
            base_site_description=site.get("base_site_description"),
            altitude_min=site.get("altitude_min"),
            altitude_max=site.get("altitude_max"),
            orientation=site.get("orientation"),
            geom=site.get("geom"),
            aire_valid=site.get("aire_valid"),
        )
        for site in sites_data
    ]

    map_component = create_map_component(sites, selected_site_id)
    list_component = create_sites_list(sites, selected_site_id)

    return map_component, list_component


@callback(
    Output("aigle-visits-data-store", "data"),
    Output("aigle-visits-panel", "children"),
    Input("aigle-selected-site-store", "data"),
    Input("aigle-year-selector", "value"),
    Input("aigle-sites-data-store", "data"),
)
def aigle_load_and_display_visits(selected_site_id, year, sites_data):
    """Charge et affiche les visites d'une aire sélectionnée."""
    if not selected_site_id or not sites_data:
        return None, create_empty_visits_panel()

    site_name = None
    for site in sites_data:
        if site["id_base_site"] == selected_site_id:
            site_name = site["base_site_name"]
            break

    if not site_name:
        return None, create_empty_visits_panel()

    visits_data = fetch_visits(selected_site_id, year)

    visits = [Visit.from_api(visit) for visit in visits_data]


    panel = create_visits_panel(site_name, visits)
    visits_dict = [visit.to_dict() for visit in visits]

    return visits_dict, panel


@callback(
    Output("aigle-selected-site-store", "data"),
    Input({"type": "site-list-item", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def aigle_select_site_from_list(n_clicks):
    """Sélectionne une aire quand on clique sur la liste."""
    if not ctx.triggered:
        return None

    trigger_id = ctx.triggered_id

    if isinstance(trigger_id, dict) and trigger_id.get("type") == "site-list-item":
        return trigger_id.get("index")

    return None
