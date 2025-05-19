from flask import Blueprint, render_template, redirect, url_for
from flask_login import LoginManager

bp = Blueprint('auth', __name__)

@bp.route('/login')
def login():
    return render_template('login.html')

@bp.route('/logout')
def logout():
    return redirect(url_for('main.home'))

@bp.route('/register')
def register():
    return render_template('register.html') 