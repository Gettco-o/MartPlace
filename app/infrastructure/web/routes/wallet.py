from quart import Blueprint
from quart_schema import tag_blueprint

wallet = Blueprint('wallet', __name__, url_prefix='/wallet')
tag_blueprint(wallet, ["wallet"])
