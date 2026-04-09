"""Composant liste observations maille - Module Flore."""
from typing import List, Optional
from dash import html
import dash_bootstrap_components as dbc
from src.modules.flore.data.models import Observation


def create_observations_panel(
    grid_name: Optional[str] = None,
    observations: Optional[List[Observation]] = None,
) -> html.Div:
    """Crée le panneau observations d'une maille.

    Args:
        grid_name: Nom de la maille sélectionnée
        observations: Liste des observations

    Returns:
        Composant panneau observations
    """

    if not grid_name or not observations:
        return html.Div([])

    obs_cards = []
    for obs in observations:
        card = dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                html.Strong(obs.date_obs.isoformat()),
                                html.Br(),
                                html.Small(
                                    f"{obs.nom_valide} ({obs.nom_vern or 'N/A'})",
                                    className="text-muted d-block",
                                ),
                                html.Small(
                                    f"Obs: {obs.observers or 'N/A'}",
                                    className="text-muted d-block",
                                ),
                            ]
                        ),
                        html.Hr() if obs.comment_description else None,
                        html.Small(obs.comment_description, className="d-block text-muted")
                        if obs.comment_description
                        else None,
                    ],
                    style={"padding": "10px"},
                )
            ],
            className="mb-2",
        )
        obs_cards.append(card)

    return html.Div(
        [
            html.H5("Observations", className="mb-2"),
            html.P(f"{grid_name} - {len(observations)} obs", className="small text-muted mb-3"),
            html.Div(
                obs_cards if obs_cards else html.P(
                    "Aucune observation",
                    className="text-muted",
                ),
                id="flore-observations-list",
                style={
                    "maxHeight": "100%",
                    "overflowY": "auto",
                    "paddingRight": "5px",
                },
            ),
        ],
    )