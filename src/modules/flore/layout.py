"""Layout principal du module Flore."""
import logging
from dash import html, dcc, callback, Input, Output, State, ctx, ALL
from dash.exceptions import PreventUpdate
import dash
import dash_bootstrap_components as dbc

from src.modules.flore.api.client import (
    get_priority_flora_taxa,
    get_observations_by_grid,
    get_observations_of_cd_nom,
    get_all_grid_unrecontacted,
    get_unrecontacted_species_in_grid,
    get_grid_geometry,
)
from src.modules.flore.components.taxon_selector import create_taxon_selector
from src.modules.flore.components.map import create_grid_map, create_obs_map
from src.modules.flore.components.map import _create_map
from src.modules.flore.components.unrecontacted_species_panel import create_unrecontacted_species_panel, create_empty_endangered_species_panel


logger = logging.getLogger(__name__)


def get_flore_layout():
    """Retourne le layout du module Flore."""
    return html.Div([
        # Stores
        dcc.Store(id="flore-grids-store", data=None),
        dcc.Store(id="flore-all-grids-store", data=None),
        dcc.Store(id="current_id_area", data=None),
        dcc.Store(id="current-selected-taxon-store", data=None),
        dcc.Store(id="flore-selected-species-geo-store", data=None),

        # Header
        html.Div([
            html.H1("🌿 Flore Prioritaire"),
        ], id="flore-header"),

        # Body principal
        html.Div([
            dbc.Row([
                # Colonne gauche (tabs)
                dbc.Col([
                    dbc.Tabs(
                        id="flore-left-tabs",
                        active_tab="tab-geographic",
                        children=[
                            dbc.Tab(
                                label="🗺️ Entrée géographique",
                                tab_id="tab-geographic",
                                children=html.Div([
                                    html.P(
                                        "Affichage de toutes les mailles ayant des espèces prioritaires non recontactées ces 10 dernières années",
                                        className="text-muted flore-info-block",
                                    ),
                                    html.P(
                                        "Cliquez sur une maille pour voir la liste d'espèces non recontactées",
                                        className="text-muted flore-info-block",
                                    ),
                                    html.P(
                                        "Cliquez sur l'espèce dans le panneau latéral de droite pour voir les observations précises de l'espèce",
                                        className="text-muted flore-info-block",
                                    ),
                                ], className="flore-panel-body"),
                            ),
                            dbc.Tab(
                                label="🔍 Entrée espèce",
                                tab_id="tab-species",
                                children=html.Div([
                                    html.Div(
                                        id="flore-selector-container",
                                        children=create_taxon_selector([]),
                                    ),
                                    html.P(
                                        "Les mailles vertes correspondent aux mailles où l'espèce a été vue il y a moins de 10 ans, et les mailles rouges à celles où l'espèce n'a pas été vue ces 10 dernières années.",
                                        className="text-muted flore-info-block",
                                    ),
                                    html.P(
                                        "Cliquez sur une maille pour voir les observations de l'espèce en point",
                                        className="text-muted flore-info-block",
                                    ),
                                ], className="flore-panel-body"),
                            ),
                        ],
                    ),
                ], width=12, md=3, className="flore-col-panel"),

                # Carte (centrale)
                dbc.Col(
                    id="flore-map-col",
                    children=_create_map(),
                    width=12, md=6,
                ),

                # Panneau droit
                dbc.Col(
                    id="flore-right-panel",
                    children=None,
                    width=12, md=3,
                    className="flore-col-panel",
                ),
            ], className="g-0 flore-main-row"),
        ], id="flore-body"),

        dbc.Modal([
            dbc.ModalBody(
                html.Div(id="modal-map-container")  # Carte des observation pour un cd_nom
            )
        ], id="modal", is_open=False),

        # Interval pour charger les taxons une seule fois au montage
        dcc.Interval(
            id="flore-init-interval",
            interval=100,  # 100ms
            max_intervals=1,  # Tourne une seule fois
        ),
    ], id="flore-app")

# --- Callback pour charger les taxons au montage de la page Flore ---
@callback(
    Output("flore-selector-container", "children"),
    Input("flore-init-interval", "n_intervals"),
)
def load_taxa_on_page_mount(n_intervals):
    """Charge les taxons prioritaires au montage de la page Flore et met à jour l'input select"""
    taxa = get_priority_flora_taxa()
    return create_taxon_selector(taxa)


# --- Mode espèce : charger les grilles pour le taxon sélectionné ---
@callback(
    Output("flore-grids-store", "data"),
    Input("current-selected-taxon-store", "data"),
    Input("flore-left-tabs", "active_tab"),
)
def flore_load_grids_species(cd_nom, active_tab):
    """Charge les grilles pour le taxon sélectionné (mode espèce uniquement)."""
    if active_tab != "tab-species":
        return None
    if not cd_nom:
        return None
    grid_cells = get_observations_by_grid(cd_nom)
    if not grid_cells:
        logger.warning(f"Aucune maille trouvée pour taxon {cd_nom}")
        return None
    return grid_cells

# --- Mode géographique : charger toutes les grilles en danger ---
@callback(
    Output("flore-all-grids-store", "data"),
    Input("flore-left-tabs", "active_tab"),
)
def flore_load_grids_geographic(active_tab):
    """Charge toutes les grilles en danger (mode géographique uniquement)."""
    if active_tab != "tab-geographic":
        return None
    grid_cells = get_all_grid_unrecontacted()
    if not grid_cells:
        logger.warning("Aucune maille trouvée")
        return None
    return grid_cells


# --- Carte : mode espèce ---
@callback(
    Output("flore-map-col", "children"),
    Input("flore-grids-store", "data"),
    Input("flore-left-tabs", "active_tab"),
)
def flore_update_map_species(grids_data, active_tab):
    """Met à jour la carte pour le mode espèce."""
    if active_tab != "tab-species":
        return dash.no_update
    if not grids_data:
        return _create_map()
    return create_grid_map(grids_data, "tab-species")

# --- Mode espèce : quand on clique sur une maille, affiche les observations dans la modale ---
@callback(
    Output("modal", "is_open", allow_duplicate=True),
    Output("modal-map-container", "children", allow_duplicate=True),
    Input("current_id_area", "data"),
    Input("flore-left-tabs", "active_tab"),
    State("current-selected-taxon-store", "data"),
    State("modal", "is_open"),
    prevent_initial_call=True,
)
def flore_on_grid_click_species_mode(id_area, active_tab, cd_nom, is_open):
    """Quand on clique sur une maille en mode espèce, affiche les observations du taxon sélectionné dans la modale."""
    if active_tab != "tab-species":
        return dash.no_update, dash.no_update
    if not id_area or not cd_nom:
        return dash.no_update, dash.no_update
    
    
    # Charger les observations du taxon sélectionné
    observations = get_observations_of_cd_nom(cd_nom)
    
    # Charger la géométrie de la maille sélectionnée
    geom_4326 = None
    if id_area:
        geom_4326 = get_grid_geometry(id_area)
    
    return not is_open, create_obs_map(observations, geom_4326=geom_4326)

# --- Carte : mode géographique ---
@callback(
    Output("flore-map-col", "children", allow_duplicate=True),
    Input("flore-all-grids-store", "data"),
    Input("flore-left-tabs", "active_tab"),
    prevent_initial_call=True,
)
def flore_update_map_geographic(all_grids_data, active_tab):
    """Met à jour la carte pour le mode géographique."""
    if active_tab != "tab-geographic":
        return dash.no_update
    if not all_grids_data:
        return _create_map()
    return create_grid_map(all_grids_data, "tab-geographic")


@callback(
    Output("current-selected-taxon-store", "data"),
    Input("flore-taxon-selector", "value"),
)
def flore_on_taxon_change(cd_nom):
    """Quand le taxon sélectionné change."""
    return cd_nom


@callback(
    Output("current_id_area", "data"),
    Input({"type": "grid-cell", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def flore_on_grid_click(n_clicks):
    """Quand on clique sur une maille."""
    if all(x is None for x in n_clicks):
        return dash.no_update

    trigger_id = ctx.triggered_id
    if isinstance(trigger_id, dict) and trigger_id.get("type") == "grid-cell":
        return trigger_id.get("index")

    return None


# Panneau droit: affiche observations ou Espèce(s) non recontactée(s) ces 10 dernières années (quand on clique)

# --- Panneau droit : mode géographique ---
@callback(
    Output("flore-right-panel", "children", allow_duplicate=True),
    Input("current_id_area", "data"),
    Input("flore-all-grids-store", "data"),
    Input("flore-selected-species-geo-store", "data"),
    Input("flore-left-tabs", "active_tab"),
    prevent_initial_call=True,
)
def flore_update_right_panel_geographic(id_area, all_grids_data, cd_nom_geo, active_tab):
    """Met à jour le panneau droit pour le mode géographique."""
    if active_tab != "tab-geographic":
        return dash.no_update
    if not id_area:
        return create_empty_endangered_species_panel()
    # Trouver le nom de la maille
    grid_name = f"Maille {id_area}"
    if all_grids_data:
        for g in all_grids_data:
            if g.get("id_area") == id_area:
                grid_name = g.get("area_name", f"Maille {id_area}")
                break
    # Sinon afficher la liste des Espèce(s) non recontactée(s) ces 10 dernières années
    endangered_species = get_unrecontacted_species_in_grid(id_area)
    if not endangered_species:
        return create_empty_endangered_species_panel()
    panel = create_unrecontacted_species_panel(grid_name, endangered_species)
    return panel


# Callback: réinitialiser la sélection quand on change de tab
@callback(
    Output("current_id_area", "data", allow_duplicate=True),
    Output("flore-selected-species-geo-store", "data", allow_duplicate=True),
    Output("flore-right-panel", "children", allow_duplicate=True),
    Input("flore-left-tabs", "active_tab"),
    prevent_initial_call=True,
)
def flore_reset_on_tab_change(active_tab):
    """Réinitialise les sélections quand on change de tab."""
    return None, None, None


@callback(
    Output("flore-selected-species-geo-store", "data", allow_duplicate=True),
    Input("current_id_area", "data"),
    prevent_initial_call=True,
)
def flore_reset_species_on_grid_change(id_area):
    """Réinitialise la sélection d'espèce quand on change de maille."""
    return None


# Callback: quand on clique sur une espèce en mode géographique
@callback(
    Output("modal", "is_open"),
    Output("modal-map-container", "children"),
    Input({"type": "unrecontacted-species-btn", "cd_nom": ALL}, "n_clicks"),
    State("modal", "is_open"),
    State("current_id_area", "data"),
)
def flore_on_species_click_geo(n_clicks, is_open, current_id_area):
    """Quand on clique sur une espèce en mode géographique."""
    # n_clicks est un tableau d'event déclenché par le click utiliasteur
    # si tous les valeur de ce tableau valent None, alors il n'y a pas eu de click utilisateur, mais un evenement déclenché par la création du composant
    if all(x is None for x in n_clicks):
        return dash.no_update, dash.no_update
    

    trigger_id = ctx.triggered_id
    if isinstance(trigger_id, dict) and trigger_id.get("type") == "unrecontacted-species-btn":
        cd_nom = trigger_id.get("cd_nom")
        
        observations = get_observations_of_cd_nom(cd_nom)
        
        # Charger la géométrie de la maille sélectionnée depuis la base de données
        geom_4326 = None
        if current_id_area:
            geom_4326 = get_grid_geometry(current_id_area)
        
        return not is_open, create_obs_map(observations, geom_4326=geom_4326)

    return dash.no_update, dash.no_update



