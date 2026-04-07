"""Modèles de données pour module Aigle."""
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List
from datetime import datetime
import json


@dataclass
class Site:
    """Représente une aire d'aigle."""

    id_base_site: int
    base_site_name: str
    base_site_code: str
    discover_year: Optional[str] = None
    base_site_description: Optional[str] = None
    altitude_min: Optional[int] = None
    altitude_max: Optional[int] = None
    orientation: Optional[str] = None
    geom: Optional[str] = None  # GeoJSON string
    aire_valid: Optional[bool] = None

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Site":
        """Crée un Site depuis les données API."""
        return cls(
            id_base_site=data.get("id_base_site"),
            base_site_name=data.get("base_site_name", ""),
            base_site_code=data.get("base_site_code", ""),
            discover_year=data.get("discover_year"),
            base_site_description=data.get("base_site_description"),
            altitude_min=data.get("altitude_min"),
            altitude_max=data.get("altitude_max"),
            orientation=data.get("orientation"),
            geom=data.get("st_asgeojson"),
            aire_valid=data.get("aire_valid"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return asdict(self)

    def get_geom_feature(self) -> Optional[Dict[str, Any]]:
        """Retourne la géométrie au format GeoJSON Feature."""
        if not self.geom:
            return None

        try:
            geom = json.loads(self.geom) if isinstance(self.geom, str) else self.geom

            return {
                "type": "Feature",
                "properties": {
                    "id": self.id_base_site,
                    "name": self.base_site_name,
                    "code": self.base_site_code,
                    "year": self.discover_year,
                    "aire_valid": self.aire_valid,
                },
                "geometry": geom,
            }
        except json.JSONDecodeError:
            return None


@dataclass
class Visit:
    """Représente une visite d'aire."""

    id_base_visit: int
    id_base_site: int
    visit_date: str
    observers_txt: Optional[str] = None
    comments: Optional[str] = None
    uuid_base_visit: Optional[str] = None

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Visit":
        """Crée une Visit depuis les données API."""
        return cls(
            id_base_visit=data.get("id_base_visit"),
            id_base_site=data.get("id_base_site"),
            visit_date=data.get("visit_date", ""),
            observers_txt=data.get("observers_txt"),
            comments=data.get("comments"),
            uuid_base_visit=data.get("uuid_base_visit"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return asdict(self)

    def get_year(self) -> int:
        """Extrait l'année de visit_date."""
        try:
            return int(self.visit_date[:4])
        except (ValueError, IndexError):
            return 0

    def get_formatted_date(self) -> str:
        """Retourne la date formatée (DD/MM/YYYY)."""
        try:
            date = datetime.strptime(self.visit_date, "%Y-%m-%d")
            return date.strftime("%d/%m/%Y")
        except ValueError:
            return self.visit_date
