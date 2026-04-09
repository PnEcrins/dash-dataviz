"""Composant liste observations maille - Module Flore."""
from typing import List, Optional, Dict, Any
from dash import html
import dash_bootstrap_components as dbc


def create_observations_panel(
    grid_name: Optional[str] = None,
    observations: Optional[List[Dict[str, Any]]] = None,
) -> html.Div:
    """Crée le panneau observations d'une maille.

    Args:
        grid_name: Nom de la maille sélectionnée
        observations: Liste des observations (dict avec clés: date_obs, nom_valide, nom_vern, observers, comment_description)

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
                                html.Strong(obs.get('date_obs')),
                                html.Br(),
                                html.Small(
                                    f"{obs.get('nom_valide')} ({obs.get('nom_vern') or 'N/A'})",
                                    className="text-muted d-block",
                                ),
                                html.Small(
                                    f"Obs: {obs.get('observers') or 'N/A'}",
                                    className="text-muted d-block",
                                ),
                            ]
                        ),
                        html.Hr() if obs.get('comment_description') else None,
                        html.Small(obs.get('comment_description'), className="d-block text-muted")
                        if obs.get('comment_description')
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