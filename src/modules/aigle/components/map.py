"""Composant carte Leaflet interactive - Module Aigle."""
from typing import Any, Dict, List, Optional
import json
import dash_leaflet as dl
from dash import html
from src.modules.aigle.data.models import Site


def create_map_component(sites: List[Site], selected_site_id: Optional[int] = None) -> html.Div:
    """Crée le composant carte Leaflet avec CircleMarkers.

    Args:
        sites: Liste des aires à afficher
        selected_site_id: ID de l'aire sélectionnée (pour highlight)

    Returns:
        Composant Dash Leaflet
    """

    markers = []
    for site in sites:
        if not site.geom:
            continue

        try:
            geom = json.loads(site.geom) if isinstance(site.geom, str) else site.geom
        except json.JSONDecodeError:
            continue

        coords = None
        if geom.get("type") == "Point":
            coords = geom.get("coordinates", [])
        elif geom.get("type") == "Polygon":
            coords = geom.get("coordinates", [[]])[0]
            if coords:
                coords = coords[0]
        elif geom.get("type") == "MultiPolygon":
            coords = geom.get("coordinates", [[[[]]]])[0][0][0]

        if not coords or len(coords) < 2:
            continue

        lat, lon = coords[1], coords[0]

        is_valid = site.aire_valid
        color = "green" if is_valid else "red"
        fill_color = "green" if is_valid else "red"

        is_selected = site.id_base_site == selected_site_id
        radius = 10 if is_selected else 6
        weight = 3 if is_selected else 2
        opacity = 1.0 if is_selected else 0.7

        marker = dl.CircleMarker(
            center=[lat, lon],
            radius=radius,
            children=dl.Popup(f"{site.base_site_name} ({site.base_site_code})"),
            color=color,
            weight=weight,
            opacity=opacity,
            fillColor=fill_color,
            fillOpacity=0.6,
            id={"type": "map-marker", "index": site.id_base_site},
        )
        markers.append(marker)

    return html.Div(
        [
            dl.Map(
                [
                    dl.TileLayer(url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"),
                    *markers,
                ],
                id="map",
                style={"width": "100%", "height": "100%"},
                center=[45.0, 6.2],
                zoom=8,
            ),
        ],
        style={
            "width": "100%",
            "height": "100%",
            "position": "relative",
        },
    )


def create_empty_map() -> html.Div:
    """Crée une carte vide (utilisée au démarrage ou en cas d'erreur)."""
    return html.Div(
        [
            dl.Map(
                [
                    dl.TileLayer(url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"),
                ],
                id="map",
                style={"width": "100%", "height": "100%"},
                center=[45.0, 6.2],
                zoom=8,
            ),
        ],
        style={
            "width": "100%",
            "height": "100%",
            "position": "relative",
        },
    )
