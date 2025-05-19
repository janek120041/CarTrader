from app import db, create_app
from app.models import Category

def init_categories():
    categories = [
        "Sedan",
        "SUV",
        "Truck",
        "Coupe",
        "Van",
        "Wagon",
        "Convertible",
        "Hatchback",
        "Luxury",
        "Sports Car",
        "Electric",
        "Hybrid",
        "Classic/Vintage",
        "Minivan",
        "Crossover",
        "Pickup"
    ]
    
    # Check if categories already exist
    existing_categories = Category.query.all()
    if existing_categories:
        print("Categories already initialized")
        return
    
    # Add categories
    for category_name in categories:
        category = Category(name=category_name)
        db.session.add(category)
    
    try:
        db.session.commit()
        print("Categories initialized successfully")
    except Exception as e:
        db.session.rollback()
        print(f"Error initializing categories: {e}")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        init_categories() 