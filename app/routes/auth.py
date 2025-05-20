from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Car, TradeRequest, Inquiry
from app import db
from werkzeug.security import generate_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from sqlalchemy import or_, and_

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = form.remember.data

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        flash('Please check your login details and try again.', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists', 'danger')
            return redirect(url_for('auth.register'))

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register'))

        new_user = User(email=email, username=username)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/profile')
@login_required
def profile():
    # Get active listings (cars that belong to the current user)
    active_listings = Car.query.filter_by(owner_id=current_user.id).all()
    
    # Get sold cars (implementation depends on your business logic)
    # For now, we'll assume a car is sold if it has a completed trade request
    # We need to check both offered and requested cars
    sold_cars = Car.query.join(
        TradeRequest,
        or_(
            and_(Car.id == TradeRequest.offered_car_id, TradeRequest.status == 'Accepted'),
            and_(Car.id == TradeRequest.requested_car_id, TradeRequest.status == 'Accepted')
        )
    ).filter(Car.owner_id == current_user.id).all()
    
    # Get inquiries received for user's cars
    inquiries = Inquiry.query.join(Car).filter(
        Car.owner_id == current_user.id
    ).order_by(Inquiry.created_at.desc()).all()
    
    # Get trade requests (both sent and received)
    trade_requests = TradeRequest.query.filter(
        (TradeRequest.owner_id == current_user.id) | 
        (TradeRequest.requester_id == current_user.id)
    ).order_by(TradeRequest.created_at.desc()).all()
    
    # Get user's favorite cars (if you have this feature)
    favorites = []  # Implement if you have a favorites feature
    
    return render_template('auth/profile.html',
                         active_listings=active_listings,
                         sold_cars=sold_cars,
                         inquiries=inquiries,
                         trade_requests=trade_requests,
                         favorites=favorites)

@auth.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        if username != current_user.username:
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'danger')
                return redirect(url_for('auth.edit_profile'))
            current_user.username = username

        if email != current_user.email:
            if User.query.filter_by(email=email).first():
                flash('Email already exists', 'danger')
                return redirect(url_for('auth.edit_profile'))
            current_user.email = email

        if current_password and new_password:
            if not current_user.check_password(current_password):
                flash('Current password is incorrect', 'danger')
                return redirect(url_for('auth.edit_profile'))
            current_user.set_password(new_password)

        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/edit_profile.html')

@auth.route('/profile/avatar', methods=['POST'])
@login_required
def update_avatar():
    if 'avatar' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('auth.profile'))
    
    file = request.files['avatar']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('auth.profile'))
    
    if file and allowed_file(file.filename):
        # Delete old avatar if it exists
        if current_user.avatar:
            old_avatar_path = os.path.join(current_app.root_path, 'static', current_user.avatar)
            try:
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)
            except Exception as e:
                print(f"Error deleting old avatar: {e}")
        
        # Save new avatar
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        filename = f"avatars/{name}_{int(datetime.utcnow().timestamp())}{ext}"
        
        # Ensure avatars directory exists
        avatar_dir = os.path.join(current_app.root_path, 'static', 'avatars')
        os.makedirs(avatar_dir, exist_ok=True)
        
        file_path = os.path.join(current_app.root_path, 'static', filename)
        file.save(file_path)
        
        current_user.avatar = filename
        db.session.commit()
        
        flash('Profile picture updated successfully', 'success')
    else:
        flash('Invalid file type. Please use PNG, JPG, or JPEG', 'danger')
    
    return redirect(url_for('auth.profile'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'} 