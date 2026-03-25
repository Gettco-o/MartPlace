from quart import Blueprint

products = Blueprint('products', __name__, url_prefix='/products')
