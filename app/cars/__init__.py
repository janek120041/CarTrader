from flask import Blueprint

bp = Blueprint('cars', __name__, url_prefix='/cars')

from app.cars import routes 