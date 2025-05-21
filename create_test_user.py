from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Check if test user already exists
    test_user = User.query.filter_by(email='test@example.com').first()
    if not test_user:
        # Create test user
        test_user = User(
            username='testuser',
            email='test@example.com'
        )
        test_user.set_password('password123')
        db.session.add(test_user)
        db.session.commit()
        print("Test user created successfully!")
    else:
        print("Test user already exists!") 