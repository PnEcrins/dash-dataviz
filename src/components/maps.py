"""Composants cartes partagés - Utilisable par tous les modules."""
import dash_leaflet as dl
from config import MAP_CENTER, MAP_ZOOM, MAP_BASE_LAYERS


def create_map(layers=None, center=None, zoom=None, map_id="map", viewport_bounds=None, height="100%"):
    """Crée une carte avec des layers.
    
    Args:
        layers: liste des composants leaflet à afficher
        center: centre de la carte [lat, lon]
        zoom: niveau de zoom
        map_id: ID unique pour la carte (par défaut "map")
        viewport_bounds: bounds pour le viewport [[min_lat, min_lon], [max_lat, max_lon]]
        height: hauteur de la carte (par défaut "100%")
    """
    if layers is None:
        layers = []
    tile_layers = [dl.TileLayer(url=url) for url in MAP_BASE_LAYERS]
    
    map_props = {
        "id": map_id,
        "style": {"width": "100%", "height": height},
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
