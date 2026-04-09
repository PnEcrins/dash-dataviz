import dash
from src.modules.aigle.layout import get_aigle_layout
from src.utils import get_page_path

dash.register_page(__name__, path=get_page_path('/aigle'), name="Aigle")

layout = get_aigle_layout()
