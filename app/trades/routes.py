from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.models import Car, TradeRequest

bp = Blueprint('trades', __name__)

@bp.route('/propose/<int:car_id>', methods=['POST'])
@login_required
def propose_trade(car_id):
    requested_car = Car.query.get_or_404(car_id)
    
    if requested_car.seller == current_user:
        flash('You cannot request to trade your own car.', 'danger')
        return redirect(url_for('cars.view_car', slug=requested_car.slug))
    
    trade_car_id = request.form.get('trade_car_id')
    message = request.form.get('message', '')
    
    if not trade_car_id:
        flash('Please select a car to offer for trade.', 'danger')
        return redirect(url_for('cars.view_car', slug=requested_car.slug))
    
    # Check if a trade request already exists
    existing_request = TradeRequest.query.filter_by(
        requester_id=current_user.id,
        requested_car_id=car_id,
        offered_car_id=trade_car_id,
        status='Pending'
    ).first()
    
    if existing_request:
        flash('You already have a pending trade request for this car.', 'warning')
        return redirect(url_for('cars.view_car', slug=requested_car.slug))
    
    trade_request = TradeRequest(
        requester_id=current_user.id,
        owner_id=requested_car.seller_id,
        offered_car_id=trade_car_id,
        requested_car_id=car_id,
        message=message
    )
    
    db.session.add(trade_request)
    
    # Update car statuses
    requested_car.status = 'Under Negotiation'
    offered_car = Car.query.get(trade_car_id)
    offered_car.status = 'Under Negotiation'
    
    db.session.commit()
    flash('Trade request sent successfully!', 'success')
    return redirect(url_for('cars.view_car', slug=requested_car.slug))

@bp.route('/requests')
@login_required
def trade_requests():
    received_requests = TradeRequest.query.filter_by(
        owner_id=current_user.id
    ).order_by(TradeRequest.created_at.desc()).all()
    
    sent_requests = TradeRequest.query.filter_by(
        requester_id=current_user.id
    ).order_by(TradeRequest.created_at.desc()).all()
    
    return render_template('trades/requests.html',
                         received_requests=received_requests,
                         sent_requests=sent_requests)

@bp.route('/request/<int:request_id>/<string:action>', methods=['POST'])
@login_required
def handle_request(request_id, action):
    trade_request = TradeRequest.query.get_or_404(request_id)
    
    if trade_request.owner_id != current_user.id:
        flash('You can only handle trade requests for your own cars.', 'danger')
        return redirect(url_for('trades.trade_requests'))
    
    if action not in ['accept', 'reject', 'cancel']:
        flash('Invalid action.', 'danger')
        return redirect(url_for('trades.trade_requests'))
    
    if trade_request.status != 'Pending':
        flash('This trade request has already been handled.', 'warning')
        return redirect(url_for('trades.trade_requests'))
    
    if action == 'accept':
        # Get the cars involved
        requested_car = Car.query.get(trade_request.requested_car_id)
        offered_car = Car.query.get(trade_request.offered_car_id)
        
        # Swap ownership
        temp_seller = requested_car.seller
        requested_car.seller = offered_car.seller
        offered_car.seller = temp_seller
        
        # Update statuses
        requested_car.status = 'Available'
        offered_car.status = 'Available'
        trade_request.status = 'Accepted'
        
        # Reject all other pending requests for these cars
        other_requests = TradeRequest.query.filter(
            TradeRequest.id != trade_request.id,
            TradeRequest.status == 'Pending',
            (
                (TradeRequest.offered_car_id == offered_car.id) |
                (TradeRequest.offered_car_id == requested_car.id) |
                (TradeRequest.requested_car_id == offered_car.id) |
                (TradeRequest.requested_car_id == requested_car.id)
            )
        ).all()
        
        for request in other_requests:
            request.status = 'Rejected'
        
        flash('Trade completed successfully!', 'success')
    
    elif action == 'reject':
        trade_request.status = 'Rejected'
        
        # Reset car statuses if no other pending requests
        requested_car = Car.query.get(trade_request.requested_car_id)
        offered_car = Car.query.get(trade_request.offered_car_id)
        
        if not TradeRequest.query.filter(
            TradeRequest.id != trade_request.id,
            TradeRequest.status == 'Pending',
            (
                (TradeRequest.offered_car_id == offered_car.id) |
                (TradeRequest.requested_car_id == offered_car.id)
            )
        ).first():
            offered_car.status = 'Available'
        
        if not TradeRequest.query.filter(
            TradeRequest.id != trade_request.id,
            TradeRequest.status == 'Pending',
            (
                (TradeRequest.offered_car_id == requested_car.id) |
                (TradeRequest.requested_car_id == requested_car.id)
            )
        ).first():
            requested_car.status = 'Available'
        
        flash('Trade request rejected.', 'info')
    
    elif action == 'cancel':
        if trade_request.requester_id != current_user.id:
            flash('You can only cancel your own trade requests.', 'danger')
            return redirect(url_for('trades.trade_requests'))
        
        trade_request.status = 'Cancelled'
        
        # Reset car statuses if no other pending requests
        requested_car = Car.query.get(trade_request.requested_car_id)
        offered_car = Car.query.get(trade_request.offered_car_id)
        
        if not TradeRequest.query.filter(
            TradeRequest.id != trade_request.id,
            TradeRequest.status == 'Pending',
            (
                (TradeRequest.offered_car_id == offered_car.id) |
                (TradeRequest.requested_car_id == offered_car.id)
            )
        ).first():
            offered_car.status = 'Available'
        
        if not TradeRequest.query.filter(
            TradeRequest.id != trade_request.id,
            TradeRequest.status == 'Pending',
            (
                (TradeRequest.offered_car_id == requested_car.id) |
                (TradeRequest.requested_car_id == requested_car.id)
            )
        ).first():
            requested_car.status = 'Available'
        
        flash('Trade request cancelled.', 'info')
    
    db.session.commit()
    return redirect(url_for('trades.trade_requests')) 