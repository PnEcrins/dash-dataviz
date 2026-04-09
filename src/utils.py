"""Utilitaires pour l'application."""
from config import URL_PREFIX


def get_page_path(path: str) -> str:
    """Construit le chemin d'une page en incluant le URL_PREFIX.
    
    Args:
        path: Chemin relatif de la page (ex: '/flore', '/aigle')
        
    Returns:
        Chemin complet avec le préfixe (ex: '/dataviz/flore')
    """
    if not URL_PREFIX:
        return path
    # Normaliser : enlever le slash final du préfixe et initial du path
    prefix = URL_PREFIX.rstrip('/')
    path = path.lstrip('/')
    return f"{prefix}/{path}" if path else prefix + '/'
