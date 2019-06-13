from flask import Blueprint

opp_bp = Blueprint('opp', __name__)

from main.opp import routes
