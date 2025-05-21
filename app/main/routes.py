from flask import render_template, request
from app.main import bp
from app.models import Car

@bp.route('/')
@bp.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    cars = Car.query.filter_by(sold=False).order_by(Car.created_at.desc()).paginate(
        page=page, per_page=6, error_out=False)
    return render_template('main/index.html', title='Home', cars=cars) 