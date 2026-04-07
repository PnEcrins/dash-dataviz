"""Composant panneau des visites d'une aire."""
from typing import List, Optional
from dash import html
import dash_bootstrap_components as dbc
from src.data.models import Visit


def create_visits_panel(
    site_name: Optional[str] = None,
    visits: Optional[List[Visit]] = None,
) -> html.Div:
    """Crée le panneau affichant les visites d'une aire.

    Args:
        site_name: Nom de l'aire sélectionnée
        visits: Liste des visites à afficher

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

    # Construire les cartes de visite
    visit_cards = []
    for visit in visits:
        card = dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                html.Strong(visit.get_formatted_date()),
                                html.Br(),
                                html.Small(
                                    f"Observateurs: {visit.observers_txt or 'N/A'}",
                                    className="text-muted d-block",
                                ),
                            ]
                        ),
                        html.Hr() if visit.comments else None,
                        html.Small(visit.comments, className="d-block text-muted")
                        if visit.comments
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
