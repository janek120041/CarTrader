from flask import Blueprint, render_template, redirect, url_for

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return render_template('home.html')

@bp.route('/cars')
def car_list():
    return render_template('car_list.html')

@bp.route('/cars/<int:car_id>')
def car_detail(car_id):
    return render_template('car_detail.html', car_id=car_id)

@bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@bp.route('/trade-requests')
def trade_requests():
    return render_template('trade_requests.html') 