"""Composant carte mailles 1km - Module Flore."""
from typing import List, Optional
import json
import dash_leaflet as dl
from dash import html
from src.modules.flore.data.models import GridCell, Observation
from config import MAP_CENTER, MAP_ZOOM, MAP_BASE_LAYERS


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


def create_map(layers=None, center=None, zoom=None, map_id="map", viewport_bounds=None):
    """Crée une carte avec des layers.
    
    Args:
        layers: liste des composants leaflet à afficher
        center: centre de la carte [lat, lon]
        zoom: niveau de zoom
        map_id: ID unique pour la carte (par défaut "map")
        viewport_bounds: bounds pour le viewport [[min_lat, min_lon], [max_lat, max_lon]]
    """
    if layers is None:
        layers = []
    tile_layers = [dl.TileLayer(url=url) for url in MAP_BASE_LAYERS]
    
    map_props = {
        "id": map_id,
        "style": {"width": "100%", "height": "500px"},  # Hauteur explicite
        "children": tile_layers + layers,
    }
    
    # Utiliser viewport avec bounds si fourni (calcule automatiquement le zoom)
    if viewport_bounds:
        map_props["center"] = center if center is not None else MAP_CENTER
        map_props["zoom"] = 1  # Zoom minimal pour initialiser, viewport prendra le dessus
        map_props["viewport"] = {"bounds": viewport_bounds}
    else:
        # Sans bounds, utiliser center et zoom fournis
        map_props["center"] = center if center is not None else MAP_CENTER
        map_props["zoom"] = zoom if zoom is not None else MAP_ZOOM
    
    return dl.Map(**map_props)

def create_obs_map(observations: List[Observation], geom_4326: str = None):
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
                )
            )


    # Ajoute les observations
    if observations:
        for _obs in observations:
            obs = _obs.to_dict()
            if obs.get('lon') and obs.get('lat'):
                layers.append(
                    dl.CircleMarker(
                        center=[obs['lat'], obs['lon']],
                        radius=5,
                        color="blue",
                        fill=True,
                        fillOpacity=0.7,
                        children=dl.Popup(html.Div([
                            html.Small(f"📅 {obs.get('date_obs', '')}"),
                            html.Br(),
                            html.Small(f"🔍 {obs.get('nom_valide', '')}"),
                        ]))
                    )
                )
    
    # Utiliser la nouvelle fonction create_map avec les bounds
    return create_map(
        layers=layers,
        viewport_bounds=viewport_bounds,
        map_id="obs-map",
    )

def create_grid_map(grid_cells: List[GridCell], mode: str = "tab-geographic") -> html.Div:
    """Crée la carte des mailles 1km colorées avec observations.

    Args:
        grid_cells: Liste des mailles à afficher
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
            fill_color = cell.color if cell.color else "#F0F0F0"
        else:
            fill_color = get_grid_color(cell.nb_unrecontacted_species_species)
        feature = {
            "type": "Feature",
            "properties": {
                "id": cell.id_area,
                "name": cell.area_name,
                "nb_obs": cell.nb_observations,
                "nb_unrecontacted_species": cell.nb_unrecontacted_species_species,
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
                    html.Small(f"Espèce(s) non recontactée(s) ces 10 dernières années: {cell.nb_unrecontacted_species_species}"),
                    html.Br(),
                    html.Small(f"Dernière: {cell.last_observation_date.isoformat() if cell.last_observation_date else 'N/A'}"),
                ])
            ),
        )
        layers.append(geojson_layer)

    # Utiliser la nouvelle fonction create_map
    map_component = create_map(
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