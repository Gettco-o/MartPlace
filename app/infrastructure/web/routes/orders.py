from quart import Blueprint

orders = Blueprint('orders', __name__, url_prefix='/orders')
