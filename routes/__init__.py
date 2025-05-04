from flask import Blueprint

api = Blueprint('api', __name__)

from routes.auth_routes import *
from routes.shop_list_routes import *
from routes.product_routes import *
