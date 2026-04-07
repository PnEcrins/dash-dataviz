"""Application Dash principale - Router entre modules."""
import logging
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import dash

from src.modules.aigle.layout import get_aigle_layout
from src.modules.flore.layout import get_flore_layout

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialiser l'app Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
# Layout principal avec routing
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),

        # Navigation bar
        html.Div(
            [
                dcc.Link(
                    html.Button("🦅 Aigle", id="btn-aigle", n_clicks=0,
                               style={"marginRight": "10px", "padding": "10px 20px", "cursor": "pointer"}),
                    href="/aigle",
                    style={"textDecoration": "none"}
                ),
                dcc.Link(
                    html.Button("🌿 Flore", id="btn-flore", n_clicks=0,
                               style={"padding": "10px 20px", "cursor": "pointer"}),
                    href="/flore",
                    style={"textDecoration": "none"}
                ),
            ],
            style={
                "padding": "10px",
                "backgroundColor": "#f8f9fa",
                "borderBottom": "1px solid #dee2e6",
                "flexShrink": "0",
            }
        ),

        # Container pour les modules
        html.Div(
            id="modules-container",
            style={
                "height": "calc(100vh - 60px)",
                "width": "100%",
                "overflow": "hidden",
                "margin": "0",
                "padding": "0",
                "flexGrow": "1",
            }
        ),
    ],
    style={
        "height": "100vh",
        "width": "100%",
        "margin": "0",
        "padding": "0",
        "display": "flex",
        "flexDirection": "column",
    },
)


@callback(
    Output("modules-container", "children"),
    Input("url", "pathname")
)
def display_module(pathname):
    """Affiche le module selon le pathname."""
    if pathname == "/flore":
        return get_flore_layout()
    else:
        # Défaut: Aigle
        return get_aigle_layout()


if __name__ == "__main__":
    import config
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
