"""Composant panneau des visites - Module Aigle."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from dash import html
import dash_bootstrap_components as dbc


def format_visit_date(date_str: str) -> str:
    """Formate une date YYYY-MM-DD en DD/MM/YYYY."""
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        return date.strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return date_str or 'N/A'


def create_visits_panel(
    site_name: Optional[str] = None,
    visits: Optional[List[Dict[str, Any]]] = None,
) -> html.Div:
    """Crée le panneau affichant les visites d'une aire.

    Args:
        site_name: Nom de l'aire sélectionnée
        visits: Liste des visites (éléments dict avec clés: visit_date, observers_txt, comments)

    Returns:
        Composant panneau visites
    """

    if not site_name or not visits:
        return html.Div(
            [
                html.H5("Visites", className="mb-3"),
                html.P(
                    "Sélectionner une aire pour voir les visites",
                    className="text-muted",
                ),
            ],
        )

    visit_cards = []
    for visit in visits:
        card = dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                html.Strong(format_visit_date(visit.get('visit_date', ''))),
                                html.Br(),
                                html.Small(
                                    f"Observateurs: {visit.get('observers_txt') or 'N/A'}",
                                    className="text-muted d-block",
                                ),
                            ]
                        ),
                        html.Hr() if visit.get('comments') else None,
                        html.Small(visit.get('comments'), className="d-block text-muted")
                        if visit.get('comments')
                        else None,
                    ],
                    style={"padding": "10px"},
                )
            ],
            className="mb-2",
        )
        visit_cards.append(card)

    return html.Div(
        [
            html.H5("Visites", className="mb-2"),
            html.P(f"pour {site_name}", className="small text-muted mb-3"),
            html.Div(
                visit_cards if visit_cards else html.P(
                    "Aucune visite pour cette année",
                    className="text-muted",
                ),
                id="visits-list",
                style={
                    "maxHeight": "100%",
                    "overflowY": "auto",
                    "paddingRight": "5px",
                },
            ),
        ],
    )


def create_empty_visits_panel() -> html.Div:
    """Crée un panneau vide (état par défaut)."""
    return html.Div(
        [
            html.H5("Visites", className="mb-3"),
            html.P(
                "Sélectionner une aire pour voir les visites",
                className="text-muted",
            ),
        ],
    )
