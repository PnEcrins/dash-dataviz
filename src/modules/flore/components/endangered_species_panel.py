"""Composant liste espèces en danger - Module Flore."""
from typing import List, Dict, Any, Optional
from dash import html
import dash_bootstrap_components as dbc


def create_endangered_species_panel(
    grid_name: Optional[str] = None,
    species: Optional[List[Dict[str, Any]]] = None,
) -> html.Div:
    """Crée le panneau espèces en danger d'une maille.

    Args:
        grid_name: Nom de la maille sélectionnée
        species: Liste des espèces en danger

    Returns:
        Composant panneau espèces en danger
    """

    if not grid_name or not species:
        return html.Div(
            [
                html.H5("Espèces en Danger", className="mb-3"),
                html.P(
                    "Cliquez sur une maille rouge pour voir les espèces non observées depuis 10 ans",
                    className="text-muted",
                ),
            ],
        )

    species_buttons = []
    for sp in species:
        btn = dbc.Button(
            [
                html.Div(
                    [
                        html.Strong(sp['nom_valide'], style={"color": "#dc3545"}),
                        html.Br(),
                        html.Small(
                            f"{sp['nom_vern'] or 'N/A'}",
                            className="text-muted d-block",
                        ),
                        html.Br(),
                        html.Small(
                            f"⏰ Dernière: {sp['last_observation_date'].isoformat() if sp['last_observation_date'] else 'N/A'}",
                            className="text-danger d-block",
                            style={"fontWeight": "500"},
                        ),
                        html.Small(
                            f"📊 {sp['nb_obs']} obs historiques",
                            className="text-muted d-block",
                        ),
                    ]
                ),
            ],
            id={"type": "endangered-species-btn", "cd_nom": sp['cd_nom']},
            className="mb-2 w-100",
            # n_clicks=0,
            style={
                "borderLeft": "4px solid #dc3545",
                "textAlign": "left",
                "backgroundColor": "white",
                "color": "black",
                "border": "1px solid #dee2e6",
                "padding": "10px",
            },
        )
        species_buttons.append(btn)

    return html.Div(
        [
            html.H5("Espèces en Danger", className="mb-2"),
            html.P(f"{grid_name} - {len(species)} espèces manquantes",
                   className="small text-danger mb-3",
                   style={"fontWeight": "500"}),
            html.Div(
                species_buttons if species_buttons else html.P(
                    "Aucune espèce en danger",
                    className="text-muted",
                ),
                id="flore-endangered-list",
                style={
                    "maxHeight": "100%",
                    "overflowY": "auto",
                    "paddingRight": "5px",
                },
            ),
        ],
    )


def create_empty_endangered_species_panel() -> html.Div:
    """Crée un panneau vide espèces en danger."""
    return html.Div(
        [
            html.H5("Espèces en Danger", className="mb-3"),
            html.P(
                "Cliquez sur une maille rouge pour voir les espèces non observées depuis 10 ans",
                className="text-muted",
            ),
        ],
    )
