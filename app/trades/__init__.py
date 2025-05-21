from flask import Blueprint

bp = Blueprint('trades', __name__)

from app.trades import routes 