"""Composant carte mailles 1km - Module Flore."""
from typing import List, Optional
import json
import dash_leaflet as dl
from dash import html
from src.modules.flore.data.models import GridCell, Observation
from config import MAP_CENTER, MAP_ZOOM


def get_danger_color(nb_observations: int) -> str:
    """Génère une couleur selon le nombre d'observations.

    Args:
        nb_observations: Nombre d'observations

    Returns:
        Code couleur hex
    """
    if nb_observations == 0:
        return "#F0F0F0"  # Gris très clair
    elif nb_observations == 1:
        return "#FFFF00"  # Jaune
    elif nb_observations == 2:
        return "#FFA500"  # Orange
    else:  # 3+
        return "#FF0000"  # Rouge


def create_legend() -> html.Div:
    """Crée une légende pour la carte."""
    return html.Div(
        [
            html.H6("Espèces en danger", style={"marginBottom": "10px", "fontWeight": "bold"}),
            html.Div([
                html.Div(
                    style={
                        "width": "20px",
                        "height": "20px",
                        "backgroundColor": "#F0F0F0",
                        "opacity": 0.5,
                        "display": "inline-block",
                        "marginRight": "8px",
                    }
                ),
                html.Span("0", style={"fontSize": "12px"}),
            ], style={"marginBottom": "5px"}),
            html.Div([
                html.Div(
                    style={
                        "width": "20px",
                        "height": "20px",
                        "backgroundColor": "#FFFF00",
                        "opacity": 0.5,
                        "display": "inline-block",
                        "marginRight": "8px",
                    }
                ),
                html.Span("1", style={"fontSize": "12px"}),
            ], style={"marginBottom": "5px"}),
            html.Div([
                html.Div(
                    style={
                        "width": "20px",
                        "height": "20px",
                        "backgroundColor": "#FFA500",
                        "opacity": 0.5,
                        "display": "inline-block",
                        "marginRight": "8px",
                    }
                ),
                html.Span("2", style={"fontSize": "12px"}),
            ], style={"marginBottom": "5px"}),
            html.Div([
                html.Div(
                    style={
                        "width": "20px",
                        "height": "20px",
                        "backgroundColor": "#FF0000",
                        "opacity": 0.5,
                        "display": "inline-block",
                        "marginRight": "8px",
                    }
                ),
                html.Span("3+", style={"fontSize": "12px"}),
            ]),
        ],
        style={
            "position": "absolute",
            "bottom": "20px",
            "right": "20px",
            "backgroundColor": "white",
            "padding": "15px",
            "borderRadius": "5px",
            "boxShadow": "0 0 15px rgba(0,0,0,0.2)",
            "zIndex": "999",
            "fontSize": "12px",
        },
    )


def create_grid_map(grid_cells: List[GridCell], observations: Optional[List[dict]] = None, mode: str = "tab-geographic") -> html.Div:
    """Crée la carte des mailles 1km colorées avec observations.

    Args:
        grid_cells: Liste des mailles à afficher
        observations: Liste des observations avec lon/lat (optionnel)
        mode: Mode d'affichage ("tab-species" ou "tab-geographic")

    Returns:
        Composant carte Leaflet
    """
    # Créer les polygones pour chaque maille
    layers = []
    for cell in grid_cells:
        if not cell.geom_4326:
            continue

        try:
            geom = json.loads(cell.geom_4326)
        except json.JSONDecodeError:
            continue

        # Déterminer la couleur selon le mode
        if mode == "tab-species":
            # Mode espèce: utiliser la couleur du cell (vert ou rouge)
            fill_color = cell.color if cell.color else "#F0F0F0"
        else:
            # Mode géographique: calculer basée sur nb_endangered_species
            fill_color = get_danger_color(cell.nb_endangered_species)

        # Créer le GeoJSON
        feature = {
            "type": "Feature",
            "properties": {
                "id": cell.id_area,
                "name": cell.area_name,
                "nb_obs": cell.nb_observations,
                "nb_endangered": cell.nb_endangered_species,
                "last_date": cell.last_observation_date.isoformat() if cell.last_observation_date else "N/A",
            },
            "geometry": geom,
        }

        geojson_layer = dl.GeoJSON(
            data=feature,
            id={"type": "grid-cell", "index": cell.id_area},
            style={
                "color": "transparent",
                "weight": 0,
                "opacity": 0,
                "fillColor": fill_color,
                "fillOpacity": 0.5,
            },
            hoverStyle={
                "color": "transparent",
                "weight": 0,
                "opacity": 0,
                "fillOpacity": 0.7,
            },
            children=dl.Popup(
                html.Div([
                    html.Strong(cell.area_name),
                    html.Br(),
                    html.Small(f"Observations: {cell.nb_observations}"),
                    html.Br(),
                    html.Small(f"Espèces en danger: {cell.nb_endangered_species}"),
                    html.Br(),
                    html.Small(f"Dernière: {cell.last_observation_date.isoformat() if cell.last_observation_date else 'N/A'}"),
                ])
            ),
        )
        layers.append(geojson_layer)

    # Ajouter les observations comme CircleMarkers
    if observations:
        for obs in observations:
            if obs.get('lon') and obs.get('lat'):
                circle = dl.CircleMarker(
                    center=[obs['lat'], obs['lon']],
                    id={"type": "observation-marker", "index": obs['id_synthese']},
                    radius=4,
                    color="blue",
                    weight=1,
                    opacity=0.7,
                    fillColor="blue",
                    fillOpacity=0.5,
                    children=dl.Popup(
                        html.Div([
                            html.Small(f"📅 {obs['date_obs']}"),
                            html.Br(),
                            html.Small(f"🔍 {obs['nom_valide']}"),
                        ])
                    ),
                )
                layers.append(circle)

    return html.Div(
        [
            dl.Map(
                [
                    dl.TileLayer(url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"),
                    *layers,
                ],
                id="flore-map",
                style={"width": "100%", "height": "100%"},
                center=MAP_CENTER,
                zoom=MAP_ZOOM,
            ),
            create_legend() if mode == "tab-geographic" else None,
        ],
        style={
            "width": "100%",
            "height": "100%",
            "position": "relative",
        },
    )


def create_empty_map() -> html.Div:
    """Crée une carte vide."""
    return html.Div(
        [
            dl.Map(
                [
                    dl.TileLayer(url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"),
                ],
                id="flore-map",
                style={"width": "100%", "height": "100%"},
                center=MAP_CENTER,
                zoom=MAP_ZOOM,
            ),
        ],
        style={
            "width": "100%",
            "height": "100%",
            "position": "relative",
        },
    )
