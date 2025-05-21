from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models import User
from flask_login import current_user

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=2, max=64)
    ])
    bio = TextAreaField('About Me', validators=[
        Length(max=500)
    ])
    avatar = FileField('Profile Picture')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.') 