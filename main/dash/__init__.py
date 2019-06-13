from flask import Blueprint

dash_bp = Blueprint('dash', __name__)

from main.dash import routes
