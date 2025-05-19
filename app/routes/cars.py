from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app.models import Car, Category, Comment, Inquiry, TradeRequest
from app import db
import os
from werkzeug.utils import secure_filename
from datetime import datetime

cars = Blueprint('cars', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def save_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to filename to prevent duplicates
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{int(datetime.utcnow().timestamp())}{ext}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return f'car_images/{filename}'
    return None

@cars.route('/car/<int:car_id>')
def view_car(car_id):
    car = Car.query.get_or_404(car_id)
    comments = Comment.query.filter_by(car_id=car_id).order_by(Comment.created_at.desc()).all()
    return render_template('cars/view.html', car=car, comments=comments)

@cars.route('/car/new', methods=['GET', 'POST'])
@login_required
def new_car():
    categories = Category.query.all()
    if request.method == 'POST':
        title = request.form.get('title')
        make = request.form.get('make')
        model = request.form.get('model')
        year = request.form.get('year')
        mileage = request.form.get('mileage')
        price = request.form.get('price')
        description = request.form.get('description')
        category_id = request.form.get('category_id')

        car = Car(
            title=title,
            make=make,
            model=model,
            year=year,
            mileage=mileage,
            price=price,
            description=description,
            category_id=category_id,
            owner_id=current_user.id
        )

        if 'image' in request.files:
            image_url = save_image(request.files['image'])
            if image_url:
                car.image_url = image_url

        db.session.add(car)
        db.session.commit()
        flash('Your car has been listed!', 'success')
        return redirect(url_for('cars.view_car', car_id=car.id))

    return render_template('cars/new.html', categories=categories)

@cars.route('/car/<int:car_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_car(car_id):
    car = Car.query.get_or_404(car_id)
    if car.owner_id != current_user.id:
        flash('You can only edit your own listings.', 'danger')
        return redirect(url_for('cars.view_car', car_id=car_id))

    categories = Category.query.all()
    if request.method == 'POST':
        car.title = request.form.get('title')
        car.make = request.form.get('make')
        car.model = request.form.get('model')
        car.year = request.form.get('year')
        car.mileage = request.form.get('mileage')
        car.price = request.form.get('price')
        car.description = request.form.get('description')
        car.category_id = request.form.get('category_id')

        if 'image' in request.files:
            image_url = save_image(request.files['image'])
            if image_url:
                # Delete old image if it exists
                if car.image_url:
                    old_image_path = os.path.join(current_app.root_path, 'static', car.image_url)
                    try:
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                    except Exception as e:
                        print(f"Error deleting old image: {e}")
                car.image_url = image_url

        db.session.commit()
        flash('Your car listing has been updated!', 'success')
        return redirect(url_for('cars.view_car', car_id=car.id))

    return render_template('cars/edit.html', car=car, categories=categories)

@cars.route('/car/<int:car_id>/delete')
@login_required
def delete_car(car_id):
    car = Car.query.get_or_404(car_id)
    if car.owner_id != current_user.id:
        flash('You can only delete your own listings.', 'danger')
        return redirect(url_for('cars.view_car', car_id=car_id))

    # Delete the car image if it exists
    if car.image_url:
        image_path = os.path.join(current_app.root_path, 'static', car.image_url)
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            print(f"Error deleting image: {e}")

    db.session.delete(car)
    db.session.commit()
    flash('Your car listing has been deleted.', 'success')
    return redirect(url_for('main.index'))

@cars.route('/car/<int:car_id>/comment', methods=['POST'])
@login_required
def add_comment(car_id):
    car = Car.query.get_or_404(car_id)
    if car.owner_id == current_user.id:
        flash('You cannot comment on your own listing.', 'danger')
        return redirect(url_for('cars.view_car', car_id=car_id))

    rating = request.form.get('rating', type=int)
    comment_text = request.form.get('comment')

    if not rating or not comment_text:
        flash('Both rating and comment are required.', 'danger')
        return redirect(url_for('cars.view_car', car_id=car_id))

    comment = Comment(
        user_id=current_user.id,
        car_id=car_id,
        rating=rating,
        comment=comment_text
    )
    db.session.add(comment)
    db.session.commit()
    flash('Your comment has been added!', 'success')
    return redirect(url_for('cars.view_car', car_id=car_id))

@cars.route('/car/<int:car_id>/inquire', methods=['POST'])
@login_required
def send_inquiry(car_id):
    car = Car.query.get_or_404(car_id)
    if car.owner_id == current_user.id:
        flash('You cannot inquire about your own listing.', 'danger')
        return redirect(url_for('cars.view_car', car_id=car_id))

    message = request.form.get('message')
    if not message:
        flash('Message is required.', 'danger')
        return redirect(url_for('cars.view_car', car_id=car_id))

    inquiry = Inquiry(
        sender_id=current_user.id,
        car_id=car_id,
        message=message
    )
    db.session.add(inquiry)
    db.session.commit()
    flash('Your inquiry has been sent!', 'success')
    return redirect(url_for('cars.view_car', car_id=car_id))

@cars.route('/inquiries')
@login_required
def view_inquiries():
    # Get inquiries for cars owned by the current user
    received_inquiries = Inquiry.query.join(Car).filter(Car.owner_id == current_user.id).all()
    # Get inquiries sent by the current user
    sent_inquiries = Inquiry.query.filter_by(sender_id=current_user.id).all()
    return render_template('cars/inquiries.html', 
                         received_inquiries=received_inquiries,
                         sent_inquiries=sent_inquiries)

@cars.route('/inquiry/<int:inquiry_id>/respond', methods=['POST'])
@login_required
def respond_to_inquiry(inquiry_id):
    inquiry = Inquiry.query.get_or_404(inquiry_id)
    car = Car.query.get(inquiry.car_id)
    
    if car.owner_id != current_user.id:
        flash('You can only respond to inquiries for your own listings.', 'danger')
        return redirect(url_for('cars.view_inquiries'))

    response = request.form.get('response')
    if not response:
        flash('Response is required.', 'danger')
        return redirect(url_for('cars.view_inquiries'))

    inquiry.response = response
    inquiry.response_date = datetime.utcnow()
    inquiry.status = 'Responded'
    db.session.commit()
    flash('Your response has been sent!', 'success')
    return redirect(url_for('cars.view_inquiries'))

@cars.route('/car/<int:car_id>/request-trade', methods=['GET', 'POST'])
@login_required
def request_trade(car_id):
    requested_car = Car.query.get_or_404(car_id)
    
    if requested_car.owner_id == current_user.id:
        flash('You cannot request to trade your own car.', 'danger')
        return redirect(url_for('cars.view_car', car_id=car_id))
    
    user_cars = Car.query.filter_by(owner_id=current_user.id).all()
    
    if request.method == 'POST':
        offered_car_id = request.form.get('offered_car_id')
        message = request.form.get('message')
        
        if not offered_car_id:
            flash('Please select a car to offer for trade.', 'danger')
            return redirect(url_for('cars.request_trade', car_id=car_id))
        
        # Check if a trade request already exists
        existing_request = TradeRequest.query.filter_by(
            requester_id=current_user.id,
            requested_car_id=car_id,
            offered_car_id=offered_car_id,
            status='Pending'
        ).first()
        
        if existing_request:
            flash('You already have a pending trade request for this car.', 'warning')
            return redirect(url_for('cars.view_car', car_id=car_id))
        
        trade_request = TradeRequest(
            requester_id=current_user.id,
            owner_id=requested_car.owner_id,
            offered_car_id=offered_car_id,
            requested_car_id=car_id,
            message=message
        )
        
        db.session.add(trade_request)
        db.session.commit()
        flash('Trade request sent successfully!', 'success')
        return redirect(url_for('cars.view_car', car_id=car_id))
    
    return render_template('cars/request_trade.html', 
                         requested_car=requested_car, 
                         user_cars=user_cars)

@cars.route('/trade-requests')
@login_required
def trade_requests():
    received_requests = TradeRequest.query.filter_by(owner_id=current_user.id).order_by(TradeRequest.created_at.desc()).all()
    sent_requests = TradeRequest.query.filter_by(requester_id=current_user.id).order_by(TradeRequest.created_at.desc()).all()
    return render_template('cars/trade_requests.html',
                         received_requests=received_requests,
                         sent_requests=sent_requests)

@cars.route('/trade-request/<int:request_id>/<string:action>', methods=['POST'])
@login_required
def handle_trade_request(request_id, action):
    trade_request = TradeRequest.query.get_or_404(request_id)
    
    if trade_request.owner_id != current_user.id:
        flash('You can only handle trade requests for your own cars.', 'danger')
        return redirect(url_for('cars.trade_requests'))
    
    if action not in ['accept', 'reject']:
        flash('Invalid action.', 'danger')
        return redirect(url_for('cars.trade_requests'))
    
    if trade_request.status != 'Pending':
        flash('This trade request has already been handled.', 'warning')
        return redirect(url_for('cars.trade_requests'))
    
    if action == 'accept':
        # Swap car ownership
        requested_car = Car.query.get(trade_request.requested_car_id)
        offered_car = Car.query.get(trade_request.offered_car_id)
        
        temp_owner = requested_car.owner_id
        requested_car.owner_id = offered_car.owner_id
        offered_car.owner_id = temp_owner
        
        trade_request.status = 'Accepted'
        flash('Trade request accepted! Car ownership has been transferred.', 'success')
    else:
        trade_request.status = 'Rejected'
        flash('Trade request rejected.', 'info')
    
    db.session.commit()
    return redirect(url_for('cars.trade_requests')) 