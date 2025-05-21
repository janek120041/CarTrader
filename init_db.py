import os
from app import create_app, db
from app.models import Category
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    app = create_app()
    
    try:
        # Get database path from config
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        logger.info(f"Database URI: {db_uri}")
        
        # Extract the database file path from the URI
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri[10:]  # Remove 'sqlite:///'
            
            # If it's a relative path, make it absolute
            if not os.path.isabs(db_path):
                db_path = os.path.join(app.instance_path, db_path)
                
            # Ensure the directory exists
            db_dir = os.path.dirname(db_path)
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"Database directory confirmed: {db_dir}")
            
            # Remove existing database if it exists
            if os.path.exists(db_path):
                os.remove(db_path)
                logger.info(f"Removed existing database: {db_path}")
        
        with app.app_context():
            logger.info("Creating database tables...")
            db.create_all()
            
            # Add categories if they don't exist
            categories = [
                'Sedan', 'SUV', 'Truck', 'Sports Car', 'Luxury',
                'Electric', 'Hybrid', 'Van', 'Convertible', 'Wagon'
            ]
            
            for category_name in categories:
                category = Category(name=category_name)
                db.session.add(category)
                logger.info(f"Added category: {category_name}")
            
            db.session.commit()
            logger.info("Database initialized successfully with categories!")
            
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

if __name__ == '__main__':
    init_db() 