import dash
from src.modules.flore.layout import get_flore_layout
from src.utils import get_page_path

dash.register_page(__name__, path=get_page_path('/flore'), name="Flore")

layout = get_flore_layout()
