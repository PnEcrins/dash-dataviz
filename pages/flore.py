import dash
from src.modules.flore.layout import get_flore_layout

dash.register_page(__name__, path="/flore", name="Flore")

layout = get_flore_layout()
