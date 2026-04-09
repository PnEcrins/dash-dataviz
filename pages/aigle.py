import dash
from src.modules.aigle.layout import get_aigle_layout

dash.register_page(__name__, path="/aigle", name="Aigle")

layout = get_aigle_layout()
