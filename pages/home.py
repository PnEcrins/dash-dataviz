"""Page d'accueil avec liste des modules."""
import dash
from dash import html, dcc
from src.utils import get_page_path

dash.register_page(__name__, path=get_page_path('/'), name="Accueil")

layout = html.Div([
    html.Div([
        html.H1("📊 Application de visualisation de données"),
    ], style={"padding": "2rem", "textAlign": "center"}),
    
    html.Div([
        html.Div([
            html.H3("🦅 Module Aigle"),
            html.P("Suivi géospatial et temporel des aigles"),
            dcc.Link("Accéder au module →", href=get_page_path('/aigle'), style={
                "display": "inline-block",
                "padding": "0.5rem 1rem",
                "backgroundColor": "#007bff",
                "color": "white",
                "textDecoration": "none",
                "borderRadius": "4px",
            }),
        ], style={
            "padding": "1.5rem",
            "border": "1px solid #ddd",
            "borderRadius": "8px",
            "marginRight": "1rem",
        }),
        html.Div([
            html.H3("🌿 Module Flore"),
            html.P("Suivi de la flore"),
            dcc.Link("Accéder au module →", href=get_page_path('/flore'), style={
                "display": "inline-block",
                "padding": "0.5rem 1rem",
                "backgroundColor": "#28a745",
                "color": "white",
                "textDecoration": "none",
                "borderRadius": "4px",
            }),
        ], style={
            "padding": "1.5rem",
            "border": "1px solid #ddd",
            "borderRadius": "8px",
            "marginRight": "1rem",
        }),
    ], style={
        "display": "flex",
        "justifyContent": "center",
        "gap": "2rem",
        "maxWidth": "1200px",
        "margin": "2rem auto",
        "flexWrap": "wrap",
    }),
], style={
    "height": "100vh",
    "display": "flex",
    "flexDirection": "column",
    "justifyContent": "center",
    "backgroundColor": "#f8f9fa",
})
