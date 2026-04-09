"""Composant sélecteur taxon - Module Flore."""
from typing import List, Dict, Any
from dash import html, dcc


def create_taxon_selector(taxa: List[Dict[str, Any]]) -> html.Div:
    """Crée le sélecteur de taxon prioritaire avec barre de recherche native.

    Args:
        taxa: Liste des taxons prioritaires

    Returns:
        Composant div avec dropdown searchable
    """
    options = [
        {"label": f"{t['nom_valide']} ({t.get('nom_vern') or t.get('lb_nom')})", "value": t['cd_nom']}
        for t in taxa
    ]

    return html.Div(
        [
            html.H5("🌿 Flore Prioritaire", className="mb-3"),
            html.Label("Sélectionnez un taxon:", className="mb-2"),
            dcc.Dropdown(
                id="flore-taxon-selector",
                options=options,
                value=None,
                searchable=True,
                clearable=True,
                placeholder="Rechercher un taxon...",
                maxHeight=400,
                style={"width": "100%"},
            ),
            html.Hr(),

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
