from app import create_app, db
from app.models import User
from datetime import datetime

app = create_app()

with app.app_context():
    users = User.query.all()
    updates_made = False
    
    for user in users:
        if user.created_at is None:
            user.created_at = datetime.utcnow()
            updates_made = True
            print(f"Updated created_at for user: {user.username}")
    
    if updates_made:
        db.session.commit()
        print("All updates committed successfully!")
    else:
        print("No updates needed - all users have timestamps.") 