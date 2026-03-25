from quart import Blueprint

users = Blueprint('users', __name__, url_prefix='/users')
