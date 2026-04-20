"""API client PostgreSQL pour module Flore."""
import json
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any

from config import DB_CONFIG, CODE_TAXHUB_LIST

logger = logging.getLogger(__name__)


def get_priority_flora_taxa() -> List[Dict[str, Any]]:
    """Récupère tous les taxons de la liste 'priority flora'."""
    query = """
    SELECT
        t.cd_nom,
        t.cd_ref,
        t.nom_valide,
        t.lb_nom,
        t.nom_vern
    FROM taxonomie.bib_listes bl
    JOIN taxonomie.cor_nom_liste cnl ON bl.id_liste = cnl.id_liste
    JOIN taxonomie.taxref t ON cnl.cd_nom = t.cd_nom
    WHERE bl.nom_liste = %s
    ORDER BY t.nom_valide
    """

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, (CODE_TAXHUB_LIST,))

        taxa = [dict(row) for row in cur.fetchall()]

        cur.close()
        conn.close()

        return taxa

    except psycopg2.Error as e:
        logger.error(f"Erreur BDD taxa: {e}")
        return []


def get_observations_by_grid(cd_nom: int) -> List[Dict[str, Any]]:
    """Récupère observations par maille 1km pour un taxon."""
    query = """
    SELECT
        la.id_area,
        la.area_name,
        ST_AsGeoJSON(la.geom_4326) as geom_4326,
        t.cd_nom,
        COUNT(DISTINCT s.id_synthese) as nb_obs,
        to_char(MAX(s.date_min::DATE), 'YYYY-MM-DD') as last_observation_date,
        CASE
            WHEN MAX(s.date_min::DATE) >= CURRENT_DATE - INTERVAL '10 years' THEN 'green'
            ELSE 'red'
        END as color
    FROM gn_synthese.synthese s
    JOIN taxonomie.taxref t ON s.cd_nom = t.cd_nom
    JOIN gn_synthese.cor_area_synthese cas ON s.id_synthese = cas.id_synthese
    JOIN ref_geo.l_areas la ON cas.id_area = la.id_area
    JOIN ref_geo.bib_areas_types bat ON la.id_type = bat.id_type
    WHERE bat.type_code = 'M1'
        AND t.cd_nom = %s
    GROUP BY la.id_area, la.area_name, la.geom_4326, t.cd_nom
    """

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, (cd_nom,))

        grid_cells = [dict(row) for row in cur.fetchall()]

        cur.close()
        conn.close()

        return grid_cells

    except psycopg2.Error as e:
        logger.error(f"Erreur BDD grid: {e}")
        return []


def get_observations_of_cd_nom(cd_nom: int) -> Dict[str, Any]:
    """Récupère les observations d'une espèce et les retourne en tant que FeatureCollection GeoJSON.
    
    Conserve la géométrie complète (point, ligne, polygone) pour affichage accurate.
    
    Args:
        cd_nom: Code du taxon
        
    Returns:
        FeatureCollection GeoJSON avec les observations
    """
    query = """
    SELECT
        s.id_synthese,
        to_char(s.date_min::DATE, 'YYYY-MM-DD') as date_obs,
        s.observers,
        s.comment_description,
        t.nom_valide,
        t.nom_vern,
        ST_AsGeoJSON(s.the_geom_4326) as geom
    FROM gn_synthese.synthese s
    JOIN taxonomie.taxref t ON s.cd_nom = t.cd_nom
    WHERE t.cd_nom = %s
    ORDER BY s.date_min DESC
    """

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, (cd_nom,))

        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Construire une FeatureCollection GeoJSON
        features = []
        for row in rows:
            feature = {
                "type": "Feature",
                "geometry": json.loads(row['geom']) if isinstance(row['geom'], str) else row['geom'],
                "properties": {
                    "id_synthese": row['id_synthese'],
                    "date_obs": row['date_obs'],
                    "observers": row['observers'],
                    "comment_description": row['comment_description'],
                    "nom_valide": row['nom_valide'],
                    "nom_vern": row['nom_vern'],
                }
            }
            features.append(feature)

        feature_collection = {
            "type": "FeatureCollection",
            "features": features
        }

        return feature_collection

    except psycopg2.Error as e:
        logger.error(f"Erreur BDD observations: {e}")
        return {"type": "FeatureCollection", "features": []}


def get_all_grid_unrecontacted() -> List[Dict[str, Any]]:
    """Récupère toutes les mailles avec au moins un taxon PRIORITAIRE en danger (non vu depuis 10 ans)."""
    query = """
    SELECT
        la.id_area,
        la.area_name,
        ST_AsGeoJSON(la.geom_4326) as geom_4326,
        COUNT(DISTINCT s.id_synthese) as nb_obs,
        to_char(MAX(s.date_min::DATE), 'YYYY-MM-DD') as last_observation_date,
        COUNT(DISTINCT t.cd_nom) as nb_unrecontacted_species_species,
        'red' as color
    FROM ref_geo.l_areas la
    JOIN gn_synthese.cor_area_synthese cas ON la.id_area = cas.id_area
    JOIN gn_synthese.synthese s ON cas.id_synthese = s.id_synthese
    JOIN ref_geo.bib_areas_types bat ON la.id_type = bat.id_type
    JOIN taxonomie.taxref t ON s.cd_nom = t.cd_nom
    JOIN taxonomie.cor_nom_liste cnl ON t.cd_nom = cnl.cd_nom
    JOIN taxonomie.bib_listes bl ON cnl.id_liste = bl.id_liste
    WHERE bat.type_code = 'M1'
        AND bl.nom_liste = %s
    GROUP BY la.id_area, la.area_name, la.geom_4326
    HAVING MAX(s.date_min::DATE) < CURRENT_DATE - INTERVAL '10 years'
    """

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, (CODE_TAXHUB_LIST,))

        grid_cells = [dict(row) for row in cur.fetchall()]

        cur.close()
        conn.close()

        return grid_cells

    except psycopg2.Error as e:
        logger.error(f"Erreur BDD grid danger: {e}")
        return []


def get_unrecontacted_species_in_grid(id_area: int) -> List[Dict[str, Any]]:
    """Récupère les espèces PRIORITAIRES non vues depuis 10 ans dans une maille."""
    query = """
    SELECT
        t.cd_nom,
        t.nom_valide,
        t.nom_vern,
        to_char(MAX(s.date_min::DATE), 'YYYY-MM-DD') as last_observation_date,
        COUNT(DISTINCT s.id_synthese) as nb_obs
    FROM gn_synthese.synthese s
    JOIN taxonomie.taxref t ON s.cd_nom = t.cd_nom
    JOIN gn_synthese.cor_area_synthese cas ON s.id_synthese = cas.id_synthese
    JOIN taxonomie.cor_nom_liste cnl ON t.cd_nom = cnl.cd_nom
    JOIN taxonomie.bib_listes bl ON cnl.id_liste = bl.id_liste
    WHERE cas.id_area = %s
        AND bl.nom_liste = %s
    GROUP BY t.cd_nom, t.nom_valide, t.nom_vern
    HAVING MAX(s.date_min::DATE) < CURRENT_DATE - INTERVAL '10 years'
    ORDER BY MAX(s.date_min::DATE) ASC
    """

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, (id_area, CODE_TAXHUB_LIST))

        species = [dict(row) for row in cur.fetchall()]

        cur.close()
        conn.close()

        return species

    except psycopg2.Error as e:
        logger.error(f"Erreur BDD espèces danger: {e}")
        return []


def get_grid_geometry(id_area: int) -> str:
    """Récupère la géométrie GeoJSON d'une maille par son id_area en tant que Feature.
    
    Args:
        id_area: ID de la maille
        
    Returns:
        Feature GeoJSON (string) ou None si pas trouvée
    """
    query = """
    SELECT ST_AsGeoJSON(geom_4326) as geom
    FROM ref_geo.l_areas
    WHERE id_area = %s
    """
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, (id_area,))
        
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if row and row['geom']:
            # Parser la géométrie et la wrapper dans une Feature
            geom = json.loads(row['geom'])
            feature = {
                "type": "Feature",
                "geometry": geom,
                "properties": {}
            }
            return feature
        else:
            return None
            
    except psycopg2.Error as e:
        logger.error(f"Erreur BDD géométrie maille {id_area}: {e}")
        return None
