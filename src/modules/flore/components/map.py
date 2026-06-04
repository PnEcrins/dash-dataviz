"""Composant carte mailles 1km - Module Flore."""
from typing import List, Dict, Any, Optional
import json
import dash_leaflet as dl
from dash import html
from src.components.maps import create_map
from config import MAP_CENTER, MAP_ZOOM


def _create_map(layers=None, center=None, zoom=None, map_id="map", viewport_bounds=None, height="100%"):
    return create_map(
        layers=layers,
        center=center,
        zoom=zoom,
        map_id=map_id,
        viewport_bounds=viewport_bounds,
        height=height
    )


def get_grid_color(nb_species: int) -> str:
    """Génère une couleur selon le nombre d'espèce.

    Args:
        nb_species: Nombre d'espèce dans la maille

    Returns:
        Code couleur hex
    """
    if nb_species == 0:
        return "#F0F0F0"  # Gris très clair
    elif nb_species == 1:
        return "#FFFF00"  # Jaune
    elif nb_species == 2:
        return "#FFA500"  # Orange
    else:  # 3+
        return "#FF0000"  # Rouge


def create_legend() -> html.Div:
    """Crée une légende pour la carte."""
    return html.Div(
        [
            html.P("Nombre d'espèce(s) non recontactée(s) ces 10 dernières années", style={"marginBottom": "10px", "fontWeight": "bold", "width": "70px"}),
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


def create_obs_map(observations: List[Dict[str, Any]], geom_4326: Optional[Dict] = None):
    """Affiche une carte leaflet avec la maille et les observations en points."""
    layers = []
    viewport_bounds = None
    
    # Afficher la maille si fournie et calculer les bounds
    if geom_4326:
        geojson_data = geom_4326
        # Extraire la géométrie et les coordonnées
        geom = geojson_data.get('geometry', {})
        coords = geom.get('coordinates', [])
        geom_type = geom.get('type')
        flat_coords = []
        
        # Extraire les coordonnées selon le type
        if geom_type == 'Polygon':
            for ring in coords:
                flat_coords.extend(ring)
        elif geom_type == 'MultiPolygon':
            for poly in coords:
                for ring in poly:
                    flat_coords.extend(ring)
        
        # Calculer les bounds simples
        if flat_coords:
            try:
                lats = [pt[1] for pt in flat_coords if len(pt) >= 2]
                lons = [pt[0] for pt in flat_coords if len(pt) >= 2]
                if lats and lons:
                    # Format: [[min_lat, min_lon], [max_lat, max_lon]]
                    viewport_bounds = [[min(lats), min(lons)], [max(lats), max(lons)]]
            except (TypeError, IndexError):
                pass
        
        # Ajouter la géométrie comme GeoJSON seulement si valide
        if geojson_data:
            layers.append(
                dl.GeoJSON(
                    data=geojson_data,
                    style={
                        "color": "black",
                        "weight": 2,
                        "fillColor": "transparent",
                        "fillOpacity": 0.0,
                    },
                    pane="overlayPane",
                )
            )


    # Ajoute les observations
    if observations:
        for obs in observations:
            if obs.get('lon') and obs.get('lat'):
                date_obs = obs.get('date_obs', '')
                nom = obs.get('nom_valide', '')
                layers.append(
                    dl.CircleMarker(
                        center=[obs['lat'], obs['lon']],
                        radius=5,
                        color="blue",
                        fill=True,
                        fillOpacity=0.7,
                        pane="markerPane",
                        children=[
                            dl.Popup(
                                children=[
                                    html.Div([
                                        html.Small(f"📅 {date_obs}", style={"display": "block"}),
                                        html.Small(f"🔍 {nom}", style={"display": "block", "marginTop": "5px"}),
                                        html.Small(f" Observateur : {obs.get('observers')} ", style={"display": "block", "marginTop": "5px"}),
                                    ])
                                ],
                                closeButton=True,
                                autoClose=False,
                            )
                        ],
                        n_clicks=0,
                    )
                )
    
    # Utiliser la nouvelle fonction create_map avec les bounds
    return create_map(
        layers=layers,
        viewport_bounds=viewport_bounds,
        map_id="obs-map",
        height="500px"
    )

def create_grid_map(grid_cells, mode: str = "tab-geographic") -> html.Div:
    """Crée la carte des mailles 1km Dict[str, Any]], mode: str = "tab-geographic") -> html.Div:

    Args:
        grid_cells: Liste des mailles à afficher (dicts)
        mode: Mode d'affichage ("tab-species" ou "tab-geographic")

    Returns:
        Composant carte Leaflet
    """
    # Créer les polygones pour chaque maille EN PREMIER (elles seront en arrière)
    layers = []
    for cell in grid_cells:
        if not cell.get('geom_4326'):
            continue
        try:
            geom = json.loads(cell['geom_4326']) if isinstance(cell['geom_4326'], str) else cell['geom_4326']
        except json.JSONDecodeError:
            continue
        # Déterminer la couleur selon le mode
        if mode == "tab-species":
            fill_color = cell.get('color') if cell.get('color') else "#F0F0F0"
        else:
            fill_color = get_grid_color(cell.get('nb_unrecontacted_species_species', 0))
        feature = {
            "type": "Feature",
            "properties": {
                "id": cell.get('id_area'),
                "name": cell.get('area_name'),
                "nb_obs": cell.get('nb_observations', 0),
                "nb_unrecontacted_species": cell.get('nb_unrecontacted_species_species', 0),
                "last_date": cell.get('last_observation_date') or "N/A",
            },
            "geometry": geom,
        }
        geojson_layer = dl.GeoJSON(
            data=feature,
            id={"type": "grid-cell", "index": cell.get('id_area')},
            pane="overlayPane",
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
        )
        layers.append(geojson_layer)



    # Utiliser la nouvelle fonction create_map
    map_component = _create_map(
        layers=layers,
        center=MAP_CENTER,
        zoom=MAP_ZOOM,
    )
    # Ajouter la légende si nécessaire
    if mode == "tab-geographic":
        return html.Div([
            map_component,
            create_legend(),
        ], style={"width": "100%", "height": "100%", "position": "relative"})
    else:
        return html.Div([
            map_component,
        ], style={"width": "100%", "height": "100%", "position": "relative"})