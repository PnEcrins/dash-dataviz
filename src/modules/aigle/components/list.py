"""Composant liste des aires - Module Aigle."""
from typing import List, Optional
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from src.modules.aigle.data.models import Site


def create_sites_list(sites: List[Site], selected_site_id: Optional[int] = None) -> html.Div:
    """Crée la liste complète des aires.

    Args:
        sites: Liste des aires à afficher
        selected_site_id: ID de l'aire sélectionnée

    Returns:
        Composant liste
    """

    list_items = []
    for site in sites:
        is_selected = site.id_base_site == selected_site_id

        item = dbc.ListGroupItem(
            [
                html.Div(
                    [
                        html.H6(site.base_site_name, className="mb-0"),
                        html.Small(
                            f"Code: {site.base_site_code}",
                            className="text-muted",
                        ),
                        html.Br(),
                        html.Small(
                            f"Découverte: {site.discover_year if site.discover_year else 'N/A'}",
                            className="text-muted",
                        ),
                    ]
                )
            ],
            id={"type": "site-list-item", "index": site.id_base_site},
            color="light" if is_selected else None,
            active=is_selected,
            style={"cursor": "pointer", "padding": "12px"},
            className="border-bottom",
        )
        list_items.append(item)

    return html.Div(
        [
            html.H5("Aires d'aigle", className="mb-3"),
            dbc.ListGroup(
                list_items,
                id="sites-list",
            ),
        ],
        style={
            "height": "100%",
            "overflowY": "auto",
            "paddingRight": "5px",
        },
    )


def create_empty_list() -> html.Div:
    """Crée une liste vide (pour état de chargement)."""
    return html.Div(
        [
            html.H5("Aires d'aigle", className="mb-3"),
            html.P("Chargement des données...", className="text-muted"),
        ],
    )
