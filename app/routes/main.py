from flask import Blueprint, render_template
from app.models import Car

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    cars = Car.query.filter_by(is_sold=False).order_by(Car.date_posted.desc()).limit(6).all()
    return render_template('index.html', cars=cars)

@bp.route('/about')
def about():
    return render_template('about.html') 