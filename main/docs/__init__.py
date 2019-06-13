from flask import Blueprint

docs_bp = Blueprint('docs', __name__)

from main.docs import routes
