from flask import Blueprint

main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')

from app.routes.main import *
from app.routes.api import * 