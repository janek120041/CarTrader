import os
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.cars import bp
from app.cars.forms import CarListingForm
from app.models import Car, Category

def save_car_image(form_image):
    if form_image:
        # Ensure the upload directory exists
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Generate a unique filename
        filename = secure_filename(form_image.filename)
        unique_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
        
        # Save the file
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        form_image.save(file_path)
        
        return unique_filename
    return None

@bp.route('/list', methods=['GET', 'POST'])
@login_required
def list_car():
    form = CarListingForm()
    if request.method == 'POST':
        print("Form submitted with data:", request.form)
        print("Form validation errors:", form.errors)
        
    if form.validate_on_submit():
        try:
            image_filename = save_car_image(form.image.data)
            car = Car(
                title=form.title.data,
                make=form.make.data,
                model=form.model.data,
                year=form.year.data,
                price=form.price.data,
                mileage=form.mileage.data,
                category_id=form.category_id.data,
                description=form.description.data,
                image_filename=image_filename,
                seller=current_user
            )
            db.session.add(car)
            db.session.commit()
            flash('Your car has been listed!', 'success')
            return redirect(url_for('cars.view_car', slug=car.slug))
        except Exception as e:
            print("Error saving car:", str(e))
            db.session.rollback()
            flash('An error occurred while listing your car. Please try again.', 'danger')
            return redirect(url_for('cars.list_car'))
    
    # Ensure categories are loaded for the form
    categories = Category.query.order_by(Category.name).all()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    
    return render_template('cars/list_car.html', title='List Your Car', form=form)

@bp.route('/<slug>')
def view_car(slug):
    car = Car.query.filter_by(slug=slug).first_or_404()
    return render_template('cars/view_car.html', title=car.title, car=car)

@bp.route('/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_car(slug):
    car = Car.query.filter_by(slug=slug).first_or_404()
    if car.seller != current_user:
        flash('You can only edit your own listings.', 'danger')
        return redirect(url_for('cars.view_car', slug=slug))
    
    form = CarListingForm()
    
    # Load categories for the form
    categories = Category.query.order_by(Category.name).all()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        car.title = form.title.data
        car.make = form.make.data
        car.model = form.model.data
        car.year = form.year.data
        car.price = form.price.data
        car.mileage = form.mileage.data
        car.category_id = form.category_id.data
        car.description = form.description.data
        
        if form.image.data:
            # Delete old image if it exists
            if car.image_filename:
                old_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], car.image_filename)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            # Save new image
            car.image_filename = save_car_image(form.image.data)
        
        db.session.commit()
        flash('Your listing has been updated!', 'success')
        return redirect(url_for('cars.view_car', slug=car.slug))
    elif request.method == 'GET':
        form.title.data = car.title
        form.make.data = car.make
        form.model.data = car.model
        form.year.data = car.year
        form.price.data = car.price
        form.mileage.data = car.mileage
        form.category_id.data = car.category_id
        form.description.data = car.description
    
    return render_template('cars/edit_car.html', title='Edit Listing', form=form, car=car)

@bp.route('/<slug>/delete', methods=['POST'])
@login_required
def delete_car(slug):
    car = Car.query.filter_by(slug=slug).first_or_404()
    if car.seller != current_user:
        flash('You can only delete your own listings.', 'danger')
        return redirect(url_for('cars.view_car', slug=slug))
    
    # Delete the car image if it exists
    if car.image_filename:
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], car.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(car)
    db.session.commit()
    flash('Your listing has been deleted.', 'success')
    return redirect(url_for('main.index')) 