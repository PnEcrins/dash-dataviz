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


def _flatten_coords(coords: Any) -> list:
    """Extrait les coordonnées [lon, lat] d'une géométrie GeoJSON récursive."""
    flat = []
    if not isinstance(coords, list):
        return flat
    if len(coords) == 0:
        return flat
    if isinstance(coords[0], (int, float)):
        return [coords] if len(coords) == 2 and all(isinstance(c, (int, float)) for c in coords) else flat
    for item in coords:
        flat.extend(_flatten_coords(item))
    return flat


def _create_popup(props: Dict[str, Any]) -> dl.Popup:
    """Crée un popup HTML avec les infos de l'observation sur plusieurs lignes."""
    content = html.Div([
        html.Div(f"📅 {props.get('date_obs', '')}"),
        html.Div(f"🔍 {props.get('nom_valide', '')}"),
        html.Div(f"👁️ {props.get('observers', '')}"),
    ])
    return dl.Popup(content, className="custom-popup")


def _create_obs_layers(feature: Dict[str, Any]) -> List[Any]:
    """Crée des composants Leaflet selon le type de géométrie. Retourne une liste de couches."""
    geom = feature.get('geometry')
    if not geom:
        return []
    
    geom_type = geom.get('type', '')
    coords = geom.get('coordinates', [])
    props = feature.get('properties', {})
    popup = _create_popup(props)
    layers = []
    
    if geom_type == 'Point':
        lat, lon = coords[1], coords[0]
        layers.append(dl.CircleMarker(center=(lat, lon), radius=6, color='blue', fill=True, 
                                     fillColor='blue', fillOpacity=0.7, weight=2, children=[popup]))
    
    elif geom_type == 'MultiPoint':
        for pt in coords:
            layers.append(dl.CircleMarker(center=(pt[1], pt[0]), radius=6, color='blue', fill=True,
                                         fillColor='blue', fillOpacity=0.7, weight=2, children=[popup]))
    
    elif geom_type == 'LineString':
        layers.append(dl.Polyline(positions=[(pt[1], pt[0]) for pt in coords], color='blue', 
                                 weight=2, children=[popup]))
    
    elif geom_type == 'MultiLineString':
        for line in coords:
            layers.append(dl.Polyline(positions=[(pt[1], pt[0]) for pt in line], color='blue', 
                                     weight=2, children=[popup]))
    
    elif geom_type == 'Polygon':
        layers.append(dl.Polygon(positions=[[(pt[1], pt[0]) for pt in ring] for ring in coords],
                                color='blue', fill=True, fillColor='blue', fillOpacity=0.3, 
                                weight=2, children=[popup]))
    
    elif geom_type == 'MultiPolygon':
        for poly in coords:
            layers.append(dl.Polygon(positions=[[(pt[1], pt[0]) for pt in ring] for ring in poly],
                                    color='blue', fill=True, fillColor='blue', fillOpacity=0.3,
                                    weight=2, children=[popup]))
    
    return layers


def create_obs_map(observations_geojson: Optional[Dict[str, Any]] = None, geom_4326: Optional[Dict] = None):
    """Affiche la maille et les observations avec leurs vraies géométries.
    
    Args:
        observations_geojson: FeatureCollection GeoJSON avec les observations
        geom_4326: Feature GeoJSON de la maille de référence
    """
    layers = []
    viewport_bounds = None
    
    # Afficher la maille EN PREMIER
    if geom_4326:
        geom = geom_4326.get('geometry', {})
        geom_type = geom.get('type', '')
        coords = geom.get('coordinates', [])
        
        flat_coords = _flatten_coords(coords)
        # Zoomer UNIQUEMENT sur la maille avec une petite marge
        if flat_coords:
            lats = [pt[1] for pt in flat_coords]
            lons = [pt[0] for pt in flat_coords]
            lat_min, lat_max = min(lats), max(lats)
            lon_min, lon_max = min(lons), max(lons)
            
            # Ajouter une marge pour éviter les problèmes de bounds trop serrés (~1km)
            margin = 0.05
            viewport_bounds = [[lat_min - margin, lon_min - margin], [lat_max + margin, lon_max + margin]]
        
        # Construire la maille comme Polygon (sinon les popup ne sont pas clickable)
        if geom_type == 'Polygon':
            layers.append(dl.Polygon(positions=[[(pt[1], pt[0]) for pt in ring] for ring in coords],
                                    color='black', fill=False, weight=2))
        elif geom_type == 'MultiPolygon':
            for poly in coords:
                layers.append(dl.Polygon(positions=[[(pt[1], pt[0]) for pt in ring] for ring in poly],
                                        color='black', fill=False, weight=2))
    
    # Ajouter les observations EN DERNIER
    if observations_geojson and observations_geojson.get('features'):
        for feature in observations_geojson['features']:
            layers.extend(_create_obs_layers(feature))
    
    return create_map(layers=layers, viewport_bounds=viewport_bounds, map_id="obs-map", height="500px")

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
                "color": "black",
                "weight": 3,
                "opacity": 1,
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