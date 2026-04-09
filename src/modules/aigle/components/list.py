"""Composant liste des aires - Module Aigle."""
from typing import List, Optional, Dict, Any
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc


def create_sites_list(sites: List[Dict[str, Any]], selected_site_id: Optional[int] = None) -> html.Div:
    """Crée la liste complète des aires.

    Args:
        sites: Liste des aires (éléments dict avec clés: id_base_site, base_site_name, base_site_code, discover_year)
        selected_site_id: ID de l'aire sélectionnée

    Returns:
        Composant liste
    """

    list_items = []
    for site in sites:
        site_id = site.get('id_base_site')
        is_selected = site_id == selected_site_id

        item = dbc.ListGroupItem(
            [
                html.Div(
                    [
                        html.H6(site.get('base_site_name'), className="mb-0"),
                        html.Small(
                            f"Code: {site.get('base_site_code')}",
                            className="text-muted",
                        ),
                        html.Br(),
                        html.Small(
                            f"Découverte: {site.get('discover_year') or 'N/A'}",
                            className="text-muted",
                        ),
                    ]
                )
            ],
            id={"type": "site-list-item", "index": site_id},
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
