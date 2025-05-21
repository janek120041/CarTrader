from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    avatar = db.Column(db.String(200))
    bio = db.Column(db.Text)
    cars = db.relationship('Car', backref='owner', lazy=True)
    sent_trade_requests = db.relationship('TradeRequest', foreign_keys='TradeRequest.requester_id', backref='requester', lazy=True)
    received_trade_requests = db.relationship('TradeRequest', foreign_keys='TradeRequest.owner_id', backref='owner', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    reviews_received = db.relationship('UserReview', foreign_keys='UserReview.reviewed_user_id', backref='reviewed_user', lazy=True)
    reviews_given = db.relationship('UserReview', foreign_keys='UserReview.reviewer_id', backref='reviewer', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def unread_notifications_count(self):
        """Get the count of unread notifications"""
        return Notification.query.filter_by(user_id=self.id, is_read=False).count()

    @property
    def average_rating(self):
        """Calculate the user's average rating"""
        reviews = UserReview.query.filter_by(reviewed_user_id=self.id).all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / len(reviews)

    @property
    def total_reviews(self):
        """Get the total number of reviews received"""
        return UserReview.query.filter_by(reviewed_user_id=self.id).count()

    @property
    def rating_distribution(self):
        """Get the distribution of ratings (1-5 stars)"""
        reviews = UserReview.query.filter_by(reviewed_user_id=self.id).all()
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            distribution[review.rating] += 1
        return distribution

    def can_review_user(self, user_id):
        """Check if the user can review another user based on completed trades"""
        # Check if they have completed trades together
        completed_trades = TradeHistory.query.filter(
            ((TradeHistory.requester_id == self.id) & (TradeHistory.owner_id == user_id)) |
            ((TradeHistory.requester_id == user_id) & (TradeHistory.owner_id == self.id))
        ).first()
        
        if not completed_trades:
            return False
            
        # Check if they haven't already reviewed for this trade
        existing_review = UserReview.query.filter_by(
            reviewer_id=self.id,
            reviewed_user_id=user_id
        ).first()
        
        return not existing_review

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    cars = db.relationship('Car', backref='category', lazy=True)

class Car(db.Model):
    __tablename__ = 'cars'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    mileage = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Available')  # Available, Under Negotiation, Sold
    sent_trade_requests = db.relationship('TradeRequest', foreign_keys='TradeRequest.offered_car_id', backref='offered_car', lazy=True)
    received_trade_requests = db.relationship('TradeRequest', foreign_keys='TradeRequest.requested_car_id', backref='requested_car', lazy=True)

    def mark_as_sold(self):
        """Mark the car as sold"""
        self.status = 'Sold'
        db.session.commit()

    def mark_as_under_negotiation(self):
        """Mark the car as under negotiation"""
        if self.status != 'Sold':
            self.status = 'Under Negotiation'
            db.session.commit()

    def mark_as_available(self):
        """Mark the car as available"""
        if self.status != 'Sold':
            self.status = 'Available'
            db.session.commit()

    @property
    def is_available(self):
        """Check if the car is available for trade"""
        return self.status == 'Available'

    @property
    def is_sold(self):
        """Check if the car is sold"""
        return self.status == 'Sold'

    @property
    def is_under_negotiation(self):
        """Check if the car is under negotiation"""
        return self.status == 'Under Negotiation'

class TradeRequest(db.Model):
    __tablename__ = 'trade_requests'
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    offered_car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    requested_car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, Accepted, Rejected
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def accept_trade(self):
        """Accept the trade request and update car statuses"""
        if self.status == 'Pending':
            self.status = 'Accepted'
            # Mark both cars as sold
            offered_car = Car.query.get(self.offered_car_id)
            requested_car = Car.query.get(self.requested_car_id)
            offered_car.mark_as_sold()
            requested_car.mark_as_sold()
            # Create trade history entry
            trade_history = TradeHistory(
                trade_request_id=self.id,
                offered_car_id=self.offered_car_id,
                requested_car_id=self.requested_car_id,
                offered_car_details=f"{offered_car.year} {offered_car.make} {offered_car.model}",
                requested_car_details=f"{requested_car.year} {requested_car.make} {requested_car.model}",
                requester_id=self.requester_id,
                owner_id=self.owner_id
            )
            db.session.add(trade_history)
            # Create notifications for both users
            Notification.create_trade_status_notification(self.requester_id, self, 'Accepted')
            Notification.create_trade_status_notification(self.owner_id, self, 'Accepted')
            # Update other pending requests for these cars to Rejected
            self._reject_other_requests()
            db.session.commit()

    def reject_trade(self):
        """Reject the trade request and update car statuses"""
        if self.status == 'Pending':
            self.status = 'Rejected'
            # Mark both cars as available if they have no other pending requests
            offered_car = Car.query.get(self.offered_car_id)
            requested_car = Car.query.get(self.requested_car_id)
            if not self._has_other_pending_requests(offered_car.id):
                offered_car.mark_as_available()
            if not self._has_other_pending_requests(requested_car.id):
                requested_car.mark_as_available()
            db.session.commit()

    def _reject_other_requests(self):
        """Reject all other pending requests for both cars"""
        other_requests = TradeRequest.query.filter(
            TradeRequest.id != self.id,
            TradeRequest.status == 'Pending',
            db.or_(
                TradeRequest.offered_car_id.in_([self.offered_car_id, self.requested_car_id]),
                TradeRequest.requested_car_id.in_([self.offered_car_id, self.requested_car_id])
            )
        ).all()
        for request in other_requests:
            request.status = 'Rejected'

    def _has_other_pending_requests(self, car_id):
        """Check if a car has other pending trade requests"""
        return TradeRequest.query.filter(
            TradeRequest.id != self.id,
            TradeRequest.status == 'Pending',
            db.or_(
                TradeRequest.offered_car_id == car_id,
                TradeRequest.requested_car_id == car_id
            )
        ).count() > 0

class TradeHistory(db.Model):
    """Model to track completed car trades"""
    __tablename__ = 'trade_history'
    id = db.Column(db.Integer, primary_key=True)
    trade_request_id = db.Column(db.Integer, db.ForeignKey('trade_requests.id'), nullable=False)
    offered_car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    requested_car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    offered_car_details = db.Column(db.String(200), nullable=False)  # Stored for historical record
    requested_car_details = db.Column(db.String(200), nullable=False)  # Stored for historical record
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    trade_request = db.relationship('TradeRequest', backref='trade_history', lazy=True)
    offered_car = db.relationship('Car', foreign_keys=[offered_car_id], backref='offered_trades_history', lazy=True)
    requested_car = db.relationship('Car', foreign_keys=[requested_car_id], backref='requested_trades_history', lazy=True)
    requester = db.relationship('User', foreign_keys=[requester_id], backref='trades_made_history', lazy=True)
    owner = db.relationship('User', foreign_keys=[owner_id], backref='trades_received_history', lazy=True)

    @property
    def trade_description(self):
        """Return a human-readable description of the trade"""
        return f"Trade of {self.offered_car_details} for {self.requested_car_details} completed on {self.completed_at.strftime('%Y-%m-%d')}"

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add the relationship to the User model
    user = db.relationship('User', backref=db.backref('comments', lazy=True))

class Inquiry(db.Model):
    __tablename__ = 'inquiries'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    response = db.Column(db.Text)
    response_date = db.Column(db.DateTime)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.car_id:
            car = Car.query.get(self.car_id)
            if car and car.owner_id:
                Notification.create_inquiry_notification(car.owner_id, self)

class Notification(db.Model):
    """Model for user notifications"""
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # trade_request, inquiry, status_update, etc.
    related_id = db.Column(db.Integer)  # ID of related object (trade request, inquiry, etc.)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def create_trade_request_notification(cls, user_id, trade_request):
        """Create a notification for a new trade request"""
        offered_car = Car.query.get(trade_request.offered_car_id)
        requested_car = Car.query.get(trade_request.requested_car_id)
        notification = cls(
            user_id=user_id,
            title="New Trade Request",
            message=f"New trade request: {offered_car.year} {offered_car.make} {offered_car.model} "
                   f"for your {requested_car.year} {requested_car.make} {requested_car.model}",
            notification_type="trade_request",
            related_id=trade_request.id
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @classmethod
    def create_trade_status_notification(cls, user_id, trade_request, status):
        """Create a notification for a trade request status update"""
        offered_car = Car.query.get(trade_request.offered_car_id)
        requested_car = Car.query.get(trade_request.requested_car_id)
        title = f"Trade Request {status.capitalize()}"
        message = f"Trade request for {offered_car.year} {offered_car.make} {offered_car.model} "
        message += f"has been {status.lower()}"
        
        notification = cls(
            user_id=user_id,
            title=title,
            message=message,
            notification_type="trade_status",
            related_id=trade_request.id
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @classmethod
    def create_inquiry_notification(cls, user_id, inquiry):
        """Create a notification for a new inquiry"""
        car = Car.query.get(inquiry.car_id)
        notification = cls(
            user_id=user_id,
            title="New Inquiry",
            message=f"New inquiry received for your {car.year} {car.make} {car.model}",
            notification_type="inquiry",
            related_id=inquiry.id
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    def mark_as_read(self):
        """Mark the notification as read"""
        self.is_read = True
        db.session.commit()

class UserReview(db.Model):
    """Model for user reviews and ratings"""
    __tablename__ = 'user_reviews'
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewed_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review_text = db.Column(db.Text)
    trade_id = db.Column(db.Integer, db.ForeignKey('trade_history.id'))  # Optional link to specific trade
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Validation
    __table_args__ = (
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        db.UniqueConstraint('reviewer_id', 'reviewed_user_id', 'trade_id', 
                          name='unique_review_per_trade')
    )

    @validates('rating')
    def validate_rating(self, key, rating):
        """Validate rating is between 1 and 5"""
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return rating

    @validates('reviewer_id')
    def validate_reviewer(self, key, reviewer_id):
        """Ensure reviewer is not reviewing themselves"""
        if reviewer_id == self.reviewed_user_id:
            raise ValueError("Users cannot review themselves")
        return reviewer_id

    def notify_reviewed_user(self):
        """Create a notification for the reviewed user"""
        reviewer = User.query.get(self.reviewer_id)
        notification = Notification(
            user_id=self.reviewed_user_id,
            title="New Review Received",
            message=f"{reviewer.username} has left you a {self.rating}-star review",
            notification_type="review",
            related_id=self.id
        )
        db.session.add(notification)
        db.session.commit() 