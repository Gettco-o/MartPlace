from quart import Blueprint, jsonify
from quart_schema import tag_blueprint

orders = Blueprint('orders', __name__, url_prefix='/orders')
tag_blueprint(orders, ["orders"])
