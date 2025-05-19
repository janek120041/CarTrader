from flask import Blueprint, render_template, request
from app.models import Car, Category
from sqlalchemy import desc

main = Blueprint('main', __name__)

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    categories = Category.query.all()
    category_id = request.args.get('category', type=int)
    search_query = request.args.get('search', '')

    query = Car.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    if search_query:
        search = f"%{search_query}%"
        query = query.filter(
            (Car.title.ilike(search)) |
            (Car.make.ilike(search)) |
            (Car.model.ilike(search)) |
            (Car.description.ilike(search))
        )

    cars = query.order_by(desc(Car.created_at)).paginate(page=page, per_page=12)
    return render_template('index.html', cars=cars, categories=categories,
                         current_category=category_id, search_query=search_query) 