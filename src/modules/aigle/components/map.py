"""Composant carte Leaflet interactive - Module Aigle."""
from typing import Any, Dict, List, Optional
import json
import dash_leaflet as dl
from dash import html
from src.components.maps import create_map


def create_map_component(sites: List[Dict[str, Any]], selected_site_id: Optional[int] = None) -> html.Div:
    """Crée le composant carte Leaflet avec CircleMarkers.

    Args:
        sites: Liste des aires (éléments dict avec clés: id_base_site, base_site_name, base_site_code, geom, aire_valid)
        selected_site_id: ID de l'aire sélectionnée (pour highlight)

    Returns:
        Composant Dash Leaflet
    """

    markers = []
    for site in sites:
        geom_data = site.get('geom') or site.get('st_asgeojson')
        if not geom_data:
            continue

        try:
            geom = json.loads(geom_data) if isinstance(geom_data, str) else geom_data
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

        is_valid = site.get('aire_valid')
        color = "green" if is_valid else "red"
        fill_color = "green" if is_valid else "red"

        site_id = site.get('id_base_site')
        is_selected = site_id == selected_site_id
        radius = 10 if is_selected else 6
        weight = 3 if is_selected else 2
        opacity = 1.0 if is_selected else 0.7

        marker = dl.CircleMarker(
            center=[lat, lon],
            radius=radius,
            children=dl.Popup(f"{site.get('base_site_name')} ({site.get('base_site_code')})"),
            color=color,
            weight=weight,
            opacity=opacity,
            fillColor=fill_color,
            fillOpacity=0.6,
            id={"type": "map-marker", "index": site_id},
        )
        markers.append(marker)

    return create_map(
        layers=markers,
        map_id="map",
        center=[45.0, 6.2],
        zoom=8,
    )


