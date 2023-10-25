from flask import Blueprint

bp = Blueprint('clubs', __name__)

from app.clubs import routes