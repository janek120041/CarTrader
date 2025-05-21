from flask import Blueprint

bp = Blueprint('messages', __name__)

from app.messages import routes  # Import routes at the bottom to avoid circular imports 