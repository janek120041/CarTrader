from app import create_app, db
from app.models import User
from datetime import datetime

def update_timestamps():
    app = create_app()
    with app.app_context():
        # Get all users without timestamps
        users = User.query.filter_by(created_at=None).all()
        
        # Update timestamps
        for user in users:
            user.created_at = datetime.utcnow()
            print(f"Updating timestamp for user: {user.username}")
        
        # Commit changes
        db.session.commit()
        print(f"Updated timestamps for {len(users)} users")

if __name__ == '__main__':
    update_timestamps() 