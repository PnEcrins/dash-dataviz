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
