from quart import Blueprint

tenants = Blueprint('tenants', __name__, url_prefix='/tenants')
