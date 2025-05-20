from app import create_app, db
from app.models import Category

app = create_app()

def seed_categories():
    categories = [
        'Sedan',
        'SUV',
        'Truck',
        'Coupe',
        'Van',
        'Wagon',
        'Convertible',
        'Sports Car',
        'Luxury',
        'Electric',
        'Hybrid',
        'Classic',
        'Motorcycle'
    ]
    
    with app.app_context():
        for category_name in categories:
            # Check if category already exists
            if not Category.query.filter_by(name=category_name).first():
                category = Category(name=category_name)
                db.session.add(category)
                print(f"Added category: {category_name}")
        
        db.session.commit()
        print("Categories seeded successfully!")

if __name__ == '__main__':
    seed_categories() 