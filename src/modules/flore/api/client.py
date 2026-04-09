"""API client PostgreSQL pour module Flore."""
import json
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date
from typing import List, Dict, Any

from config import DB_CONFIG
from src.modules.flore.data.models import PriorityTaxon, GridCell, Observation

logger = logging.getLogger(__name__)


def get_priority_flora_taxa() -> List[PriorityTaxon]:
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
    JOIN taxonomie.bib_noms bn ON cnl.id_nom = bn.id_nom
    JOIN taxonomie.taxref t ON bn.cd_nom = t.cd_nom
    WHERE bl.nom_liste = 'Priority Flora'
    ORDER BY t.nom_valide
    """

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query)

        taxa = []
        rows = cur.fetchall()
        for row in rows:
            taxa.append(PriorityTaxon(
                cd_nom=row['cd_nom'],
                cd_ref=row['cd_ref'],
                nom_valide=row['nom_valide'],
                lb_nom=row['lb_nom'],
                nom_vern=row['nom_vern'],
            ))

        cur.close()
        conn.close()

        logger.info(f"✓ Chargé {len(taxa)} taxons de flore prioritaire")
        return taxa

    except psycopg2.Error as e:
        logger.error(f"Erreur BDD taxa: {e}")
        return []


def get_observations_by_grid(cd_nom: int) -> List[GridCell]:
    """Récupère observations par maille 1km pour un taxon."""
    query = """
    SELECT
        la.id_area,
        la.area_name,
        ST_AsGeoJSON(la.geom_4326) as geom_4326,
        t.cd_nom,
        COUNT(DISTINCT s.id_synthese) as nb_obs,
        MAX(s.date_min::DATE) as last_observation_date,
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

        grid_cells = []
        for row in cur.fetchall():
            # Parser la date
            last_date = None
            if row['last_observation_date']:
                if isinstance(row['last_observation_date'], date):
                    last_date = row['last_observation_date']
                else:
                    last_date = datetime.strptime(row['last_observation_date'], "%Y-%m-%d").date()

            grid_cells.append(GridCell(
                id_area=row['id_area'],
                area_name=row['area_name'],
                geom_4326=row['geom_4326'],
                nb_observations=row['nb_obs'],
                last_observation_date=last_date,
                color=row['color'],
            ))

        cur.close()
        conn.close()

        logger.info(f"✓ Chargé {len(grid_cells)} mailles pour taxon {cd_nom}")
        return grid_cells

    except psycopg2.Error as e:
        logger.error(f"Erreur BDD grid: {e}")
        return []


def get_observations_of_cd_nom(cd_nom: int) -> List[Observation]:
    """Récupère détail observations d'une maille."""
    query = """
    SELECT
        s.id_synthese,
        s.date_min::DATE as date_obs,
        s.observers,
        s.comment_description,
        t.nom_valide,
        t.nom_vern,
        ST_X(ST_Centroid(s.the_geom_4326)) as lon,
        ST_Y(ST_Centroid(s.the_geom_4326)) as lat
    FROM gn_synthese.synthese s
    JOIN taxonomie.taxref t ON s.cd_nom = t.cd_nom
    WHERE t.cd_nom = %s
    ORDER BY s.date_min DESC
    """

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, (cd_nom,))

        observations = []
        for row in cur.fetchall():

            observations.append(Observation(
                id_synthese=row['id_synthese'],
                date_obs=row["date_obs"],
                observers=row['observers'],
                comment_description=row['comment_description'],
                nom_valide=row['nom_valide'],
                nom_vern=row['nom_vern'],
                lon=row['lon'],
                lat=row['lat'],
            ))

        cur.close()
        conn.close()

        logger.info(f"✓ Chargé {len(observations)} observations pour cd_nom {cd_nom}")
        return observations

    except psycopg2.Error as e:
        logger.error(f"Erreur BDD observations: {e}")
        return []


def get_all_grid_cells_with_danger() -> List[GridCell]:
    """Récupère toutes les mailles avec au moins un taxon PRIORITAIRE en danger (non vu depuis 10 ans)."""
    query = """
    SELECT
        la.id_area,
        la.area_name,
        ST_AsGeoJSON(la.geom_4326) as geom_4326,
        COUNT(DISTINCT s.id_synthese) as nb_obs,
        MAX(s.date_min::DATE) as last_observation_date,
        COUNT(DISTINCT t.cd_nom) as nb_unrecontacted_species_species,
        'red' as color
    FROM ref_geo.l_areas la
    JOIN gn_synthese.cor_area_synthese cas ON la.id_area = cas.id_area
    JOIN gn_synthese.synthese s ON cas.id_synthese = s.id_synthese
    JOIN ref_geo.bib_areas_types bat ON la.id_type = bat.id_type
    JOIN taxonomie.taxref t ON s.cd_nom = t.cd_nom
    JOIN taxonomie.bib_noms bn ON t.cd_nom = bn.cd_nom
    JOIN taxonomie.cor_nom_liste cnl ON bn.id_nom = cnl.id_nom
    JOIN taxonomie.bib_listes bl ON cnl.id_liste = bl.id_liste
    WHERE bat.type_code = 'M1'
        AND bl.nom_liste = 'Priority Flora'
    GROUP BY la.id_area, la.area_name, la.geom_4326
    HAVING MAX(s.date_min::DATE) < CURRENT_DATE - INTERVAL '10 years'
    """

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query)

        grid_cells = []
        for row in cur.fetchall():
            last_date = None
            if row['last_observation_date']:
                if isinstance(row['last_observation_date'], date):
                    last_date = row['last_observation_date']
                else:
                    last_date = datetime.strptime(row['last_observation_date'], "%Y-%m-%d").date()

            grid_cells.append(GridCell(
                id_area=row['id_area'],
                area_name=row['area_name'],
                geom_4326=row['geom_4326'],
                nb_observations=row['nb_obs'] or 0,
                last_observation_date=last_date,
                color=row['color'],
                nb_unrecontacted_species_species=row['nb_unrecontacted_species_species'] or 0,
            ))

        cur.close()
        conn.close()

        logger.info(f"✓ Chargé {len(grid_cells)} mailles avec danger")
        return grid_cells

    except psycopg2.Error as e:
        logger.error(f"Erreur BDD grid danger: {e}")
        return []


def get_endangered_species_in_grid(id_area: int) -> List[Dict[str, Any]]:
    """Récupère les espèces PRIORITAIRES non vues depuis 10 ans dans une maille."""
    query = """
    SELECT
        t.cd_nom,
        t.nom_valide,
        t.nom_vern,
        MAX(s.date_min::DATE) as last_observation_date,
        COUNT(DISTINCT s.id_synthese) as nb_obs
    FROM gn_synthese.synthese s
    JOIN taxonomie.taxref t ON s.cd_nom = t.cd_nom
    JOIN gn_synthese.cor_area_synthese cas ON s.id_synthese = cas.id_synthese
    JOIN taxonomie.bib_noms bn ON t.cd_nom = bn.cd_nom
    JOIN taxonomie.cor_nom_liste cnl ON bn.id_nom = cnl.id_nom
    JOIN taxonomie.bib_listes bl ON cnl.id_liste = bl.id_liste
    WHERE cas.id_area = %s
        AND bl.nom_liste = 'Priority Flora'
    GROUP BY t.cd_nom, t.nom_valide, t.nom_vern
    HAVING MAX(s.date_min::DATE) < CURRENT_DATE - INTERVAL '10 years'
    ORDER BY MAX(s.date_min::DATE) ASC
    """

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, (id_area,))

        species = []
        for row in cur.fetchall():
            last_date = None
            if row['last_observation_date']:
                if isinstance(row['last_observation_date'], date):
                    last_date = row['last_observation_date']
                else:
                    last_date = datetime.strptime(row['last_observation_date'], "%Y-%m-%d").date()

            species.append({
                'cd_nom': row['cd_nom'],
                'nom_valide': row['nom_valide'],
                'nom_vern': row['nom_vern'],
                'last_observation_date': last_date,
                'nb_obs': row['nb_obs'],
            })

        cur.close()
        conn.close()

        logger.info(f"✓ Chargé {len(species)} espèces prioritaires en danger pour maille {id_area}")
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
            logger.info(f"✓ Géométrie chargée pour maille {id_area}")
            return feature
        else:
            logger.warning(f"❌ Aucune géométrie trouvée pour maille {id_area}")
            return None
            
    except psycopg2.Error as e:
        logger.error(f"Erreur BDD géométrie maille {id_area}: {e}")
        return None
