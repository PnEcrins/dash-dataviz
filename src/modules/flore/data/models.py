"""Modèles de données pour module Flore."""
from dataclasses import dataclass
from typing import Optional
from datetime import date
import json


@dataclass
class PriorityTaxon:
    """Taxon dans la liste de flore prioritaire."""

    cd_nom: int
    cd_ref: int
    nom_valide: str
    lb_nom: str
    nom_vern: Optional[str] = None

    def to_dict(self) -> dict:
        """Convertit en dictionnaire."""
        return {
            "cd_nom": self.cd_nom,
            "cd_ref": self.cd_ref,
            "nom_valide": self.nom_valide,
            "lb_nom": self.lb_nom,
            "nom_vern": self.nom_vern,
        }


@dataclass
class GridCell:
    """Maille 1km avec observations."""

    id_area: int
    area_name: str
    geom_4326: Optional[str]  # GeoJSON
    nb_observations: int
    last_observation_date: Optional[date]
    color: str  # 'green' ou 'red'
    nb_endangered_species: int = 0  # Nombre d'espèces en danger

    def to_dict(self) -> dict:
        """Convertit en dictionnaire."""
        return {
            "id_area": self.id_area,
            "area_name": self.area_name,
            "geom_4326": self.geom_4326,
            "nb_observations": self.nb_observations,
            "last_observation_date": self.last_observation_date.isoformat() if self.last_observation_date else None,
            "color": self.color,
            "nb_endangered_species": self.nb_endangered_species,
        }


@dataclass
class Observation:
    """Observation dans une maille."""

    id_synthese: int
    date_obs: date
    observers: Optional[str]
    comment_description: Optional[str]
    nom_valide: str
    nom_vern: Optional[str]
    lon: Optional[float] = None
    lat: Optional[float] = None

    def to_dict(self) -> dict:
        """Convertit en dictionnaire."""
        return {
            "id_synthese": self.id_synthese,
            "date_obs": self.date_obs.isoformat(),
            "observers": self.observers,
            "comment_description": self.comment_description,
            "nom_valide": self.nom_valide,
            "nom_vern": self.nom_vern,
            "lon": self.lon,
            "lat": self.lat,
        }
