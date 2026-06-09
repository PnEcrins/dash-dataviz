from dash import html

import dash_bootstrap_components as dbc


def base_modal_component():
    return dbc.Modal(
        [
            dbc.ModalBody(
                [
                    # Carte des observation pour un cd_nom
                    html.Div(
                        id="modal-map-container",
                        style={
                            "marginBottom": "10px",
                        },
                    ),
                    # Légende pour la carte (circle markers)
                    html.Div(
                        id="modal-legend",
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "6px",
                            "marginBottom": "10px",
                        },
                        children=[
                            html.Div(
                                [
                                    html.Span(
                                        "",
                                        style={
                                            "width": "12px",
                                            "height": "12px",
                                            "borderRadius": "50%",
                                            "backgroundColor": "blue",
                                            "display": "inline-block",
                                            "marginRight": "8px",
                                        },
                                    ),
                                    html.Small("< 10 ans"),
                                ],
                                style={"display": "flex", "alignItems": "center"},
                            ),
                            html.Div(
                                [
                                    html.Span(
                                        "",
                                        style={
                                            "width": "12px",
                                            "height": "12px",
                                            "borderRadius": "50%",
                                            "backgroundColor": "red",
                                            "display": "inline-block",
                                            "marginRight": "8px",
                                        },
                                    ),
                                    html.Small("> 10 ans"),
                                ],
                                style={"display": "flex", "alignItems": "center"},
                            ),
                            html.Div(
                                [
                                    html.Span(
                                        "",
                                        style={
                                            "width": "12px",
                                            "height": "12px",
                                            "borderRadius": "50%",
                                            "backgroundColor": "transparent",
                                            "display": "inline-block",
                                            "marginRight": "8px",
                                            "border": "5px solid black",  # contour noir épais = centroid de polygone/ligne
                                        },
                                    ),
                                    html.Small(
                                        "Obseervation non précise (centroid de polygone / ligne)"
                                    ),
                                ],
                                style={"display": "flex", "alignItems": "center"},
                            ),
                        ],
                    ),
                    dbc.Alert(
                        html.Small(
                            "⚠️ Les observations sont représentées par leur centroid. Si l'observation était un grand polygone, il se peut qu'elle ne soit pas exactement dans la maille sélectionnée",
                            style={"font-size": "0.7rem"},
                        ),
                        color="info",
                    ),
                ]
            )
        ],
        id="modal",
        is_open=False,
    )
