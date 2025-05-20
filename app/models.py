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