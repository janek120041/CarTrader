from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, IntegerField, FloatField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, ValidationError
from app.models import Category
from datetime import datetime

class CarListingForm(FlaskForm):
    title = StringField('Listing Title', validators=[DataRequired(), Length(min=10, max=100)])
    make = StringField('Make', validators=[DataRequired(), Length(max=50)])
    model = StringField('Model', validators=[DataRequired(), Length(max=50)])
    year = IntegerField('Year', validators=[
        DataRequired(),
        NumberRange(min=1900, max=datetime.now().year + 1)
    ])
    price = FloatField('Price ($)', validators=[
        DataRequired(),
        NumberRange(min=0)
    ])
    mileage = IntegerField('Mileage', validators=[
        DataRequired(),
        NumberRange(min=0)
    ])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=30, max=2000)])
    image = FileField('Car Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Save Changes')

    def __init__(self, *args, **kwargs):
        super(CarListingForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(c.id, c.name) for c in Category.query.order_by('name')]

    def validate_category_id(self, field):
        category = Category.query.get(field.data)
        if not category:
            raise ValidationError('Please select a valid category.') 