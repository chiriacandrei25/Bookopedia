from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from flask_login import current_user


def validate_name(form, shelf_name):
    if next((shelf for shelf in current_user.shelves if shelf.name == shelf_name.data), None) is not None:
        raise ValidationError('You already have that shelf.')


class ShelfForm(FlaskForm):
    shelf_name = StringField('Shelf', validators=[DataRequired(), validate_name])
    submit = SubmitField('Create')
