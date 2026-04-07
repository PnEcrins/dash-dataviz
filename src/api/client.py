"""Client pour les APIs GeoNature."""
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from config import API_SITES, API_VISITS, API_TIMEOUT

logger = logging.getLogger(__name__)


def fetch_all_sites() -> List[Dict[str, Any]]:
    """Récupère toutes les aires d'aigle en paginant.

    Returns:
        Liste de toutes les aires avec leurs géométries en GeoJSON
    """
    all_sites = []
    offset = 0
    limit = 100

    try:
        while True:
            params = {
                "limit": limit,
                "offset": offset,
            }
            response = requests.get(API_SITES, params=params, timeout=API_TIMEOUT)
            response.raise_for_status()

            data = response.json()
            # L'API retourne soit une liste directe, soit dans un wrapper "items"
            sites = data.get("items", data) if isinstance(data, dict) else data

            if not isinstance(sites, list) or len(sites) == 0:
                break

            all_sites.extend(sites)

            # Si on a reçu moins d'items que la limite, on a tout
            if len(sites) < limit:
                break

            offset += limit

        logger.info(f"✓ Chargé {len(all_sites)} aires")
        return all_sites

    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur API sites: {e}")
        return []


def fetch_visits(site_id: int, year: int) -> List[Dict[str, Any]]:
    """Récupère les visites d'une aire pour une année donnée en paginant.

    Args:
        site_id: ID de l'aire (id_base_site)
        year: Année pour le filtre

    Returns:
        Liste des visites filtrées
    """
    all_visits = []
    offset = 0
    limit = 100

    try:
        while True:
            params = {
                "id_base_site": site_id,
                "visit_date_min": f"{year}-01-01",
                "visit_date_max": f"{year}-12-31",
                "limit": limit,
                "offset": offset,
            }
            response = requests.get(API_VISITS, params=params, timeout=API_TIMEOUT)
            response.raise_for_status()

            data = response.json()
            visits = data.get("items", data) if isinstance(data, dict) else data

            if not isinstance(visits, list) or len(visits) == 0:
                break

            all_visits.extend(visits)

            if len(visits) < limit:
                break

            offset += limit

        logger.info(f"✓ Chargé {len(all_visits)} visites pour site {site_id} année {year}")
        return all_visits

    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur API visites (site={site_id}, year={year}): {e}")
        return []


def fetch_all_years() -> List[int]:
    """Récupère toutes les années disponibles dans les données de visite.

    Returns:
        Liste triée d'années disponibles
    """
    all_visits = []
    offset = 0
    limit = 100

    try:
        # Récupérer toutes les visites sans filtre d'année
        while True:
            params = {"limit": limit, "offset": offset}
            response = requests.get(API_VISITS, params=params, timeout=API_TIMEOUT)
            response.raise_for_status()

            data = response.json()
            visits = data.get("items", data) if isinstance(data, dict) else data

            if not isinstance(visits, list) or len(visits) == 0:
                break

            all_visits.extend(visits)

            if len(visits) < limit:
                break

            offset += limit

        # Extraire les années des dates de visite
        years = set()
        for visit in all_visits:
            if "visit_date" in visit and visit["visit_date"]:
                try:
                    year = int(visit["visit_date"][:4])
                    years.add(year)
                except (ValueError, TypeError):
                    continue

        return sorted(years, reverse=True)

    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur API années: {e}")
        return []
