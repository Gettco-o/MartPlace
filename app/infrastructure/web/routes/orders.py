from quart import Blueprint, jsonify

orders = Blueprint('orders', __name__, url_prefix='/orders')

