"""Application Dash principale - Multi-page avec Dash Pages."""
import logging
from dash import html
import dash
import dash_bootstrap_components as dbc
import config

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialiser l'app Dash avec Dash Pages
app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    requests_pathname_prefix=config.URL_PREFIX
)

app.layout = html.Div(
    dash.page_container,
    style={"height": "100vh", "width": "100vw", "margin": "0", "padding": "0", "overflow": "hidden"}
)

if __name__ == "__main__":
    import config
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
