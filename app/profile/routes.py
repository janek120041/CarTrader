from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.profile import bp
from app.models import Car, TradeRequest, db
from app.profile.forms import EditProfileForm
from werkzeug.utils import secure_filename

@bp.route('/')
@login_required
def profile():
    active_listings = Car.query.filter_by(seller=current_user, sold=False).order_by(Car.created_at.desc()).all()
    sold_cars = Car.query.filter_by(seller=current_user, sold=True).order_by(Car.created_at.desc()).all()
    return render_template('profile/profile.html', title='Profile',
                         active_listings=active_listings,
                         sold_cars=sold_cars)

@bp.route('/my_cars')
@login_required
def my_cars():
    active_listings = Car.query.filter_by(seller=current_user, sold=False).order_by(Car.created_at.desc()).all()
    sold_cars = Car.query.filter_by(seller=current_user, sold=True).order_by(Car.created_at.desc()).all()
    return render_template('profile/my_cars.html', title='My Cars',
                         active_listings=active_listings,
                         sold_cars=sold_cars)

@bp.route('/trade_requests')
@login_required
def trade_requests():
    # Get trade requests where the current user is either the owner or requester
    received_requests = TradeRequest.query.filter_by(owner_id=current_user.id).order_by(TradeRequest.created_at.desc()).all()
    sent_requests = TradeRequest.query.filter_by(requester_id=current_user.id).order_by(TradeRequest.created_at.desc()).all()
    return render_template('profile/trade_requests.html', title='Trade Requests',
                         received_requests=received_requests,
                         sent_requests=sent_requests)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.bio = form.bio.data
        if form.avatar.data:
            # Handle avatar upload
            filename = secure_filename(form.avatar.data.filename)
            form.avatar.data.save('app/static/avatars/' + filename)
            current_user.avatar = filename
        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('profile.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.bio.data = current_user.bio
    return render_template('profile/edit_profile.html', title='Edit Profile',
                         form=form) 