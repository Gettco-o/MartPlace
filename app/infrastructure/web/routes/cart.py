from quart import Blueprint
from quart_schema import tag_blueprint

cart = Blueprint('cart', __name__, url_prefix='/cart')
tag_blueprint(cart, ["cart"])
