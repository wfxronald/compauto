from flask import Blueprint

req_bp = Blueprint('req', __name__)

from main.req import routes
