from flask import Flask
from main.config import Config
app = Flask(__name__)
app.config.from_object(Config)

from main import routes
