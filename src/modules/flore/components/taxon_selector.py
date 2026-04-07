"""Composant sélecteur taxon - Module Flore."""
from typing import List
from dash import html
import dash_bootstrap_components as dbc
from src.modules.flore.data.models import PriorityTaxon


def create_taxon_selector(taxa: List[PriorityTaxon]) -> html.Div:
    """Crée le sélecteur de taxon prioritaire.

    Args:
        taxa: Liste des taxons prioritaires

    Returns:
        Composant div avec dropdown
    """
    options = [
        {"label": f"{t.nom_valide} ({t.nom_vern or t.lb_nom})", "value": t.cd_nom}
        for t in taxa
    ]

    return html.Div(
        [
            html.H5("🌿 Flore Prioritaire", className="mb-3"),
            html.Label("Sélectionnez un taxon:", className="mb-2"),
            dbc.Select(
                id="flore-taxon-selector",
                options=options,
                value=None,
            ),
            html.Hr(),
            html.Div(
                id="flore-selected-taxon-info",
                className="mt-3",
                style={"fontSize": "0.9rem", "color": "#666"},
            ),
        ],
        style={
            "height": "100%",
            "padding": "1rem",
            "overflowY": "auto",
        },
    )


def create_empty_selector() -> html.Div:
    """Crée un sélecteur vide."""
    return html.Div(
        [
            html.H5("🌿 Flore Prioritaire", className="mb-3"),
            html.P("Chargement des taxons...", className="text-muted"),
        ],
        style={"padding": "1rem"},
    )
